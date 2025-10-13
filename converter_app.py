import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import shutil
import os
import concurrent.futures
import functools
import time

from conversion_logic import find_video_files, build_ffmpeg_command, execute_ffmpeg_command, get_output_filepath, get_file_details

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
        video_codecs = ["hevc_nvenc", "h264_nvenc", "av1_nvenc", "av1", "h264", "h265"]
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
        self.video_bitrate = tk.StringVar(value="optimized")
        bitrates = ["dynamic", "optimized"] + [f"{i}M" for i in range(5, 251, 5)]
        ttk.Combobox(options_frame, textvariable=self.video_bitrate, values=bitrates, state="readonly").grid(row=3, column=1, sticky="ew")

        # Delete input file checkbox
        self.delete_input = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Delete input files after successful conversion", variable=self.delete_input).grid(row=4, column=0, columnspan=2, sticky=tk.W)

        # Fallback Bitrate
        ttk.Label(options_frame, text="Fallback Bitrate (if dynamic fails):").grid(row=5, column=0, sticky=tk.W)
        self.fallback_bitrate = tk.StringVar(value="20M")
        ttk.Entry(options_frame, textvariable=self.fallback_bitrate).grid(row=5, column=1, sticky="ew")

        # Cap dynamic bitrate checkbox
        self.cap_dynamic_bitrate = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Cap dynamic bitrate at fallback bitrate", variable=self.cap_dynamic_bitrate).grid(row=6, column=0, columnspan=2, sticky=tk.W)

        # Concurrent Conversions
        ttk.Label(options_frame, text="Concurrent Conversions:").grid(row=7, column=0, sticky=tk.W)
        self.concurrent_conversions = tk.IntVar(value=2)
        self.concurrent_conversions_spinbox = ttk.Spinbox(options_frame, from_=1, to=32, textvariable=self.concurrent_conversions, state="readonly")
        self.concurrent_conversions_spinbox.grid(row=7, column=1, sticky="ew")

        # Verbose Logging
        self.verbose_logging = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Enable Verbose Logging", variable=self.verbose_logging).grid(row=8, column=0, columnspan=2, sticky=tk.W)

        # Progress and Log frame
        progress_log_frame = ttk.LabelFrame(self, text="Progress and Log", padding="10")
        progress_log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        progress_log_frame.columnconfigure(0, weight=1)
        progress_log_frame.rowconfigure(0, weight=1)

        self.log_area = tk.Text(progress_log_frame, height=10)
        self.log_area.grid(row=0, column=0, sticky="nsew")

        self.progress_bar = ttk.Progressbar(progress_log_frame, orient="horizontal", mode="determinate")
        self.progress_bar.grid(row=1, column=0, sticky="ew")

        self.eta_label = ttk.Label(progress_log_frame, text="ETA: Calculating...")
        self.eta_label.grid(row=2, column=0, sticky=tk.W)

        # Log control buttons
        log_buttons_frame = ttk.Frame(progress_log_frame)
        log_buttons_frame.grid(row=3, column=0, sticky="ew")
        log_buttons_frame.columnconfigure(0, weight=1)
        log_buttons_frame.columnconfigure(1, weight=1)

        ttk.Button(log_buttons_frame, text="Clear Log", command=self._clear_log).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(log_buttons_frame, text="Save Log", command=self._save_log).grid(row=0, column=1, sticky=tk.E)

        # Start button
        self.start_button = ttk.Button(self, text="Start Conversion", command=self._start_conversion)
        self.start_button.grid(row=3, column=0, columnspan=2, sticky="ew")

        self.cancel_button = ttk.Button(self, text="Cancel", command=self._cancel_conversion, state=tk.DISABLED)
        self.cancel_button.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.conversion_widgets = [self.start_button] + list(self.children.values())
        self.current_processes = {}

        self._check_ffmpeg()

    def _check_ffmpeg(self):
        if not shutil.which("ffmpeg"):
            messagebox.showerror("FFmpeg Not Found", "FFmpeg is not installed or not in your system's PATH. Please install FFmpeg to use this application.")
            self.master.destroy()

    def _toggle_widgets(self, enabled):
        for widget in self.conversion_widgets:
            if isinstance(widget, (ttk.Button, ttk.Entry, ttk.Combobox)):
                widget.config(state=tk.NORMAL if enabled else tk.DISABLED)

    def _clear_log(self):
        self.log_area.delete("1.0", tk.END)

    def _save_log(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
                                                 title="Save Log File")
        if file_path:
            try:
                with open(file_path, "w") as f:
                    f.write(self.log_area.get("1.0", tk.END))
                messagebox.showinfo("Save Log", "Log saved successfully!")
            except Exception as e:
                messagebox.showerror("Save Log Error", f"Failed to save log: {e}")

    def _start_conversion(self):
        self._toggle_widgets(False)
        self.cancel_button.config(state=tk.NORMAL)
        self.cancel_event = threading.Event()
        self.progress_queue = queue.Queue()
        self.start_time = time.time() # Initialize start time
        self.total_files_count = 0 # Will be set in _conversion_worker

        args = (
            self.input_dir.get(),
            self.output_dir.get(),
            self.video_codec.get(),
            self.audio_codec.get(),
            self.video_bitrate.get(),
            self.output_format.get(),
            self.delete_input.get(),
            self.fallback_bitrate.get(),
            self.cap_dynamic_bitrate.get(),
            self.concurrent_conversions.get(),
            self.start_time, # Pass start_time
            self.verbose_logging.get(), # Pass verbose_logging state
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
        for video_file, process in self.current_processes.items():
            if process.poll() is None:  # Process is still running
                process.terminate()
                self.progress_queue.put(("log", f"Terminating conversion for {video_file}.\n"))
        self.current_processes.clear() # Clear the dictionary after attempting to terminate all processes

    def _conversion_worker(self, input_dir, output_dir, video_codec, audio_codec, video_bitrate, output_format, delete_input, fallback_bitrate, cap_dynamic_bitrate, concurrent_conversions, start_time, verbose_logging):

        if not input_dir or not output_dir:
            self.progress_queue.put(("log", "Error: Input and output folders must be selected.\n"))
            self.progress_queue.put(("conversion_finished", None))
            return

        video_files = find_video_files(input_dir)
        if not video_files:
            self.progress_queue.put(("log", f"No video files found in {input_dir}\n"))
            self.progress_queue.put(("conversion_finished", None))
            return

        self.progress_queue.put(("log", f"Found {len(video_files)} video files to convert.\n"))
        self.progress_queue.put(("progress_max", len(video_files)))
        self.total_files_count = len(video_files) # Set total files count here

        # Use a ThreadPoolExecutor for concurrent conversions
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_conversions) as executor:
            # Store futures to track progress and results
            futures = {
                executor.submit(self._convert_single_file,
                                video_file,
                                output_dir,
                                video_codec,
                                audio_codec,
                                video_bitrate,
                                output_format,
                                delete_input,
                                fallback_bitrate,
                                cap_dynamic_bitrate,
                                self.cancel_event,
                                verbose_logging): video_file
                for video_file in video_files
            }

            completed_count = 0
            self.completed_files_count = 0 # Initialize for ETA calculation
            self.conversion_start_times = {} # To store start time of each file conversion

            for video_file in video_files:
                self.conversion_start_times[video_file] = time.time()
                futures[executor.submit(self._convert_single_file,
                                        video_file,
                                        output_dir,
                                        video_codec,
                                        audio_codec,
                                        video_bitrate,
                                        output_format,
                                        delete_input,
                                        fallback_bitrate,
                                        cap_dynamic_bitrate,
                                        self.cancel_event,
                                        verbose_logging)] = video_file

            for future in concurrent.futures.as_completed(futures):
                if self.cancel_event.is_set():
                    self.progress_queue.put(("log", "Conversion canceled.\n"))
                    # Attempt to cancel any pending futures
                    for f in futures:
                        f.cancel()
                    break

                video_file = futures[future]
                try:
                    result = future.result() # This will re-raise any exception from _convert_single_file
                    if result["success"]:
                        self.progress_queue.put(("log", f"Successfully converted {video_file} to {result["output_filepath"]}.\n"))
                        self.completed_files_count += 1
                        elapsed_time_for_file = time.time() - self.conversion_start_times.get(video_file, time.time())
                        avg_time_per_file = (time.time() - start_time) / self.completed_files_count
                        remaining_files = self.total_files_count - self.completed_files_count
                        eta_seconds = avg_time_per_file * remaining_files
                        self.progress_queue.put(("eta", eta_seconds))

                        if delete_input:
                            try:
                                os.remove(video_file)
                                self.progress_queue.put(("log", f"Deleted input file: {video_file}\n"))
                            except OSError as e:
                                self.progress_queue.put(("log", f"Error deleting file {video_file}: {e}\n"))
                    else:
                        self.progress_queue.put(("log", f"Error converting {video_file}: {result["error"]}\n"))
                except concurrent.futures.CancelledError:
                    self.progress_queue.put(("log", f"Conversion of {video_file} was cancelled.\n"))
                except Exception as exc:
                    self.progress_queue.put(("log", f"Error processing {video_file}: {exc}\n"))
                finally:
                    completed_count += 1
                    self.progress_queue.put(("progress", completed_count))

        self.progress_queue.put(("log", "All conversions complete.\n"))
        self.progress_queue.put(("conversion_finished", None))

    def _convert_single_file(self, video_file, output_dir, video_codec, audio_codec, video_bitrate, output_format, delete_input, fallback_bitrate, cap_dynamic_bitrate, cancel_event, verbose_logging):
        output_filepath = get_output_filepath(video_file, output_dir, output_format)
        command = build_ffmpeg_command(
            video_file,
            output_filepath,
            video_codec,
            audio_codec,
            video_bitrate,
            fallback_bitrate,
            cap_dynamic_bitrate,
        )
        
        log_message = f"Converting {video_file} to {output_filepath} with video codec: {video_codec}, audio codec: {audio_codec}, bitrate: {video_bitrate}, format: {output_format}.\n"
        self.progress_queue.put(("log", log_message))

        process = execute_ffmpeg_command(command, verbose_logging)
        # Store the process object for potential termination
        self.current_processes[video_file] = process

        stdout, stderr = process.communicate()

        if verbose_logging:
            if stdout:
                self.progress_queue.put(("log", f"FFmpeg STDOUT for {video_file}:\n{stdout}\n"))
            if stderr:
                self.progress_queue.put(("log", f"FFmpeg STDERR for {video_file}:\n{stderr}\n"))

        # Remove process from tracking after it completes
        if video_file in self.current_processes:
            del self.current_processes[video_file]

        if cancel_event.is_set():
            return {"success": False, "error": "Conversion cancelled", "output_filepath": output_filepath}

        if process.returncode == 0:
            actual_details = get_file_details(output_filepath)
            details_log = (
                f"  Actual Output Details:\n"
                f"    Format: {actual_details["format"]}\n"
                f"    Resolution: {actual_details["resolution"]}\n"
                f"    Video Codec: {actual_details["video_codec"]}\n"
                f"    Audio Codec: {actual_details["audio_codec"]}\n"
                f"    Bitrate: {actual_details["bitrate"]}\n"
            )
            self.progress_queue.put(("log", details_log))
            return {"success": True, "output_filepath": output_filepath}
        else:
            return {"success": False, "error": stderr, "output_filepath": output_filepath}

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
                elif message_type == "eta":
                    hours, remainder = divmod(int(data), 3600)
                    minutes, seconds = divmod(remainder, 60)
                    self.eta_label.config(text=f"ETA: {hours:02}:{minutes:02}:{seconds:02}")
                    self.update_idletasks()                
                elif message_type == "conversion_finished":
                    self._toggle_widgets(True)
                    self.cancel_button.config(state=tk.DISABLED)
                    return # Exit the update loop as conversions are finished
        except queue.Empty:
            pass

        if self.thread.is_alive():
            self.after(100, self._update_progress)
        else:
            # If thread is not alive and conversion_finished wasn't sent (e.g., early exit)
            self._toggle_widgets(True)
            self.cancel_button.config(state=tk.DISABLED)

if __name__ == "__main__":
    root = tk.Tk()
    root.title("FFMPEG Bulk Converter")
    root.geometry("1000x750")
    app = ConverterApp(root)
    root.mainloop()