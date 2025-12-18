#!/usr/bin/env python3
"""
Java-the-hud GUI - Just Another Voice Assistant with GUI support
Following ADA's architecture with multi-LLM support
Dsigned by Clay Burkhead
"""

import tkinter as tk
from tkinter import scrolledtext, ttk, messagebox
import threading
from datetime import datetime
from java_the_hud_main import (
    JAVAAssistant, OpenAIProvider, AnthropicProvider, 
    GeminiProvider, OllamaProvider
)
import os

class JAVAGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Java-the-hud - Voice Assistant")
        self.root.geometry("800x700")
        self.root.configure(bg='#0a0e27')
        
        self.assistant = None
        self.llm_provider = None
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        # Header
        header_frame = tk.Frame(self.root, bg='#0a0e27')
        header_frame.pack(fill=tk.X, padx=20, pady=20)
        
        title = tk.Label(
            header_frame, 
            text="Java-the-hud", 
            font=('Helvetica', 36, 'bold'),
            bg='#0a0e27', 
            fg='#00ff9f'
        )
        title.pack()
        
        subtitle = tk.Label(
            header_frame,
            text="Just Another Voice Assistant",
            font=('Helvetica', 11, 'italic'),
            bg='#0a0e27',
            fg='#888'
        )
        subtitle.pack()
        
        # LLM Configuration Frame
        config_frame = tk.LabelFrame(
            self.root,
            text="LLM Configuration",
            font=('Helvetica', 11, 'bold'),
            bg='#1a1f3a',
            fg='#00ff9f',
            relief=tk.FLAT
        )
        config_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Provider selection
        provider_frame = tk.Frame(config_frame, bg='#1a1f3a')
        provider_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            provider_frame,
            text="Provider:",
            bg='#1a1f3a',
            fg='#fff',
            font=('Helvetica', 10)
        ).pack(side=tk.LEFT, padx=5)
        
        self.provider_var = tk.StringVar(value="openai")
        providers = [
            ("OpenAI", "openai"),
            ("Anthropic", "anthropic"),
            ("Google Gemini", "gemini"),
            ("Ollama (Local)", "ollama")
        ]
        
        for text, value in providers:
            tk.Radiobutton(
                provider_frame,
                text=text,
                variable=self.provider_var,
                value=value,
                bg='#1a1f3a',
                fg='#fff',
                selectcolor='#0a0e27',
                activebackground='#1a1f3a',
                activeforeground='#00ff9f',
                font=('Helvetica', 9),
                command=self.on_provider_change
            ).pack(side=tk.LEFT, padx=10)
        
        # API Key / Model configuration
        self.config_inner_frame = tk.Frame(config_frame, bg='#1a1f3a')
        self.config_inner_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API Key
        tk.Label(
            self.config_inner_frame,
            text="API Key:",
            bg='#1a1f3a',
            fg='#fff',
            font=('Helvetica', 9)
        ).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.api_key_entry = tk.Entry(
            self.config_inner_frame,
            show="*",
            bg='#0a0e27',
            fg='#00ff9f',
            insertbackground='#00ff9f',
            font=('Courier', 9),
            width=40
        )
        self.api_key_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.EW)
        
        # Model
        tk.Label(
            self.config_inner_frame,
            text="Model:",
            bg='#1a1f3a',
            fg='#fff',
            font=('Helvetica', 9)
        ).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        
        self.model_entry = tk.Entry(
            self.config_inner_frame,
            bg='#0a0e27',
            fg='#00ff9f',
            insertbackground='#00ff9f',
            font=('Courier', 9),
            width=40
        )
        self.model_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.EW)
        self.model_entry.insert(0, "gpt-4")
        
        self.config_inner_frame.columnconfigure(1, weight=1)
        
        # Initialize button
        self.init_button = tk.Button(
            config_frame,
            text="Initialize Java-the-hud",
            command=self.initialize_assistant,
            font=('Helvetica', 10, 'bold'),
            bg='#00ff9f',
            fg='#0a0e27',
            activebackground='#00cc7f',
            padx=20,
            pady=5,
            relief=tk.FLAT
        )
        self.init_button.pack(pady=10)
        
        # Status indicator
        status_frame = tk.Frame(self.root, bg='#0a0e27')
        status_frame.pack(pady=10)
        
        self.status_canvas = tk.Canvas(
            status_frame,
            width=20,
            height=20,
            bg='#0a0e27',
            highlightthickness=0
        )
        self.status_canvas.pack(side=tk.LEFT, padx=5)
        self.status_indicator = self.status_canvas.create_oval(2, 2, 18, 18, fill='#ff4444')
        
        self.status_label = tk.Label(
            status_frame,
            text="Not Initialized",
            font=('Helvetica', 11),
            bg='#0a0e27',
            fg='#888'
        )
        self.status_label.pack(side=tk.LEFT)
        
        # Chat display
        chat_frame = tk.Frame(self.root, bg='#0a0e27')
        chat_frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            wrap=tk.WORD,
            font=('Courier', 10),
            bg='#0f1419',
            fg='#00ff9f',
            insertbackground='#00ff9f',
            selectbackground='#1a1f3a',
            height=20
        )
        self.chat_display.pack(fill=tk.BOTH, expand=True)
        self.chat_display.config(state=tk.DISABLED)
        
        # Control buttons
        button_frame = tk.Frame(self.root, bg='#0a0e27')
        button_frame.pack(pady=10)
        
        self.start_button = tk.Button(
            button_frame,
            text="🎤 Start Listening",
            command=self.toggle_listening,
            font=('Helvetica', 11, 'bold'),
            bg='#444',
            fg='#888',
            activebackground='#555',
            padx=20,
            pady=10,
            relief=tk.FLAT,
            state=tk.DISABLED
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.clear_button = tk.Button(
            button_frame,
            text="Clear Chat",
            command=self.clear_chat,
            font=('Helvetica', 10),
            bg='#1a1f3a',
            fg='#fff',
            activebackground='#2a2f4a',
            padx=15,
            pady=10,
            relief=tk.FLAT
        )
        self.clear_button.pack(side=tk.LEFT, padx=5)
        
        # Footer
        footer = tk.Label(
            self.root,
            text="Uses ADA's architecture from Naz Louis | Say 'exit' to stop",
            font=('Helvetica', 8),
            bg='#0a0e27',
            fg='#555'
        )
        footer.pack(pady=10)
        
        # Load default API key if available
        self.on_provider_change()
    
    def on_provider_change(self):
        """Update UI based on provider selection"""
        provider = self.provider_var.get()
        
        # Clear entries
        self.api_key_entry.delete(0, tk.END)
        self.model_entry.delete(0, tk.END)
        
        # Set defaults based on provider
        if provider == "openai":
            key = os.getenv("OPENAI_API_KEY", "")
            self.api_key_entry.insert(0, key)
            self.model_entry.insert(0, "gpt-4")
            self.api_key_entry.config(show="*")
        
        elif provider == "anthropic":
            key = os.getenv("ANTHROPIC_API_KEY", "")
            self.api_key_entry.insert(0, key)
            self.model_entry.insert(0, "claude-3-5-sonnet-20241022")
            self.api_key_entry.config(show="*")
        
        elif provider == "gemini":
            key = os.getenv("GOOGLE_API_KEY", "")
            self.api_key_entry.insert(0, key)
            self.model_entry.insert(0, "gemini-2.0-flash-exp")
            self.api_key_entry.config(show="*")
        
        elif provider == "ollama":
            self.api_key_entry.insert(0, "http://localhost:11434")
            self.model_entry.insert(0, "llama3.2")
            self.api_key_entry.config(show="")
    
    def initialize_assistant(self):
        """Initialize the LLM and assistant"""
        provider = self.provider_var.get()
        api_key = self.api_key_entry.get().strip()
        model = self.model_entry.get().strip()
        
        if not model:
            messagebox.showerror("Error", "Please enter a model name")
            return
        
        try:
            # Create LLM provider
            if provider == "openai":
                if not api_key:
                    messagebox.showerror("Error", "Please enter OpenAI API key")
                    return
                self.llm_provider = OpenAIProvider(api_key, model)
                self.add_message("SYSTEM", f"Initialized OpenAI {model}")
            
            elif provider == "anthropic":
                if not api_key:
                    messagebox.showerror("Error", "Please enter Anthropic API key")
                    return
                self.llm_provider = AnthropicProvider(api_key, model)
                self.add_message("SYSTEM", f"Initialized Anthropic {model}")
            
            elif provider == "gemini":
                if not api_key:
                    messagebox.showerror("Error", "Please enter Google API key")
                    return
                self.llm_provider = GeminiProvider(api_key, model)
                self.add_message("SYSTEM", f"Initialized Google {model}")
            
            elif provider == "ollama":
                base_url = api_key if api_key else "http://localhost:11434"
                self.llm_provider = OllamaProvider(model, base_url)
                self.add_message("SYSTEM", f"Initialized Ollama {model} at {base_url}")
            
            # Create assistant
            self.assistant = JAVAAssistant(self.llm_provider)
            
            # Set callbacks
            self.assistant.on_status_change = self.update_status
            self.assistant.on_transcription = lambda text: self.add_message("You", text)
            self.assistant.on_response = lambda text: self.add_message("JAVA", text)
            
            # Enable start button
            self.start_button.config(
                bg='#00ff9f',
                fg='#0a0e27',
                state=tk.NORMAL
            )
            
            self.update_status("idle")
            self.init_button.config(state=tk.DISABLED)
            
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
    
    def toggle_listening(self):
        """Start or stop listening"""
        if not self.assistant:
            return
        
        if not self.assistant.is_running:
            # Start listening
            self.start_button.config(
                text="🛑 Stop Listening",
                bg='#ff4444'
            )
            threading.Thread(target=self.assistant.start, daemon=True).start()
        else:
            # Stop listening
            self.assistant.stop()
            self.start_button.config(
                text="🎤 Start Listening",
                bg='#00ff9f'
            )
            self.update_status("idle")
    
    def update_status(self, status):
        """Update status indicator"""
        status_map = {
            "idle": ("Idle", '#ff4444'),
            "listening": ("Listening...", '#44ff44'),
            "processing": ("Processing...", '#ffaa44'),
            "speaking": ("Speaking...", '#00aaff')
        }
        
        text, color = status_map.get(status, ("Unknown", '#888'))
        self.status_label.config(text=text)
        self.status_canvas.itemconfig(self.status_indicator, fill=color)
    
    def add_message(self, sender, message):
        """Add message to chat display"""
        self.chat_display.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Color coding
        if sender == "You":
            color = '#00d4ff'
        elif sender == "JAVA":
            color = '#ff6b9d'
        else:
            color = '#888'
        
        self.chat_display.insert(tk.END, f"[{timestamp}] ", 'timestamp')
        self.chat_display.insert(tk.END, f"{sender}: ", sender.lower())
        self.chat_display.insert(tk.END, f"{message}\n\n", 'message')
        
        self.chat_display.tag_config('timestamp', foreground='#555')
        self.chat_display.tag_config('you', foreground='#00d4ff', font=('Courier', 10, 'bold'))
        self.chat_display.tag_config('java', foreground='#ff6b9d', font=('Courier', 10, 'bold'))
        self.chat_display.tag_config('system', foreground='#888', font=('Courier', 10, 'italic'))
        self.chat_display.tag_config('message', foreground='#00ff9f')
        
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def clear_chat(self):
        """Clear chat display"""
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        self.add_message("SYSTEM", "Chat cleared.")

def main():
    root = tk.Tk()
    app = JAVAGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
