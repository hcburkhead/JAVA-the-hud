#!/bin/bash
# JAVA-the-hud Setup Script

echo "=========================================="
echo "JAVA - Just Another Voice Assistant"
echo "Using ADA Architecture from Naz Louis"
echo "=========================================="
echo ""

# Detect OS
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="mac"
    echo "✓ Detected: macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
    echo "✓ Detected: Linux"
else
    echo "❌ Unsupported operating system"
    exit 1
fi

echo ""
echo "Installing dependencies..."
echo ""

# Install system dependencies
if [ "$OS" = "mac" ]; then
    echo "→ Checking for Homebrew..."
    if ! command -v brew &> /dev/null; then
        echo "❌ Homebrew not found. Please install from https://brew.sh"
        exit 1
    fi
    
    echo "→ Installing PortAudio and FFmpeg..."
    brew install portaudio ffmpeg
    
elif [ "$OS" = "linux" ]; then
    echo "→ Installing system packages..."
    
    if command -v apt-get &> /dev/null; then
        sudo apt-get update
        sudo apt-get install -y portaudio19-dev python3.11 python3.11-venv ffmpeg espeak espeak-ng
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y portaudio-devel python3.11 ffmpeg espeak
    else
        echo "⚠️  Package manager not supported. Please install manually:"
        echo "   - portaudio19-dev"
        echo "   - python3.11"
        echo "   - ffmpeg"
        echo "   - espeak (for TTS)"
        exit 1
    fi
fi

# Create virtual environment
echo ""
echo "→ Creating Python virtual environment..."
python3.11 -m venv venv

# Activate virtual environment
if [ "$OS" = "mac" ]; then
    source venv/bin/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "→ Upgrading pip..."
pip install --upgrade pip

# Install Python packages
echo ""
echo "→ Installing Python dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "⚠️  Some dependencies failed. Trying alternative installation..."
    
    # Install core packages first
    pip install python-dotenv
    pip install RealtimeSTT==0.3.7 RealtimeTTS==0.4.3
    
    # Install LLM clients (these might fail individually, that's ok)
    pip install openai anthropic google-generativeai ollama || echo "⚠️  Some LLM clients failed (optional)"
    
    # Try ElevenLabs
    pip install elevenlabs || echo "⚠️  ElevenLabs failed (optional)"
fi

# Create .env from template if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "→ Creating .env file from template..."
    cp .env.template .env
    echo "✓ Created .env - please edit it to add your API keys"
fi

# Make scripts executable
chmod +x java-the-hud-main.py java-the-hud-gui.py

echo ""
echo "=========================================="
echo "✓ Setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. If using Ollama (local models), install it:"
echo "   curl -fsSL https://ollama.com/install.sh | sh"
echo "   ollama pull llama3.2"
echo ""
echo "3. Run JAVA:"
echo "   • Console mode: java-activate --console"
echo "   • GUI mode: java-activate"
echo ""
echo "4. Choose your LLM provider:"
echo "   • OpenAI (requires OPENAI_API_KEY)"
echo "   • Anthropic (requires ANTHROPIC_API_KEY)"
echo "   • Google Gemini (requires GOOGLE_API_KEY)"
echo "   • Ollama (no key needed, runs locally)"
echo ""
echo "For ElevenLabs TTS (optional but recommended):"
echo "   • Get key from elevenlabs.io"
echo "   • Add ELEVENLABS_API_KEY to .env"
echo ""
echo "Architecture reference: https://github.com/Nlouis38/ada"
echo ""
