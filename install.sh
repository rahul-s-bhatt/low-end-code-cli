#!/bin/bash
echo "🚀 Installing Low-End-Code CLI..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  python -m venv venv
  echo "✅ Virtual environment created"
fi

# Activate the virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if model already exists
MODEL_PATH=\"models/Phi-3-mini-4k-instruct-q4.gguf\"
if [ ! -f \"$MODEL_PATH\" ]; then
  echo \"📥 Downloading Phi-3 Mini model...\"
  mkdir -p models
  wget -q https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf -O \"$MODEL_PATH\"
  echo \"✅ Model downloaded: $MODEL_PATH\"
else
  echo \"✅ Model already present: $MODEL_PATH\"
fi

echo \"🎉 All set! Now run:\"
echo \"  python lec.py init\"

echo "🔗 Adding lec to PATH..."

INSTALL_DIR=~/.local/bin
mkdir -p $INSTALL_DIR
cp lec $INSTALL_DIR/lec

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
  echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.bashrc
  echo "export PATH=\"$INSTALL_DIR:\$PATH\"" >> ~/.zshrc
  export PATH="$INSTALL_DIR:$PATH"
fi

echo "✅ 'lec' is now globally available (restart terminal if needed)"
