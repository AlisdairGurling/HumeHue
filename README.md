# 💡 Empathy Light: Hume AI x Philips Hue

An interactive smart home project that uses AI to analyze the emotion in your voice and changes your room's lighting color to match your mood in real-time.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-Web%20App-green)
![Hume AI](https://img.shields.io/badge/Hume%20AI-Prosody-purple)

## 🌟 Features

* **Real-time Emotion Detection:** Uses Hume AI's Prosody model to analyze speech tone and nuance.
* **Dynamic Lighting:** Controls Philips Hue lights instantly via local network.
* **Secure Web Interface:** Enter your API keys and Bridge IP via the browser (no hardcoding secrets).
* **Visual Dashboard:** See the detected emotion and confidence score live on screen.

## 🎨 Emotion Color Map

| Emotion Detected | Light Color |
| :--- | :--- |
| **Joy / Excitement** | 🟡 Bright Yellow / Orange |
| **Anger / Disgust** | 🔴 Deep Red |
| **Sadness** | 🔵 Dim Blue |
| **Calmness / Satisfaction** | 🟢 Soft Teal |
| **Fear / Anxiety** | 🟣 Violet |
| **Neutral** | ⚪️ Warm White |

## 🛠 Prerequisites

* **Hardware:** A Philips Hue Bridge and at least one Hue Light (e.g., Hue Go).
* **API Key:** A free API key from [Hume AI](https://platform.hume.ai/).
* **Python:** Version 3.9 or higher.

## 🚀 Installation

1.  **Clone the repository**
    ```bash
    git clone [https://github.com/YOUR_USERNAME/hume-hue-bridge.git](https://github.com/YOUR_USERNAME/hume-hue-bridge.git)
    cd hume-hue-bridge
    ```

2.  **Set up Virtual Environment**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

## 🎤 How to Run

1.  **Start the Server**
    ```bash
    python3 app.py
    ```

2.  **Open the Web Interface**
    Open your browser and navigate to: `http://127.0.0.1:5000`

3.  **Connect System**
    * Enter your **Hume API Key**.
    * Enter your **Hue Bridge IP** (Find via Hue App > Settings > Bridge).
    * Enter your **Light Name** (Must match Hue App exactly).
    * ⚠️ **IMPORTANT:** Walk to your physical Hue Bridge and **press the large center button**, then immediately click **"Connect System"** on the web page.

4.  **Start Listening**
    Click "Start Listening" and speak into your microphone!

## 🤝 Troubleshooting

* **"Bridge Connect Failed"**: Ensure you pressed the physical button on the Hue Bridge within 30 seconds of clicking Connect.
* **"Address already in use"**: Another instance of the app is running. Close your terminal or run `lsof -i :5000` to find and kill the process.
* **Lights not changing?**: Check if the "Light Name" matches exactly (Case Sensitive) with what is in your mobile Hue App.

## 📜 License

This project is open source. Feel free to modify and distribute.
