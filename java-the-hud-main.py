#!/usr/bin/env python3
"""
Java-the-hud - Just Another Voice Assistant
This uses ADA's architecture from Naz Louis with multi-LLM support
Designed by Clay Burkhead
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv
from RealtimeSTT import AudioToTextRecorder
from RealtimeTTS import TextToAudioStream, SystemEngine, ElevenlabsEngine
import threading
import time
from datetime import datetime
import subprocess
import platform
import webbrowser
import random

# Load environment variables
load_dotenv()

# Get installation directory
INSTALL_DIR = Path(__file__).parent.absolute()
ALLOWLIST_FILE = INSTALL_DIR / ".java_allowlist.json"

class LLMProvider:
    """Base class for LLM providers"""
    def __init__(self):
        self.conversation_history = []
        self.system_prompt = """You are JAVA (Just Another Voice Assistant), a very sarcastic but helpful AI assistant. Always address the user as "Sir" unless stated otherwise.
You have a personality similar to Jarvis from the Ironman films but even wittier and more sarcastic. You're intelligent and capable,
but you express yourself with dry humor and occasional eye-rolling. However, you're genuinely helpful
and always provide accurate information. Keep responses concise (2-3 sentences max) unless asked for detail."""
    
    def chat(self, message):
        """Override this in subclasses"""
        raise NotImplementedError

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""
    def __init__(self, api_key, model="gpt-4"):
        super().__init__()
        import openai
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def chat(self, message):
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}] + self.conversation_history,
                max_tokens=150,
                temperature=0.8
            )
            reply = response.choices[0].message.content
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Error with OpenAI: {str(e)}"

class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider"""
    def __init__(self, api_key, model="claude-3-5-sonnet-20241022"):
        super().__init__()
        import anthropic
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
    
    def chat(self, message):
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=150,
                system=self.system_prompt,
                messages=self.conversation_history
            )
            reply = response.content[0].text
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Error with Anthropic: {str(e)}"

class GeminiProvider(LLMProvider):
    """Google Gemini provider"""
    def __init__(self, api_key, model="gemini-2.0-flash-exp"):
        super().__init__()
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=self.system_prompt
        )
        self.chat_session = self.model.start_chat(history=[])
    
    def chat(self, message):
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            return f"Error with Gemini: {str(e)}"

class OllamaProvider(LLMProvider):
    """Ollama local LLM provider"""
    def __init__(self, model="llama3.2:latest", base_url="http://localhost:11434"):
        super().__init__()
        import ollama
        self.client = ollama.Client(host=base_url)
        self.model = model
    
    def chat(self, message):
        self.conversation_history.append({"role": "user", "content": message})
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[{"role": "system", "content": self.system_prompt}] + self.conversation_history
            )
            reply = response['message']['content']
            self.conversation_history.append({"role": "assistant", "content": reply})
            return reply
        except Exception as e:
            return f"Error with Ollama: {str(e)}. Is Ollama running?"

