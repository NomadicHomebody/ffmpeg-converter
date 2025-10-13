import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import shutil

from conversion_logic import find_video_files, build_ffmpeg_command, execute_ffmpeg_command, get_output_filepath

class ConverterApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding="10")
        self.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        # Folder selection frame
        folder_frame = ttk.LabelFrame(self, text="Folder Selection", padding="10")
        folder_frame.grid(row=0, column=0, columnspan=2, sticky="ew")
        folder_frame.columnconfigure(1, weight=1)

        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar()

        ttk.Label(folder_frame, text="Input Folder:").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(folder_frame, textvariable=self.input_dir).grid(row=0, column=1, sticky="ew")
        ttk.Button(folder_frame, text="Browse...", command=self._select_input_folder).grid(row=0, column=2, sticky=tk.E)

        ttk.Label(folder_frame, text="Output Folder:").grid(row=1, column=0, sticky=tk.W)
        ttk.Entry(folder_frame, textvariable=self.output_dir).grid(row=1, column=1, sticky="ew")
        ttk.Button(folder_frame, text="Browse...", command=self._select_output_folder).grid(row=1, column=2, sticky=tk.E)

        # Conversion options frame
        options_frame = ttk.LabelFrame(self, text="Conversion Options", padding="10")
        options_frame.grid(row=1, column=0, sticky="ew", columnspan=2)
        options_frame.columnconfigure(1, weight=1)

        # Video Codec
        ttk.Label(options_frame, text="Video Codec:").grid(row=0, column=0, sticky=tk.W)
        self.video_codec = tk.StringVar(value="hevc_nvenc")
        video_codecs = ["hevc_nvenc", "h264_nvenc", "av1", "h264", "h265"]
        ttk.Combobox(options_frame, textvariable=self.video_codec, values=video_codecs, state="readonly").grid(row=0, column=1, sticky="ew")

        # Audio Codec
        ttk.Label(options_frame, text="Audio Codec:").grid(row=1, column=0, sticky=tk.W)
        self.audio_codec = tk.StringVar(value="aac")
        audio_codecs = ["aac", "mp3"]
        ttk.Combobox(options_frame, textvariable=self.audio_codec, values=audio_codecs, state="readonly").grid(row=1, column=1, sticky="ew")

        # Output Format
        ttk.Label(options_frame, text="Output Format:").grid(row=2, column=0, sticky=tk.W)
        self.output_format = tk.StringVar(value="mp4")
        output_formats = ["mp4", "mkv", "mov"]
        ttk.Combobox(options_frame, textvariable=self.output_format, values=output_formats, state="readonly").grid(row=2, column=1, sticky="ew")

        # Video Bitrate
        ttk.Label(options_frame, text="Video Bitrate:").grid(row=3, column=0, sticky=tk.W)
        self.video_bitrate = tk.StringVar(value="dynamic")
        bitrates = ["dynamic"] + [f"{i}M" for i in range(10, 251, 10)]
        ttk.Combobox(options_frame, textvariable=self.video_bitrate, values=bitrates, state="readonly").grid(row=3, column=1, sticky="ew")

        # Progress and Log frame
        progress_log_frame = ttk.LabelFrame(self, text="Progress and Log", padding="10")
        progress_log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        progress_log_frame.columnconfigure(0, weight=1)
        progress_log_frame.rowconfigure(0, weight=1)

        self.log_area = tk.Text(progress_log_frame, height=10)
        self.log_area.grid(row=0, column=0, sticky="nsew")

        self.progress_bar = ttk.Progressbar(progress_log_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew")

        # Start button
        self.start_button = ttk.Button(self, text="Start Conversion", command=self._start_conversion)
        self.start_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self._cancel_conversion, state=tk.DISABLED)
        self.cancel_button.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.conversion_widgets = [self.start_button] + list(self.children.values())

        self._check_ffmpeg()

    def _check_ffmpeg(self):
        if not shutil.which("ffmpeg"):
            messagebox.showerror("FFmpeg Not Found", "FFmpeg is not installed or not in your system's PATH. Please install FFmpeg to use this application.")
            self.master.destroy()

    def _toggle_widgets(self, enabled):
        for widget in self.conversion_widgets:
            if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                widget.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def _start_conversion(self):
        self._toggle_widgets(False)
        self.cancel_button.config(state=tk.NORMAL)
        self.cancel_event = threading.Event()
        self.progress_queue = queue.Queue()

        args = (
            self.input_dir.get(),
            self.output_dir.get(),
            self.video_codec.get(),
            self.audio_codec.get(),
            self.video_bitrate.get(),
            self.output_format.get(),
        )

        self.thread = threading.Thread(target=self._conversion_worker, args=args)
        self.thread.start()
        self.after(100, self._update_progress)

    def _select_input_folder(self):
        self.input_dir.set(filedialog.askdirectory())

    def _select_output_folder(self):
        self.output_dir.set(filedialog.askdirectory())


    def _cancel_conversion(self):
        self.cancel_event.set()

    def _conversion_worker(self, input_dir, output_dir, video_codec, audio_codec, video_bitrate, output_format):

        if not input_dir or not output_dir:
            self.progress_queue.put(("log", "Error: Input and output folders must be selected.\n"))
            return

        video_files = find_video_files(input_dir)
        if not video_files:
            self.progress_queue.put(("log", f"No video files found in {input_dir}\n"))
            return

        self.progress_queue.put(("log", f"Found {len(video_files)} video files to convert.\n"))
        self.progress_queue.put(("progress_max", len(video_files)))

        for i, video_file in enumerate(video_files):
            if self.cancel_event.is_set():
                self.progress_queue.put(("log", "Conversion canceled.\n"))
                return

            output_filepath = get_output_filepath(video_file, output_dir, output_format)
            command = build_ffmpeg_command(
                video_file,
                output_filepath,
                video_codec,
                audio_codec,
                video_bitrate,
            )
            self.progress_queue.put(("log", f"Converting {video_file} to {output_filepath}...\n"))
            try:
                execute_ffmpeg_command(command)
                self.progress_queue.put(("log", "Conversion successful.\n"))
            except Exception as e:
                self.progress_queue.put(("log", f"Error converting {video_file}: {e}\n"))
            
            self.progress_queue.put(("progress", i + 1))

        self.progress_queue.put(("log", "All conversions complete.\n"))

    def _update_progress(self):
        try:
            while True:
                message_type, data = self.progress_queue.get_nowait()
                if message_type == "log":
                    self.log_area.insert(tk.END, data)
                elif message_type == "progress_max":
                    self.progress_bar["maximum"] = data
                elif message_type == "progress":
                    self.progress_bar["value"] = data
                self.update_idletasks()
        except queue.Empty:
            pass

        if self.thread.is_alive():
            self.after(100, self._update_progress)
        else:
            self._toggle_widgets(True)
            self.cancel_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("FFMPEG Bulk Converter")
    root.geometry("800x600")
    app = ConverterApp(root)
    root.mainloop()