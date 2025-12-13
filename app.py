import asyncio
import threading
import base64
import functools
from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from hume import HumeStreamClient
from hume.models.config import ProsodyConfig
from phue import Bridge

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# --- GLOBAL SESSION STATE ---
session_data = {
    "bridge": None,
    "hume_key": None,
    "light_name": None
}

audio_queue = asyncio.Queue()

# --- COLOR MAPPING ---
COLOR_MAP = {
    "Joy":        {"hue": 10000, "sat": 254, "bri": 254}, # Yellow
    "Excitement": {"hue": 5000,  "sat": 254, "bri": 254}, # Orange
    "Anger":      {"hue": 0,     "sat": 254, "bri": 254}, # Red
    "Sadness":    {"hue": 46920, "sat": 200, "bri": 100}, # Blue
    "Calmness":   {"hue": 35000, "sat": 150, "bri": 150}, # Teal
    "Fear":       {"hue": 50000, "sat": 254, "bri": 200}, # Violet
    "Neutral":    {"hue": 8000,  "sat": 50,  "bri": 150}, # White
}

def map_emotion_to_light(emotion_name):
    if emotion_name in COLOR_MAP: return COLOR_MAP[emotion_name]
    if emotion_name in ["Adoration", "Amusement", "Ecstasy"]: return COLOR_MAP["Joy"]
    if emotion_name in ["Annoyance", "Disgust", "Contempt"]: return COLOR_MAP["Anger"]
    if emotion_name in ["Anxiety", "Horror", "Distress"]: return COLOR_MAP["Fear"]
    return COLOR_MAP["Neutral"]

# --- HUME ASYNC LOOP ---
async def hume_loop():
    while True:
        # Wait until user provides a key via the UI
        if session_data["hume_key"] is None:
            await asyncio.sleep(1)
            continue

        try:
            client = HumeStreamClient(session_data["hume_key"])
            config = ProsodyConfig()
            
            async with client.connect([config]) as socket:
                print("✅ Hume Stream Connected")
                while session_data["hume_key"]: # Stay connected while key exists
                    # Get audio from queue
                    if audio_queue.empty():
                        await asyncio.sleep(0.01)
                        continue
                        
                    audio_data = await audio_queue.get()
                    # FIX: Hume expects base64 encoded bytes
                    encoded_data = base64.b64encode(audio_data)
                    result = await socket.send_bytes(encoded_data)
                    
                    if result and "prosody" in result and "predictions" in result["prosody"]:
                        preds = result["prosody"]["predictions"]
                        if preds:
                            top = max(preds[0]["emotions"], key=lambda x: x["score"])
                            name = top["name"]
                            score = top["score"]

                            if score > 0.45:
                                print(f"Detected: {name} ({score:.2f})")
                                socketio.emit('emotion_update', {'emotion': name, 'score': score})
                                
                                if session_data["bridge"] and session_data["light_name"]:
                                    try:
                                        state = map_emotion_to_light(name)
                                        # FIX: Run blocking Hue call in a separate thread so we don't block the AsyncIO loop
                                        loop = asyncio.get_running_loop()
                                        func = functools.partial(session_data["bridge"].set_light, session_data["light_name"], state, transitiontime=5)
                                        await loop.run_in_executor(None, func)
                                    except Exception as e:
                                        print(f"Light Error: {e}")

        except Exception as e:
            print(f"Hume Reconnect Error: {e}")
            await asyncio.sleep(2)

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(hume_loop())

new_loop = asyncio.new_event_loop()
t = threading.Thread(target=start_background_loop, args=(new_loop,))
t.daemon = True
t.start()

# --- ROUTES ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/setup', methods=['POST'])
def setup():
    data = request.json
    ip = data.get('hue_ip')
    key = data.get('hume_key')
    light = data.get('light_name')

    print(f"Attempting connection to Bridge at {ip}...")

    # 1. Try Connecting to Hue
    try:
        b = Bridge(ip)
        b.connect() # Throws error if button not pressed
        session_data["bridge"] = b
        print("✅ Bridge Connected!")
    except Exception as e:
        return jsonify({"success": False, "message": "Bridge Connect Failed. Did you press the physical button? Error: " + str(e)})

    # 2. Save Data
    session_data["hume_key"] = key
    session_data["light_name"] = light

    return jsonify({"success": True, "message": "Connected!"})

@socketio.on('audio_stream')
def handle_audio(data):
    if session_data["hume_key"]:
        new_loop.call_soon_threadsafe(audio_queue.put_nowait, data)

if __name__ == '__main__':
    print("🚀 App running on http://127.0.0.1:5001")
    socketio.run(app, allow_unsafe_werkzeug=True, debug=True, port=5001)
