# JAVA-the-hud
## Just. Another. Voice. Assistant.


<img width="722" height="372" alt="ascii-art (1)" src="https://github.com/user-attachments/assets/c2fb86c0-afbc-4dbd-a690-cc8b7b6c4f99" />



A personal AI assistant to help you automate tasks by speaking to it. Features a GUI with real-time waveforms to visualize voice activity and responses. This acts as a wrapper for whatever LLM you want - just needs an API key.

Named "Java-the-hud" to avoid conflicts with Java programming language installations on user systems.

## Setup

```bash
# 1. Install
./setup.sh

# 2. Configure (choose one):
# Option A: Use Ollama (free, local)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2

# Option B: Use cloud LLM
nano .env  # Add OPENAI_API_KEY or others

# 3. Setup security allowlist
java-add --app "Spotify"
java-add --app "Firefox"
java-add --site "github.com"

# 4. Launch
java-activate  # GUI mode
# OR
java-activate --console  # Console mode
```

## Pre-requisites

**Required:**
- Python 3.11+
- Microphone and speakers
- LLM API Key (OpenAI, Anthropic, Google Gemini) OR Ollama installed locally

**Optional:**
- ElevenLabs API Key (for high-quality voice synthesis - otherwise uses system TTS)
- Google Maps API Key (for travel time queries)

## Installation

**MacOS:**
```bash
brew install python@3.11 portaudio ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.11 portaudio19-dev ffmpeg espeak
```

**Linux (Fedora):**
```bash
sudo dnf install python3.11 portaudio-devel ffmpeg espeak
```

## CLI

Download the repository and run it in Python using its own virtual environment. The setup script will create the virtual environment and install all dependencies:

```bash
cd java-the-hud
./setup.sh
```

The system will detect your microphone after initialization. Launch with:

```bash
java-activate
```

## GUI

The GUI provides a visual interface with:
- LLM provider selection (OpenAI, Anthropic, Google Gemini, Ollama)
- Real-time status indicators (idle, listening, processing, speaking)
- Live conversation history display
- Model and API key configuration

Tested on Linux (including Arch) and MacOS. Can be integrated into desktop environments like KDE as needed.

## Use

Java-the-hud can perform the following actions:

**Application Management:**
- Open applications placed in the app allowlist via `java-add`
- Install applications placed in the app allowlist via `java-add` (requires sudo group access - run `./java-sudo-access.sh` if desired)
- Perform specific actions in apps as specified in config files (power users can customize extensively)

**Voice Commands:**
- "Open [application]" - Launches allowed applications
- "Go to [website]" - Opens allowed websites in default browser
- "Search for [query]" - Performs web search in default browser (or specify browser: "search for linux commands in Brave")
- "What time is it?" - Current time
- "What's the date?" - Current date
- "Hello" - Greeting
- "Exit" - Stop listening

**Advanced Features:**
- Google Maps integration (requires MAPS API Key): "Java, how long of a drive would it be to go to [destination]?" - Java responds with travel time and offers to open directions
- All other queries are processed by your selected LLM with a sarcastic but helpful personality

**Security:**
- Application allowlist prevents unauthorized app launches
- Website allowlist controls which sites can be opened
- Empty allowlist allows everything (first-time setup)
- Adding one item activates deny-by-default security mode

## Allowlist Management

```bash
# Interactive menu
java-add

# Quick commands
java-add --app "Application Name"
java-add --site "website.com"
java-add --list
java-add --remove-app 2
java-add --remove-site 1
java-add --clear
```

## Configuration

Create a `.env` file from the template:

```bash
cp env.template .env
nano .env
```

Add your API keys:

```env
# Choose ONE LLM provider:
OPENAI_API_KEY=sk-your-key-here
# OR
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
GOOGLE_API_KEY=your-key-here

# Optional:
ELEVENLABS_API_KEY=your-key-here  # High-quality TTS
MAPS_API_KEY=your-key-here  # For travel time queries
```

## Architecture

Based on ADA by Naz Louis (https://github.com/Nlouis38/ada):

```
Microphone → RealtimeSTT (Whisper) → Command Processing → LLM → Security Check → RealtimeTTS → Speakers
```

## Supported LLM Providers

- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude 3.5 Sonnet, Claude 3 Haiku)
- Google Gemini (2.0 Flash, 1.5 Flash)
- Ollama (Llama 3.2, Mistral, Gemma, etc. - runs locally)

## Troubleshooting

**Command not found:**
```bash
chmod +x java-activate java-add setup.sh
export PATH=$PATH:$(pwd)
```

**Microphone not working:**
```bash
# Linux
arecord -l  # List devices
arecord -d 3 test.wav  # Test recording

# MacOS
# Grant permission: System Settings → Privacy → Microphone → Terminal
```

**Ollama connection refused:**
```bash
ollama serve  # Start Ollama server
ollama list   # Verify models installed
```

**App won't open:**
```bash
java-add --list  # Check allowlist
java-add --app "ExactAppName"  # Case-sensitive
```

## Credits

- Architecture inspired by ADA by Naz Louis
- Voice processing: RealtimeSTT and RealtimeTTS
- LLM providers: OpenAI, Anthropic, Google, Ollama

## License

MIT License
