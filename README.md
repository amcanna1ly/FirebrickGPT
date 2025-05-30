# 🔥🧱 FirebrickGPT
FirebrickGPT is a local LLM interface for Raspberry Pi 5 using Flask and Mistral via llama.cpp. It supports a dark mode UI, command execution mode, and runs fully offline. Ideal for privacy-focused or embedded AI applications.

# FirebrickGPT Setup on Raspberry Pi 5

## 🔧 Requirements
- Raspberry Pi 5 (4GB or 8GB recommended)
- Ubuntu 22.04 or Raspberry Pi OS 64-bit
- Internet connection
- Python 3.9+ (Python 3.12 used here)
- Git

---

## Step-by-Step Installation

### 🔧 1. Update and Install System Dependencies
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git python3 python3-pip build-essential cmake libopenblas-dev libomp-dev
```

### 🧪 2. Set Up Virtual Environment (Optional but Recommended)
```bash
sudo apt install -y python3-venv
mkdir ~/llm-flask && cd ~/llm-flask
python3 -m venv venv
source venv/bin/activate
```

### 📦 3. Install Python Dependencies
Create a `requirements.txt` file (or use this command):
```bash
pip install flask markupsafe markdown
```

You can also auto-generate a requirements file:
```bash
pip freeze > requirements.txt
```

### 🛠️  4. Download and Build llama.cpp
```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make -j$(nproc)
cd ..
```

### 📥 5. Download a Quantized Mistral Model
```bash
mkdir -p models/mistral
cd models/mistral
wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf
cd ../../
```

### 📄 6. Copy or Create the app.py Web App
Ensure the folder contains:
- `app.py`
- `llama/llama-cli` (symlink or move binary from `llama.cpp`)
- `models/mistral/mistral-7b-instruct-v0.1.Q4_K_M.gguf`
- `static/` folder for logo image (if applicable)

### 🚀 7. Run the Flask App
```bash
source venv/bin/activate
python app.py
```

Access the app in your browser at:
`http://<pi-ip>:5050`

---

## Optional: Run as a Background Service
To keep it running after SSH disconnect:
```bash
nohup python app.py &
```
Or, set up a `systemd` service for persistence.

## 🧭 Planned Features

    User authentication for protected access to command mode

    Chat history and session context memory

    Voice input and output via WebRTC or browser APIs

    Pi system dashboard for real-time stats via natural language

    Custom instruction tuning with user-provided documents

    Offline documentation agent (query Linux man pages or local manuals)
