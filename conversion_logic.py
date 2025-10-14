import os
import subprocess
import json

OPTIMIZED_BITRATE_MAP = {}

def load_optimized_bitrate_map(quality_profile: str) -> dict:
    global OPTIMIZED_BITRATE_MAP
    file_name = quality_profile.lower().replace(" ", "_") + ".json"
    config_path = os.path.join("bitrate_configs", file_name)
    try:
        with open(config_path, "r") as f:
            OPTIMIZED_BITRATE_MAP = json.load(f)
        return OPTIMIZED_BITRATE_MAP
    except FileNotFoundError:
        print(f"Error: Bitrate config file not found: {config_path}. Optimized bitrate feature may be unavailable or use default.")
        OPTIMIZED_BITRATE_MAP = {}
        return {}
    except json.JSONDecodeError:
        print(f"Error: Could not decode bitrate config file: {config_path}. Check file format.")
        OPTIMIZED_BITRATE_MAP = {}
        return {}

def find_video_files(directory: str) -> list[str]:
    """
    Scans a directory for video files (non-recursively).

    Args:
        directory: The directory to scan.

    Returns:
        A list of absolute paths to video files.
    """
    if not os.path.isdir(directory):
        raise ValueError(f"Directory not found: {directory}")

    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.wmv', '.flv', '.webm']
    video_files = []
    for item in os.listdir(directory):
        if os.path.isfile(os.path.join(directory, item)):
            _, ext = os.path.splitext(item)
            if ext.lower() in video_extensions:
                video_files.append(os.path.abspath(os.path.join(directory, item)))
    return video_files


def get_video_bitrate(input_file: str) -> str | None:
    """
    Gets the bitrate of a video file using ffprobe.

    Args:
        input_file: The path to the input video file.

    Returns:
        The bitrate of the video file as a string, or None if it cannot be determined.
    """
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        input_file,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        if "format" in data and "bit_rate" in data["format"]:
            return data["format"]["bit_rate"]
        else:
            return None
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None

def _get_video_details(input_file: str) -> dict | None:
    """
    Gets video details (resolution, codec) of a video file using ffprobe.
    The resolution is rounded up to the nearest supported resolution in the bitrate map.

    Args:
        input_file: The path to the input video file.

    Returns:
        A dictionary containing 'resolution' and 'codec_name', or None if it cannot be determined.
    """
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_streams",
        input_file,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                width = stream.get("width")
                height = stream.get("height")
                codec_name = stream.get("codec_name")
                if width and height and codec_name:
                    # Get supported resolutions from the global map
                    supported_resolutions = sorted([int(r.replace('p', '')) for r in OPTIMIZED_BITRATE_MAP.keys()])
                    
                    if not supported_resolutions:
                        return None # No supported resolutions loaded

                    # Find the best matching resolution
                    best_res = supported_resolutions[-1] # Default to highest if above all
                    for res in supported_resolutions:
                        if height <= res:
                            best_res = res
                            break
                    
                    resolution = f"{best_res}p"
                    
                    return {"resolution": resolution, "codec_name": codec_name}
        return None
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return None

def get_file_details(file_path: str) -> dict:
    """
    Gets comprehensive details of a media file using ffprobe.

    Args:
        file_path: The path to the media file.

    Returns:
        A dictionary containing details like bitrate, resolution, video codec, audio codec, and format.
        Returns default values if information cannot be retrieved.
    """
    details = {
        "bitrate": "N/A",
        "resolution": "N/A",
        "video_codec": "N/A",
        "audio_codec": "N/A",
        "format": "N/A",
    }
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        file_path,
    ]
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)

        # Get format details
        if "format" in data:
            details["format"] = data["format"].get("format_name", "N/A")
            bitrate_bps = data["format"].get("bit_rate")
            if bitrate_bps:
                details["bitrate"] = f"{int(bitrate_bps) / 1000000:.2f} Mbps"

        # Get stream details
        for stream in data.get("streams", []):
            if stream.get("codec_type") == "video":
                details["video_codec"] = stream.get("codec_name", "N/A")
                width = stream.get("width")
                height = stream.get("height")
                if width and height:
                    details["resolution"] = f"{width}x{height}"
            elif stream.get("codec_type") == "audio":
                details["audio_codec"] = stream.get("codec_name", "N/A")
                # Assuming one audio stream for simplicity, could be extended for multiple

    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        pass # Return default N/A values on error

    return details


