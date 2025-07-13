@echo off
echo 🚀 Installing Low-End-Code CLI...

:: Create virtual environment if not exists
if not exist venv (
    echo Creating Python virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
echo 📦 Installing Python dependencies...
pip install -r requirements.txt

:: Download model if not already present
set MODEL_PATH=models\Phi-3-mini-4k-instruct-q4.gguf
if exist %MODEL_PATH% (
    echo ✅ Model already present: %MODEL_PATH%
) else (
    echo 📥 Downloading Phi-3 Mini model...
    if not exist models mkdir models
    powershell -Command "Invoke-WebRequest -Uri https://huggingface.co/microsoft/Phi-3-mini-4k-instruct-gguf/resolve/main/Phi-3-mini-4k-instruct-q4.gguf -OutFile %MODEL_PATH%"
    echo ✅ Model downloaded: %MODEL_PATH%
)

echo 🎉 All set! Now run:
echo     python lec.py init

echo 🔗 Adding lec to global PATH...

set "TARGET=%USERPROFILE%\AppData\Local\Programs\lec"
if not exist %TARGET% mkdir %TARGET%
copy lec.bat %TARGET%\lec.bat
copy lec.py %TARGET%\lec.py

:: Add to user PATH (if not already)
setx PATH "%PATH%;%TARGET%" >nul

echo ✅ 'lec' is now globally available. Restart your terminal to use it from anywhere.
