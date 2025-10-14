import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import shutil
import os
import concurrent.futures
import functools
import time

from conversion_logic import find_video_files, build_ffmpeg_command, execute_ffmpeg_command, get_output_filepath, get_file_details, load_optimized_bitrate_map, get_video_resolution_for_optimization, get_optimized_bitrate

class ConverterApp(ttk.Frame):
    def __init__(self, master):
        super().__init__(master, padding="10")
        self.grid(row=0, column=0, sticky="nsew")
        master.columnconfigure(0, weight=1)
        master.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0) # folder_frame row
        self.rowconfigure(1, weight=0) # options_frame row
        self.rowconfigure(2, weight=1) # progress_log_frame row
        self.rowconfigure(3, weight=0) # start_button row
        self.rowconfigure(4, weight=0) # cancel_button row

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
        bitrates = ["dynamic", "optimized"] + [f"{i}M" for i in range(1, 10, 1)] + [f"{i}M" for i in range(10, 251, 5)]
        ttk.Combobox(options_frame, textvariable=self.video_bitrate, values=bitrates, state="readonly").grid(row=3, column=1, sticky="ew")

        # Bitrate Quality Profile
        ttk.Label(options_frame, text="Bitrate Quality Profile (optimized): ").grid(row=4, column=0, sticky=tk.W)
        self.bitrate_quality_profile = tk.StringVar(value="Balanced Quality")
        quality_profiles = ["Max Quality", "High Quality", "Balanced Quality", "Low Quality", "Min Quality"]
        ttk.Combobox(options_frame, textvariable=self.bitrate_quality_profile, values=quality_profiles, state="readonly").grid(row=4, column=1, sticky="ew")

        # Delete input file checkbox
        self.delete_input = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Delete input files after successful conversion", variable=self.delete_input).grid(row=5, column=0, columnspan=2, sticky=tk.W)

        # Fallback Bitrate
        ttk.Label(options_frame, text="Fallback Bitrate (if dynamic fails):").grid(row=6, column=0, sticky=tk.W)
        self.fallback_bitrate = tk.StringVar(value="20M")
        ttk.Entry(options_frame, textvariable=self.fallback_bitrate).grid(row=6, column=1, sticky="ew")

        # Cap dynamic bitrate checkbox
        self.cap_dynamic_bitrate = tk.BooleanVar()
        ttk.Checkbutton(options_frame, text="Cap dynamic bitrate at fallback bitrate", variable=self.cap_dynamic_bitrate).grid(row=7, column=0, columnspan=2, sticky=tk.W)

        # Concurrent Conversions
        ttk.Label(options_frame, text="Concurrent Conversions:").grid(row=8, column=0, sticky=tk.W)
        self.concurrent_conversions = tk.IntVar(value=2)
        self.concurrent_conversions_spinbox = ttk.Spinbox(options_frame, from_=1, to=32, textvariable=self.concurrent_conversions, state="readonly")
        self.concurrent_conversions_spinbox.grid(row=8, column=1, sticky="ew")

        # Verbose Logging
        self.verbose_logging = tk.BooleanVar(value=False)
        ttk.Checkbutton(options_frame, text="Enable Verbose Logging", variable=self.verbose_logging).grid(row=9, column=0, columnspan=2, sticky=tk.W)

        # Progress and Log frame
        progress_log_frame = ttk.LabelFrame(self, text="Progress and Log", padding="10")
        progress_log_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        progress_log_frame.columnconfigure(0, weight=1)
        progress_log_frame.rowconfigure(0, weight=1)

        self.log_area = tk.Text(progress_log_frame, height=10)
        self.log_area.grid(row=0, column=0, sticky="nsew")

        # Configure log tags for color coding
        self.log_area.tag_configure("info", foreground="black")
        self.log_area.tag_configure("success", foreground="green")
        self.log_area.tag_configure("error", foreground="red")
        self.log_area.tag_configure("warning", foreground="orange")
        self.log_area.tag_configure("timestamp", foreground="gray")
        self.log_area.tag_configure("details", foreground="blue")

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
        self.conversion_start_times = {}
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
            self.bitrate_quality_profile.get(), # Pass bitrate_quality_profile
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
                self.progress_queue.put(("log", ("warning", f"Terminating conversion for {video_file}.")))
        self.current_processes.clear() # Clear the dictionary after attempting to terminate all processes

    def _conversion_worker(self, input_dir, output_dir, video_codec, audio_codec, video_bitrate, bitrate_quality_profile, output_format, delete_input, fallback_bitrate, cap_dynamic_bitrate, concurrent_conversions, start_time, verbose_logging):

        # Load the appropriate optimized bitrate map based on user selection
        load_optimized_bitrate_map(bitrate_quality_profile)

        if not input_dir or not output_dir:
            self.progress_queue.put(("log", ("error", "Error: Input and output folders must be selected.")))
            self.progress_queue.put(("conversion_finished", None))
            return

        video_files = find_video_files(input_dir)
        if not video_files:
            self.progress_queue.put(("log", ("warning", f"No video files found in {input_dir}")))
            self.progress_queue.put(("conversion_finished", None))
            return

        self.progress_queue.put(("log", ("info", f"Found {len(video_files)} video files to convert.")))
        self.progress_queue.put(("progress_max", len(video_files)))
        self.total_files_count = len(video_files) # Set total files count here

        # Adjust the number of workers to not exceed the number of files
        num_workers = min(concurrent_conversions, self.total_files_count)

        # Use a ThreadPoolExecutor for concurrent conversions
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
            # Store futures to track progress and results
            futures = {}
            for video_file in video_files:
                self.conversion_start_times[video_file] = time.time()
                future = executor.submit(self._convert_single_file,
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
                                        verbose_logging)
                futures[future] = video_file

            completed_count = 0
            self.completed_files_count = 0 # Initialize for ETA calculation

            for future in concurrent.futures.as_completed(futures):
                if self.cancel_event.is_set():
                    self.progress_queue.put(("log", ("warning", "Conversion canceled.")))
                    # Attempt to cancel any pending futures
                    for f in futures:
                        f.cancel()
                    break

                video_file = futures[future]
                try:
                    result = future.result() # This will re-raise any exception from _convert_single_file
                    if result["success"]:
                        self.progress_queue.put(("log", ("success", f"Successfully converted {video_file} to {result["output_filepath"]}.")))
                        self.completed_files_count += 1
                        elapsed_time_for_file = time.time() - self.conversion_start_times.get(video_file, time.time())
                        avg_time_per_file = (time.time() - start_time) / self.completed_files_count
                        remaining_files = self.total_files_count - self.completed_files_count
                        eta_seconds = avg_time_per_file * remaining_files
                        self.progress_queue.put(("eta", eta_seconds))

                        if delete_input:
                            try:
                                os.remove(video_file)
                                self.progress_queue.put(("log", ("info", f"Deleted input file: {video_file}")))
                            except OSError as e:
                                self.progress_queue.put(("log", ("error", f"Error deleting file {video_file}: {e}")))
                    else:
                        self.progress_queue.put(("log", ("error", f"Error converting {video_file}: {result["error"]}")))
                except concurrent.futures.CancelledError:
                    self.progress_queue.put(("log", ("warning", f"Conversion of {video_file} was cancelled.")))
                except Exception as exc:
                    self.progress_queue.put(("log", ("error", f"Error processing {video_file}: {exc}")))
                finally:
                    completed_count += 1
                    self.progress_queue.put(("progress", completed_count))

        self.progress_queue.put(("log", ("info", "All conversions complete.")))
        self.progress_queue.put(("conversion_finished", None))

    def _convert_single_file(self, video_file, output_dir, video_codec, audio_codec, video_bitrate, output_format, delete_input, fallback_bitrate, cap_dynamic_bitrate, cancel_event, verbose_logging):
        original_details = get_file_details(video_file)
        log_message = f"Input: {os.path.basename(video_file)} | Codec: {original_details['video_codec']}, Bitrate: {original_details['bitrate']}"
        self.progress_queue.put(("log", ("info", log_message)))

        target_bitrate = video_bitrate
        if video_bitrate == "optimized":
            optimal_resolution = "N/A"
            video_details = get_video_resolution_for_optimization(video_file)
            if video_details:
                optimal_resolution = video_details.get("resolution", "N/A")
            
            target_bitrate = get_optimized_bitrate(video_file, video_codec, fallback_bitrate)
            log_message = f"Optimized settings: Resolution: {optimal_resolution}, Bitrate: {target_bitrate}"
            self.progress_queue.put(("log", ("info", log_message)))

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
        
        log_message = f"Converting {os.path.basename(video_file)} to {os.path.basename(output_filepath)} with video codec: {video_codec}, audio codec: {audio_codec}, bitrate: {target_bitrate}, format: {output_format}."
        self.progress_queue.put(("log", ("info", log_message)))

        process = execute_ffmpeg_command(command, verbose_logging)
        # Store the process object for potential termination
        self.current_processes[video_file] = process

        stdout, stderr = process.communicate()

        if verbose_logging:
            if stdout:
                self.progress_queue.put(("log", ("details", f"FFmpeg STDOUT for {video_file}:\n{stdout.strip()}")))
            if stderr:
                self.progress_queue.put(("log", ("error", f"FFmpeg STDERR for {video_file}:\n{stderr.strip()}")))

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
                f"    Bitrate: {actual_details["bitrate"]}"
            )
            self.progress_queue.put(("log", ("details", details_log)))
            return {"success": True, "output_filepath": output_filepath}
        else:
            return {"success": False, "error": stderr, "output_filepath": output_filepath}

    def _update_progress(self):
        try:
            while True:
                message_type, data = self.progress_queue.get_nowait()
                if message_type == "log":
                    log_type = data[0]
                    message = data[1]
                    timestamp = time.strftime("[%H:%M:%S]")
                    self.log_area.insert(tk.END, f"{timestamp} ", "timestamp")
                    self.log_area.insert(tk.END, f"{message}\n", log_type)
                    self.log_area.see(tk.END) # Auto-scroll to the end
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