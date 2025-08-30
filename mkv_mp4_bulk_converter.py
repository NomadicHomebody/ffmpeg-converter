"""Bulk MKV to MP4 Converter CLI

Provides a command-line interface for batch conversion of MKV files to MP4 format.

Usage Examples:
    python mkv-mp4-bulkConverter.py /path/to/input_folder
    python mkv-mp4-bulkConverter.py /input --dry-run --verbose --progress

Args:
    input_folder (str): Path to the folder containing MKV files.

Options:
    --dry-run      : Simulate conversion without making changes.
    --verbose      : Enable verbose output.
    --progress     : Show progress reporting.
    --help         : Show this message and exit.

Raises:
    click.BadParameter: If input_folder is not provided or invalid.
"""

import os
import sys
import click
import structlog

def find_mkv_files(input_folder: str) -> list[str]:
    """Recursively scan the input folder and return absolute paths to .mkv files only.

    Args:
        input_folder (str): Path to the folder to scan.

    Returns:
        list[str]: List of absolute paths to .mkv files.

    Raises:
        ValueError: If input_folder does not exist or is not a directory.
    """
    import os

    if not os.path.isdir(input_folder):
        raise ValueError(f"Input folder '{input_folder}' does not exist or is not a directory.")

    mkv_files: list[str] = []
    for root, dirs, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(".mkv") or file.lower().endswith(".mp4"):
                abs_path = os.path.abspath(os.path.join(root, file))
                abs_path_quoted = abs_path
                mkv_files.append(abs_path_quoted)
    logger.info("find_mkv_files loaded and returning", mkv_files=mkv_files)
    return mkv_files

def build_ffmpeg_command(
    input_path: str,
    output_path: str,
    crf: int = 28
) -> list[str]:
    """Construct the FFmpeg command for MKV to MP4 conversion.

    Args:
        input_path (str): Absolute path to the input .mkv file.
        output_path (str): Absolute path to the output .mp4 file.
        crf (int, optional): Constant Rate Factor for libx265. Defaults to 28.

    Returns:
        list[str]: FFmpeg command as a list of arguments.

    Raises:
        ValueError: If input_path or output_path is empty.
    """
    def quote_if_needed(path: str) -> str:
        """Wrap path in double quotes if it contains spaces.

        Args:
            path (str): File path.

        Returns:
            str: Quoted path if needed.
        """
        return f'"{path}"' if " " in path else path

    if not input_path or not output_path:
        raise ValueError("Both input_path and output_path must be provided.")

    return [
        "ffmpeg",
        "-i", input_path,
        "-c:v", "hevc_nvenc",
        "-crf", str(crf),
        "-c:a", "aac",
        "-b:a", "192k",
        output_path
    ]

def redact_sensitive_fields(logger, method_name, event_dict):
    """Redact sensitive fields from log event dict.

    Args:
        logger: Logger instance.
        method_name: Logging method name.
        event_dict: Log event dictionary.

    Returns:
        dict: Event dict with sensitive fields redacted.
    """
    for key in ("password", "api_key", "token"):
        if key in event_dict:
            event_dict[key] = "***REDACTED***"
    return event_dict

structlog.configure(
    processors=[
        redact_sensitive_fields,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()

@click.command(
    context_settings={"help_option_names": ["-h", "--help"]},
    help="Bulk MKV to MP4 Converter CLI.\n\n"
         "Required argument: input_folder (path to MKV files).\n"
         "Optional flags: --dry-run, --verbose, --progress.\n\n"
         "Examples:\n"
         "  python mkv-mp4-bulkConverter.py /path/to/input_folder\n"
         "  python mkv-mp4-bulkConverter.py /input --dry-run --verbose --progress"
)
@click.argument(
    "input_folder",
    type=click.Path(exists=True, file_okay=False, readable=True),
    metavar="<input_folder>",
)
@click.option(
    "--dry-run",
    is_flag=True,
    default=False,
    help="Simulate conversion without making changes."
)
@click.option(
    "--verbose",
    is_flag=True,
    default=False,
    help="Enable verbose output."
)
@click.option(
    "--progress",
    is_flag=True,
    default=False,
    help="Show progress reporting."
)
def main(
    input_folder: str,
    dry_run: bool,
    verbose: bool,
    progress: bool
) -> None:
    """Entry point for the bulk MKV to MP4 converter CLI.

    Args:
        input_folder (str): Path to the folder containing MKV files.
        dry_run (bool): If True, simulate conversion.
        verbose (bool): If True, enable verbose output.
        progress (bool): If True, show progress reporting.

    Returns:
        None

    Raises:
        click.BadParameter: If input_folder is not valid.
    """

    import subprocess

    logger.info("About to call find_mkv_files", input_folder=input_folder)
    mkv_files: list[str] = find_mkv_files(input_folder)
    if not mkv_files:
        logger.warning("No .mkv files found in the specified folder.", input_folder=input_folder)
        return

    if progress:
        try:
            from tqdm import tqdm
        except ImportError as imp_err:
            logger.error("tqdm is required for progress reporting.", error=str(imp_err))
            sys.exit(1)
        file_iter = tqdm(mkv_files, desc="Converting files", unit="file", ncols=80)
    else:
        file_iter = mkv_files

    for idx, mkv_path in enumerate(file_iter, 1):
        mp4_path = mkv_path[:-4] + "_.mp4"
        cmd = build_ffmpeg_command(mkv_path, mp4_path)
        status_msg = f"[{idx}/{len(mkv_files)}] {os.path.basename(mkv_path)}"
        if dry_run:
            logger.info("Dry run: Would run ffmpeg command.", status_msg=status_msg, cmd=cmd)
            continue

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("Conversion successful.", status_msg=status_msg, mkv_path=mkv_path, mp4_path=mp4_path)
                try:
                    os.remove(mkv_path)
                except OSError as e:
                    logger.warning("Could not remove MKV file after conversion.", status_msg=status_msg, mkv_path=mkv_path, error=str(e))
            else:
                logger.error("Error converting MKV file.", status_msg=status_msg, mkv_path=mkv_path, stderr=result.stderr)
        except subprocess.SubprocessError as exc:
            logger.error("Subprocess error during conversion.", status_msg=status_msg, mkv_path=mkv_path, exc_info=True, error=str(exc))
        except Exception as exc:
            logger.exception("Unhandled exception during conversion.", status_msg=status_msg, mkv_path=mkv_path)

if __name__ == "__main__":
    main()
