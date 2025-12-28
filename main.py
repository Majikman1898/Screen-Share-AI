import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import keyboard
import os
import queue
from core.screen_capture import capture_screen_as_base64
from core.api_client import AIClient
from core.audio import speak_text

class ScreenReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Screen Reader")
        self.root.geometry("600x500")

        # Variables
        self.api_key = tk.StringVar()
        self.model_name = tk.StringVar(value="gpt-4o")
        self.hotkey_var = tk.StringVar(value="ctrl+alt+s")
        self.include_context = tk.BooleanVar(value=True)
        self.status_var = tk.StringVar(value="Ready")

        self.ai_client = None
        self.is_listening = False

        # Queue for thread-safe UI updates
        self.ui_queue = queue.Queue()
        self.root.after(100, self.process_ui_queue)

        self._create_widgets()

    def _create_widgets(self):
        # API Key Section
        api_frame = ttk.LabelFrame(self.root, text="Settings", padding=10)
        api_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(api_frame, text="OpenAI API Key:").grid(row=0, column=0, sticky="w")
        self.api_entry = ttk.Entry(api_frame, textvariable=self.api_key, show="*", width=40)
        self.api_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(api_frame, text="Model:").grid(row=1, column=0, sticky="w")
        # Only include vision-capable models
        models = ["gpt-4o", "gpt-4-turbo"]
        self.model_combo = ttk.Combobox(api_frame, textvariable=self.model_name, values=models)
        self.model_combo.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(api_frame, text="Hotkey:").grid(row=2, column=0, sticky="w")
        self.hotkey_entry = ttk.Entry(api_frame, textvariable=self.hotkey_var)
        self.hotkey_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        self.set_hotkey_btn = ttk.Button(api_frame, text="Set Hotkey", command=self.update_hotkey)
        self.set_hotkey_btn.grid(row=2, column=2, padx=5)

        ttk.Checkbutton(api_frame, text="Include Prior Context", variable=self.include_context).grid(row=3, column=1, sticky="w")

        # Controls
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10)

        self.start_btn = ttk.Button(control_frame, text="Start Listening", command=self.toggle_listening)
        self.start_btn.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Clear History", command=self.clear_history).pack(side="left", padx=5)

        # Chat/Log Area
        log_frame = ttk.LabelFrame(self.root, text="Log / Conversation", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, state="disabled", height=15)
        self.log_area.pack(fill="both", expand=True)

        # Status Bar
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def process_ui_queue(self):
        """Check queue for UI updates."""
        try:
            while True:
                task = self.ui_queue.get_nowait()
                action = task.get("action")
                if action == "log":
                    self._log_internal(task["message"])
                elif action == "status":
                    self.status_var.set(task["message"])
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.process_ui_queue)

    def log(self, message):
        """Thread-safe logging."""
        self.ui_queue.put({"action": "log", "message": message})

    def set_status(self, message):
        """Thread-safe status update."""
        self.ui_queue.put({"action": "status", "message": message})

    def _log_internal(self, message):
        self.log_area.config(state="normal")
        self.log_area.insert("end", message + "\n")
        self.log_area.see("end")
        self.log_area.config(state="disabled")

    def toggle_listening(self):
        if not self.is_listening:
            api_key = self.api_key.get().strip()
            if not api_key:
                messagebox.showerror("Error", "Please enter an OpenAI API Key.")
                return

            self.ai_client = AIClient(api_key, self.model_name.get())
            self.start_hotkey_listener()
            self.start_btn.config(text="Stop Listening")
            self.status_var.set("Listening for hotkey...")
            self.is_listening = True
            self.log("System: Started listening.")
        else:
            self.stop_hotkey_listener()
            self.start_btn.config(text="Start Listening")
            self.status_var.set("Stopped.")
            self.is_listening = False
            self.log("System: Stopped listening.")

    def start_hotkey_listener(self):
        hotkey = self.hotkey_var.get()
        try:
            keyboard.add_hotkey(hotkey, self.on_hotkey_triggered)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set hotkey: {e}")
            self.toggle_listening() # Revert

    def stop_hotkey_listener(self):
        keyboard.unhook_all_hotkeys()

    def update_hotkey(self):
        if self.is_listening:
            self.stop_hotkey_listener()
            self.start_hotkey_listener()
            self.log(f"System: Hotkey updated to {self.hotkey_var.get()}")

    def on_hotkey_triggered(self):
        self.log("System: Hotkey triggered! Capturing screen...")
        self.set_status("Processing...")

        # Run in thread to not freeze GUI
        threading.Thread(target=self.process_request).start()

    def process_request(self):
        image_b64 = capture_screen_as_base64()
        if not image_b64:
            self.log("Error: Failed to capture screen.")
            self.set_status("Error capturing screen")
            return

        self.log("System: Sending to AI...")
        response = self.ai_client.send_query(
            prompt="Analyze this screen content and describe what you see, or answer any obvious question presented.",
            image_base64=image_b64,
            include_history=self.include_context.get()
        )

        self.log(f"AI: {response}")
        self.set_status("Ready")

        # Speak response
        speak_text(response)

    def clear_history(self):
        if self.ai_client:
            self.ai_client.clear_history()
        self.log("System: History cleared.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenReaderApp(root)
    root.mainloop()
