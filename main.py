import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import keyboard
import os
import queue
from core.screen_capture import capture_screen_as_base64
from core.api_client import AIClient
from core.audio import speak_text

class SettingsDialog(tk.Toplevel):
    def __init__(self, parent, current_settings, on_save):
        super().__init__(parent)
        self.title("Settings")
        self.geometry("400x250")
        self.on_save = on_save

        # Modal
        self.transient(parent)
        self.grab_set()

        # Local variables to hold temporary changes
        self.api_key = tk.StringVar(value=current_settings.get("api_key", ""))
        self.model_name = tk.StringVar(value=current_settings.get("model_name", "gpt-4o"))
        self.hotkey_var = tk.StringVar(value=current_settings.get("hotkey", "ctrl+alt+s"))
        self.include_context = tk.BooleanVar(value=current_settings.get("include_context", True))

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill="both", expand=True)

        # API Key
        ttk.Label(main_frame, text="OpenAI API Key:").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.api_key, show="*", width=30).grid(row=0, column=1, sticky="ew", pady=5)

        # Model
        ttk.Label(main_frame, text="Model:").grid(row=1, column=0, sticky="w", pady=5)
        models = ["gpt-4o", "gpt-4-turbo"]
        ttk.Combobox(main_frame, textvariable=self.model_name, values=models).grid(row=1, column=1, sticky="ew", pady=5)

        # Hotkey
        ttk.Label(main_frame, text="Hotkey:").grid(row=2, column=0, sticky="w", pady=5)
        ttk.Entry(main_frame, textvariable=self.hotkey_var).grid(row=2, column=1, sticky="ew", pady=5)

        # Context
        ttk.Checkbutton(main_frame, text="Include Prior Context", variable=self.include_context).grid(row=3, column=1, sticky="w", pady=5)

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(btn_frame, text="Save", command=self.save).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side="left", padx=5)

        main_frame.columnconfigure(1, weight=1)

    def save(self):
        new_settings = {
            "api_key": self.api_key.get().strip(),
            "model_name": self.model_name.get(),
            "hotkey": self.hotkey_var.get(),
            "include_context": self.include_context.get()
        }
        self.on_save(new_settings)
        self.destroy()

class ScreenReaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Screen Reader")
        self.root.geometry("600x400")

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
        # Toolbar / Controls
        control_frame = ttk.Frame(self.root, padding=10)
        control_frame.pack(fill="x", padx=10)

        self.start_btn = ttk.Button(control_frame, text="Start Listening", command=self.toggle_listening)
        self.start_btn.pack(side="left", padx=5)

        ttk.Button(control_frame, text="Clear History", command=self.clear_history).pack(side="left", padx=5)

        # Spacer
        ttk.Frame(control_frame).pack(side="left", fill="x", expand=True)

        ttk.Button(control_frame, text="Settings", command=self.open_settings).pack(side="right", padx=5)

        # Chat/Log Area
        log_frame = ttk.LabelFrame(self.root, text="Log / Conversation", padding=10)
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.log_area = scrolledtext.ScrolledText(log_frame, state="disabled", height=15)
        self.log_area.pack(fill="both", expand=True)

        # Status Bar
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")

    def open_settings(self):
        current_settings = {
            "api_key": self.api_key.get(),
            "model_name": self.model_name.get(),
            "hotkey": self.hotkey_var.get(),
            "include_context": self.include_context.get()
        }
        SettingsDialog(self.root, current_settings, self.apply_settings)

    def apply_settings(self, new_settings):
        self.api_key.set(new_settings["api_key"])
        self.model_name.set(new_settings["model_name"])
        self.include_context.set(new_settings["include_context"])

        old_hotkey = self.hotkey_var.get()
        new_hotkey = new_settings["hotkey"]

        if old_hotkey != new_hotkey:
            self.hotkey_var.set(new_hotkey)
            self.update_hotkey()

        self.log("System: Settings updated.")

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
                messagebox.showerror("Error", "Please enter an OpenAI API Key in Settings.")
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