def _get_optimized_bitrate(input_file: str, output_video_codec: str, fallback_bitrate: str) -> str:
    """
    Determines the optimized bitrate based on input video details and a mapping table.

    Args:
        input_file: The path to the input video file.
        output_video_codec: The target output video codec.
        fallback_bitrate: The bitrate to use if no optimized mapping is found.

    Returns:
        The optimized bitrate as a string (e.g., "5M"), or the fallback bitrate.
    """
    video_details = _get_video_details(input_file)
    if not video_details:
        return fallback_bitrate

    resolution = video_details.get("resolution")
    input_codec = video_details.get("codec_name")

    if resolution and input_codec and resolution in OPTIMIZED_BITRATE_MAP:
        resolution_map = OPTIMIZED_BITRATE_MAP[resolution]
        if input_codec in resolution_map:
            codec_map = resolution_map[input_codec]
            if output_video_codec in codec_map:
                return codec_map[output_video_codec]

    return fallback_bitrate


def build_ffmpeg_command(
    input_file: str,
    output_file: str,
    video_codec: str,
    audio_codec: str,
    video_bitrate: str,
    fallback_bitrate: str,
    cap_dynamic_bitrate: bool,
) -> list[str]:
    """
    Constructs the ffmpeg command as a list of strings.

    Args:
        input_file: The path to the input video file.
        output_file: The path to the output video file.
        video_codec: The video codec to use.
        audio_codec: The audio codec to use.
        video_bitrate: The video bitrate to use.
        fallback_bitrate: The bitrate to use if optimized mapping is not found.
        cap_dynamic_bitrate: Whether to cap the optimized bitrate at the fallback bitrate.

    Returns:
        A list of strings representing the ffmpeg command.
    """
    if not input_file or not output_file:
        raise ValueError("Input and output files must be specified.")

    command = [
        "ffmpeg",
        "-i",
        input_file,
        "-c:v",
        video_codec,
        "-c:a",
        audio_codec,
    ]

    if video_bitrate == "optimized":
        target_bitrate = _get_optimized_bitrate(input_file, video_codec, fallback_bitrate)
        if cap_dynamic_bitrate:
            try:
                # Convert to common unit (bits) for comparison
                target_bitrate_val = int(target_bitrate.upper().replace("M", "000000").replace("K", "000"))
                fallback_bitrate_val = int(fallback_bitrate.upper().replace("M", "000000").replace("K", "000"))
                if target_bitrate_val > fallback_bitrate_val:
                    target_bitrate = fallback_bitrate
            except ValueError:
                pass  # Handle cases where bitrate strings are not perfectly parsable
        command.extend(["-b:v", target_bitrate])
    elif video_bitrate == "dynamic":
        bitrate = get_video_bitrate(input_file)
        if bitrate:
            if cap_dynamic_bitrate:
                try:
                    dynamic_bitrate_int = int(bitrate.upper().replace("M", "000000").replace("K", "000"))
                    fallback_bitrate_int = int(fallback_bitrate.upper().replace("M", "000000").replace("K", "000"))
                    if dynamic_bitrate_int > fallback_bitrate_int:
                        bitrate = fallback_bitrate
                except ValueError:
                    pass  # Could not convert bitrates to int for comparison
            command.extend(["-b:v", bitrate])
        else:
            command.extend(["-b:v", fallback_bitrate])
    else:
        command.extend(["-b:v", video_bitrate])

    command.append(output_file)

    return command


def execute_ffmpeg_command(command: list[str], verbose_logging: bool) -> subprocess.Popen:
    """
    Executes an ffmpeg command.

    Args:
        command: The ffmpeg command to execute, as a list of strings.
        verbose_logging: If True, ffmpeg will output verbose logs.
    
    Returns:
        The Popen object for the running process.
    """
    if not verbose_logging:
        # Insert -v quiet after ffmpeg if not verbose
        command.insert(1, "-v")
        command.insert(2, "quiet")

    return subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)


def get_output_filepath(input_file: str, output_dir: str, output_format: str) -> str:
    """
    Determines the output file path based on the naming convention.

    Args:
        input_file: The path to the input video file.
        output_dir: The path to the output directory.
        output_format: The output file format (e.g., "mp4").

    Returns:
        The path to the output video file.
    """
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_filename = f"z_{base_filename}.{output_format}"
    output_filepath = os.path.join(output_dir, output_filename)

    counter = 1
    while os.path.exists(output_filepath):
        output_filename = f"z_{counter}_{base_filename}.{output_format}"
        output_filepath = os.path.join(output_dir, output_filename)
        counter += 1

    return output_filepath
