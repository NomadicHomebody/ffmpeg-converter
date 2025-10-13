import os
import subprocess
import json

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

    if video_bitrate == "dynamic":
        bitrate = get_video_bitrate(input_file)
        if bitrate:
            if cap_dynamic_bitrate:
                try:
                    dynamic_bitrate_int = int(bitrate)
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


def execute_ffmpeg_command(command: list[str]) -> subprocess.Popen:
    """
    Executes an ffmpeg command.

    Args:
        command: The ffmpeg command to execute, as a list of strings.
    
    Returns:
        The Popen object for the running process.
    """
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