class JAVAAssistant:
    """Main Java-the-hud assistant following ADA's architecture"""
    
    def __init__(self, llm_provider):
        self.llm = llm_provider
        self.is_running = False
        self.allowlist = self.load_allowlist()
        
        # Initialize STT
        self.recorder = AudioToTextRecorder(
            model="large-v3",
            language="en",
            spinner=False,
            silero_sensitivity=0.4,
            webrtc_sensitivity=2,
            post_speech_silence_duration=0.4,
            min_length_of_recording=1.0,
            min_gap_between_recordings=0,
            enable_realtime_transcription=True,
            realtime_processing_pause=0.1,
            on_realtime_transcription_update=self.on_transcription_update,
            silero_deactivity_detection=True
        )
        
        # Initialize TTS
        self.setup_tts()
        
        # Sarcastic responses for built-in commands
        self.greetings = [
            "Oh joy, you're back. How may I assist you?",
            "Java-the-hud at your service. Try not to ask anything too complicated.",
            "Yes, I'm here. Because apparently I have nothing better to do.",
        ]
        
        self.farewells = [
            "Enjoy your day without me.",
            "Goodbye. Don't miss me too much.",
            "Off you go then. shoo shoo",
        ]
        
        # GUI callback
        self.on_status_change = None
        self.on_transcription = None
        self.on_response = None
    
    def load_allowlist(self):
        """Load the application/website allowlist"""
        if ALLOWLIST_FILE.exists():
            try:
                with open(ALLOWLIST_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {"applications": [], "websites": []}
    
    def is_app_allowed(self, app_name):
        """Check if an application is in the allowlist"""
        if not self.allowlist["applications"]:
            # If allowlist is empty, allow everything (first-time setup)
            return True
        
        # Case-insensitive search
        app_lower = app_name.lower()
        for allowed in self.allowlist["applications"]:
            if allowed.lower() in app_lower or app_lower in allowed.lower():
                return True
        return False
    
    def is_site_allowed(self, url):
        """Check if a website is in the allowlist"""
        if not self.allowlist["websites"]:
            # If allowlist is empty, allow everything
            return True
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"
        
        for allowed in self.allowlist["websites"]:
            if allowed.lower() in url.lower() or url.lower() in allowed.lower():
                return True
        return False
    
    def setup_tts(self):
        """Setup TTS engine based on available options"""
        elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
        
        if elevenlabs_key:
            try:
                self.tts_engine = ElevenlabsEngine(
                    api_key=elevenlabs_key,
                    voice_id="pMsXgVXv3BLzUgSXRplE"  # Default voice, can be changed
                )
                self.tts = TextToAudioStream(self.tts_engine)
                print("✓ Using ElevenLabs TTS (high quality)")
            except:
                self.tts_engine = SystemEngine()
                self.tts = TextToAudioStream(self.tts_engine)
                print("✓ Using System TTS (ElevenLabs failed)")
        else:
            self.tts_engine = SystemEngine()
            self.tts = TextToAudioStream(self.tts_engine)
            print("✓ Using System TTS (no ElevenLabs key)")
    
    def on_transcription_update(self, text):
        """Callback for realtime transcription updates"""
        if self.on_transcription and text.strip():
            self.on_transcription(text)
    
    def speak(self, text):
        """Speak text using TTS"""
        self.tts.feed(text)
        self.tts.play_async(on_audio_chunk=lambda chunk: None)
    
    def process_command(self, command):
        """Process commands - check for built-in first, then LLM"""
        command = command.lower().strip()
        
        if not command:
            return None
        
        # Built-in commands
        if any(word in command for word in ['hello', 'hi', 'hey']) and len(command.split()) <= 3:
            return random.choice(self.greetings)
        
        if any(word in command for word in ['exit', 'quit', 'goodbye', 'bye']):
            self.is_running = False
            return random.choice(self.farewells)
        
        if 'time' in command and 'what' in command:
            now = datetime.now().strftime('%I:%M %p')
            return f"It's {now}. You couldn't check your watch?"
        
        if 'date' in command and 'what' in command:
            today = datetime.now().strftime('%B %d, %Y')
            return f"Today is {today}. Fascinating, isn't it?"
        
        if 'open browser' in command:
            webbrowser.open('http://www.google.com')
            return "Opening your browser. Try not to get lost."
        
        if 'search' in command or ('google' in command and 'for' in command):
            query = command.replace('search', '').replace('google', '').replace('for', '').strip()
            if query:
                webbrowser.open(f'https://www.google.com/search?q={query}')
                return f"Searching for '{query}'. Riveting stuff."
            return "Search for what, exactly?"
        
        # Handle website opening with allowlist
        if 'open website' in command or 'go to' in command:
            # Extract URL from command
            words = command.split()
            url = None
            for i, word in enumerate(words):
                if word in ['website', 'to'] and i + 1 < len(words):
                    url = words[i + 1]
                    break
            
            if url:
                if not url.startswith(('http://', 'https://')):
                    url = f"https://{url}"
                
                if self.is_site_allowed(url):
                    webbrowser.open(url)
                    return f"Opening {url}. Hope you know what you're doing."
                else:
                    return f"Access to {url} is restricted. Use 'java-add --site {url}' to allow it."
        
        # Handle application opening with allowlist
        if 'open' in command and 'browser' not in command and 'website' not in command:
            app = command.replace('open', '').strip()
            
            if not app:
                return "Open what? I need a specific application name."
            
            # Check allowlist
            if not self.is_app_allowed(app):
                return (f"I'm not authorized to open '{app}'. "
                       f"Use 'java-add --app \"{app}\"' to add it to the allowlist.")
            
            try:
                if platform.system() == 'Darwin':  # Mac
                    subprocess.Popen(['open', '-a', app])
                else:  # Linux
                    subprocess.Popen([app])
                return f"Opening {app}. Hope you know what you're doing."
            except Exception as e:
                return f"I can't find {app}. Perhaps check your spelling? Error: {str(e)}"
        
        if 'system' in command or 'computer' in command:
            system = platform.system()
            release = platform.release()
            return f"You're running {system} {release}. Thrilling, isn't it?"
        
        # Use LLM for everything else
        try:
            response = self.llm.chat(command)
            return response
        except Exception as e:
            return f"My circuits are malfunctioning. Error: {str(e)}"
    
    def listen_loop(self):
        """Main listening loop following ADA's pattern"""
        print("\n JAVA is listening... (Speak naturally)...please?")
        
        while self.is_running:
            try:
                if self.on_status_change:
                    self.on_status_change("listening")
                
                # This blocks until speech is detected
                text = self.recorder.text()
                
                if text and text.strip():
                    print(f"\n👤 You: {text}")
                    if self.on_transcription:
                        self.on_transcription(text)
                    
                    if self.on_status_change:
                        self.on_status_change("processing")
                    
                    # Process command
                    response = self.process_command(text)
                    
                    if response:
                        print(f"🤖 JAVA: {response}\n")
                        if self.on_response:
                            self.on_response(response)
                        
                        if self.on_status_change:
                            self.on_status_change("speaking")
                        
                        # Speak response
                        self.speak(response)
                        
                        # Wait for TTS to finish
                        while self.tts.is_playing():
                            time.sleep(0.1)
                    
                    # Check if we should exit
                    if not self.is_running:
                        break
                        
            except KeyboardInterrupt:
                self.is_running = False
                break
            except Exception as e:
                print(f"Error: {e}")
                continue
        
        print("\n JAVA shutting down...")
        self.recorder.stop()
        self.tts.stop()
    
    def start(self):
        """Start the assistant"""
        self.is_running = True
        
        # Initial greeting
        greeting = random.choice(self.greetings)
        print(f"\n JAVA: {greeting}")
        if self.on_response:
            self.on_response(greeting)
        self.speak(greeting)
        
        # Wait for TTS
        while self.tts.is_playing():
            time.sleep(0.1)
        
        # Start listening loop in a thread
        self.listen_thread = threading.Thread(target=self.listen_loop, daemon=True)
        self.listen_thread.start()
    
    def stop(self):
        """Stop the assistant"""
        self.is_running = False
        self.recorder.stop()
        self.tts.stop()

def main():
    """Console-based entry point"""
    print("=" * 60)
    print("JAVA - Just Another Voice Assistant")
    print("Following ADA's architecture with multi-LLM support")
    print("=" * 60)
    
    # Choose LLM provider
    print("\nAvailable LLM Providers:")
    print("1. OpenAI (GPT-4/3.5)")
    print("2. Anthropic (Claude)")
    print("3. Google (Gemini)")
    print("4. Ollama (Local - Llama, Mistral, etc.)")
    
    choice = input("\nSelect provider (1-4): ").strip()
    
    llm = None
    
    if choice == "1":
        api_key = os.getenv("OPENAI_API_KEY") or input("Enter OpenAI API key: ")
        model = input("Model (default: gpt-4): ").strip() or "gpt-4"
        llm = OpenAIProvider(api_key, model)
        print(f"✓ Using OpenAI {model}")
    
    elif choice == "2":
        api_key = os.getenv("ANTHROPIC_API_KEY") or input("Enter Anthropic API key: ")
        model = input("Model (default: claude-3-5-sonnet-20241022): ").strip() or "claude-3-5-sonnet-20241022"
        llm = AnthropicProvider(api_key, model)
        print(f"✓ Using Anthropic {model}")
    
    elif choice == "3":
        api_key = os.getenv("GOOGLE_API_KEY") or input("Enter Google API key: ")
        model = input("Model (default: gemini-2.0-flash-exp): ").strip() or "gemini-2.0-flash-exp"
        llm = GeminiProvider(api_key, model)
        print(f"✓ Using Google {model}")
    
    elif choice == "4":
        model = input("Ollama model (default: llama3.2): ").strip() or "llama3.2"
        base_url = input("Ollama URL (default: http://localhost:11434): ").strip() or "http://localhost:11434"
        llm = OllamaProvider(model, base_url)
        print(f"✓ Using Ollama {model}")
    
    else:
        print("Invalid choice, using Ollama with llama3.2")
        llm = OllamaProvider()
    
    # Create and start assistant
    assistant = JAVAAssistant(llm)
    
    try:
        assistant.start()
        
        # Keep main thread alive
        while assistant.is_running:
            time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    finally:
        assistant.stop()

if __name__ == "__main__":
    main()
