import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import cv2
import numpy as np
import threading
import time
from PIL import Image, ImageTk
import keyboard
import os
import mss

class ScreenRecorder:
    def __init__(self, root):
        self.root = root
        self.root.title("Screen Recorder")
        self.root.geometry("600x500")
        self.root.resizable(False, False)

        # Configure grid layout
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=2)
        self.root.columnconfigure(2, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(4, weight=1)
        self.root.rowconfigure(5, weight=1)
        self.root.rowconfigure(6, weight=1)
        self.root.rowconfigure(7, weight=1)
        self.root.rowconfigure(8, weight=1)
        
        # Preview label
        self.preview_label = tk.Label(self.root)
        self.preview_label.grid(row=0, column=0, columnspan=3, pady=5, sticky="nsew")

        # FPS
        self.fps_label = tk.Label(self.root, text="FPS:")
        self.fps_label.grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.fps_options = [75, 60, 50, 40, 30, 20, 10, 5, 2]
        self.fps_var = tk.IntVar(value=25)
        self.fps_menu = ttk.Combobox(self.root, textvariable=self.fps_var, values=self.fps_options, state="readonly")
        self.fps_menu.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Resolution
        self.resolution_label = tk.Label(self.root, text="Resolution:")
        self.resolution_label.grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.resolution_options = [(1920, 1080), (1600, 900), (1366, 768), (1280, 720), (1024, 576), (800, 600), (640, 480), (320, 240), (160, 120), (100, 100)]
        self.resolution_var = tk.StringVar(value="640x480")
        self.resolution_menu = ttk.Combobox(self.root, textvariable=self.resolution_var, values=["x".join(map(str, res)) for res in self.resolution_options], state="readonly")
        self.resolution_menu.grid(row=2, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Save Format
        self.format_label = tk.Label(self.root, text="Save Format:")
        self.format_label.grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.format_options = ['.mp4', '.avi', '.mov', '.wmv']
        self.format_var = tk.StringVar(value='.mp4')
        self.format_menu = ttk.Combobox(self.root, textvariable=self.format_var, values=self.format_options, state="readonly")
        self.format_menu.grid(row=3, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Save Location
        self.location_label = tk.Label(self.root, text="Save Location:")
        self.location_label.grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.default_save_path = os.path.join(os.path.expanduser("~"), "Documents", "Recorder")
        self.location_var = tk.StringVar(value=self.default_save_path)
        self.location_entry = tk.Entry(self.root, textvariable=self.location_var, width=40)
        self.location_entry.grid(row=4, column=1, padx=5, pady=5, sticky='w')
        self.browse_button = tk.Button(self.root, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=4, column=2, padx=5, pady=5)

        # Filename
        self.filename_label = tk.Label(self.root, text="Filename:")
        self.filename_label.grid(row=5, column=0, padx=5, pady=5, sticky='e')
        self.filename_var = tk.StringVar(value="recording")
        self.filename_entry = tk.Entry(self.root, textvariable=self.filename_var, width=50)
        self.filename_entry.grid(row=5, column=1, columnspan=2, padx=5, pady=5, sticky='w')

        # Control Buttons
        self.start_button = tk.Button(self.root, text="Start Recording", command=self.start_recording, state="normal")
        self.start_button.grid(row=6, column=0, padx=5, pady=5, sticky='e')
        self.stop_button = tk.Button(self.root, text="Stop Recording", command=self.stop_recording, state="disabled")
        self.stop_button.grid(row=6, column=2, padx=5, pady=5, sticky='w')

        # Status Label
        self.status_label = tk.Label(self.root, text="")
        self.status_label.grid(row=7, column=0, columnspan=3, pady=5, sticky='nsew')

        # Shortcut Configuration
        self.shortcut_label = tk.Label(self.root, text="Set Shortcuts:")
        self.shortcut_label.grid(row=8, column=0, columnspan=3, pady=5)

        self.start_shortcut_label = tk.Label(self.root, text="Start Recording Shortcut:")
        self.start_shortcut_label.grid(row=9, column=0, padx=5, pady=5, sticky='e')
        self.start_shortcut_var = tk.StringVar(value="Shift+Q")
        self.start_shortcut_entry = tk.Entry(self.root, textvariable=self.start_shortcut_var, width=20)
        self.start_shortcut_entry.grid(row=9, column=1, padx=5, pady=5, sticky='w')
        self.start_shortcut_button = tk.Button(self.root, text="Set Shortcut", command=lambda: self.set_shortcut("start"))
        self.start_shortcut_button.grid(row=9, column=2, padx=5, pady=5)

        self.stop_shortcut_label = tk.Label(self.root, text="Stop Recording Shortcut:")
        self.stop_shortcut_label.grid(row=10, column=0, padx=5, pady=5, sticky='e')
        self.stop_shortcut_var = tk.StringVar(value="Shift+A")
        self.stop_shortcut_entry = tk.Entry(self.root, textvariable=self.stop_shortcut_var, width=20)
        self.stop_shortcut_entry.grid(row=10, column=1, padx=5, pady=5, sticky='w')
        self.stop_shortcut_button = tk.Button(self.root, text="Set Shortcut", command=lambda: self.set_shortcut("stop"))
        self.stop_shortcut_button.grid(row=10, column=2, padx=5, pady=5)

        self.recording = False
        self.preview_thread = threading.Thread(target=self.update_preview)
        self.preview_thread.daemon = True
        self.preview_thread.start()

        self.start_shortcut = "Shift+Q"
        self.stop_shortcut = "Shift+A"
        keyboard.add_hotkey(self.start_shortcut, self.start_recording)
        keyboard.add_hotkey(self.stop_shortcut, self.stop_recording)

    def browse_folder(self):
        folder_selected = filedialog.askdirectory(initialdir=self.default_save_path)
        if folder_selected:
            self.location_var.set(folder_selected)

    def update_preview(self):
        while True:
            if not self.recording:
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
                    img.thumbnail((320, 180))
                    imgtk = ImageTk.PhotoImage(image=img)
                    self.preview_label.config(image=imgtk)
                    self.preview_label.image = imgtk
            time.sleep(1/25)

    def start_recording(self):
        if not self.recording:
            filename = self.filename_var.get()
            save_format = self.format_var.get()
            filename_with_extension = f"{filename}{save_format}"

            self.recording = True
            self.status_label.config(text="Recording...")
            self.start_button.config(state="disabled")
            self.stop_button.config(state="normal")
            self.record_thread = threading.Thread(target=self.record_screen, args=(filename_with_extension,))
            self.record_thread.start()

    def stop_recording(self):
        if self.recording:
            self.recording = False
            self.status_label.config(text="")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")

    def record_screen(self, filename_with_extension):
        fps = self.fps_var.get()
        resolution = tuple(map(int, self.resolution_var.get().split('x')))
        save_path = os.path.join(self.location_var.get(), filename_with_extension)
        codec_map = {
            '.mp4': 'mp4v',
            '.avi': 'XVID',
            '.mov': 'mp4v',
            '.wmv': 'WMV2'
        }
        fourcc = cv2.VideoWriter_fourcc(*codec_map[self.format_var.get()])

        # Ensure the directory exists
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        out = cv2.VideoWriter(save_path, fourcc, fps, resolution)

        with mss.mss() as sct:
            monitor = sct.monitors[1]
            start_time = time.time()
            while self.recording:
                screenshot = sct.grab(monitor)
                frame = np.array(screenshot)
                frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, resolution)
                out.write(frame)
                # Sleep to maintain the specified FPS
                time.sleep(max(1.0 / fps - (time.time() - start_time), 0))
                start_time = time.time()
        out.release()

    def set_shortcut(self, action):
        if action == "start":
            prompt_text = "press key combination to start recording..."
            self.shortcut_prompt("Start Recording Shortcut", prompt_text, self.start_shortcut_var, "start")
        elif action == "stop":
            prompt_text = "press key combination to stop recording..."
            self.shortcut_prompt("Stop Recording Shortcut", prompt_text, self.stop_shortcut_var, "stop")

    def shortcut_prompt(self, action_name, prompt_text, var, action_type):
        def on_key(event):
            keys = keyboard.get_hotkey_name(event.scan_code).split('+')
            if len(keys) == 2:
                var.set('+'.join(keys))
                if action_type == "start":
                    self.start_shortcut = var.get()
                    keyboard.remove_hotkey(self.start_shortcut)
                    keyboard.add_hotkey(self.start_shortcut, self.start_recording)
                elif action_type == "stop":
                    self.stop_shortcut = var.get()
                    keyboard.remove_hotkey(self.stop_shortcut)
                    keyboard.add_hotkey(self.stop_shortcut, self.stop_recording)
                self.prompt_window.destroy()
            else:
                messagebox.showerror("Invalid Shortcut", "Please select a valid key combination with exactly two keys.")
                self.prompt_window.destroy()

        self.prompt_window = tk.Toplevel(self.root)
        self.prompt_window.title(action_name)
        self.prompt_window.geometry("300x150")
        self.prompt_window.resizable(False, False)
        
        label = tk.Label(self.prompt_window, text=prompt_text)
        label.pack(pady=20)
        
        self.prompt_window.bind("<KeyPress>", on_key)
        self.prompt_window.focus_set()

if __name__ == "__main__":
    root = tk.Tk()
    app = ScreenRecorder(root)
    root.mainloop()
