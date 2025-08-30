"""Unit and integration tests for mkv_mp4_bulk_converter.py.

Covers file discovery, command construction, conversion logic, error handling, and logging.
All tests are written to fail initially (TDD).

"""
import os
import pytest
import tempfile
import shutil
from unittest import mock
from mkv_mp4_bulk_converter import find_mkv_files, build_ffmpeg_command

@pytest.fixture
def temp_dir() -> str:
    """Create a temporary directory for test files.

    Returns:
        str: Path to the temporary directory.

    Raises:
        OSError: If temp directory cannot be created.
    """
    dirpath = tempfile.mkdtemp()
    yield dirpath
    shutil.rmtree(dirpath)

def test_find_mkv_files_happy_path(temp_dir: str) -> None:
    """Test find_mkv_files returns correct .mkv files.

    Args:
        temp_dir (str): Temporary directory path.

    Raises:
        AssertionError: If discovered files do not match expected.
    """
    mkv1 = os.path.join(temp_dir, "video1.mkv")
    mkv2 = os.path.join(temp_dir, "video2.MKV")
    open(mkv1, "w").close()
    open(mkv2, "w").close()
    open(os.path.join(temp_dir, "not_video.txt"), "w").close()
    files = find_mkv_files(temp_dir)
    assert set(files) == {os.path.abspath(mkv1), os.path.abspath(mkv2)}

def test_find_mkv_files_empty_input(temp_dir: str) -> None:
    """Test find_mkv_files with empty directory.

    Args:
        temp_dir (str): Temporary directory path.

    Raises:
        AssertionError: If result is not empty list.
    """
    files = find_mkv_files(temp_dir)
    assert files == []

def test_find_mkv_files_invalid_dir() -> None:
    """Test find_mkv_files raises ValueError for invalid directory.

    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError):
        find_mkv_files("/nonexistent/path")

def test_build_ffmpeg_command_happy_path() -> None:
    """Test build_ffmpeg_command returns correct command list.

    Raises:
        AssertionError: If command does not match expected.
    """
    cmd = build_ffmpeg_command("input.mkv", "output.mp4")
    assert cmd[0] == "ffmpeg"
    assert "-i" in cmd and "input.mkv" in cmd
    assert "output.mp4" in cmd

def test_build_ffmpeg_command_missing_args() -> None:
    """Test build_ffmpeg_command raises ValueError for missing args.

    Raises:
        AssertionError: If ValueError is not raised.
    """
    with pytest.raises(ValueError):
        build_ffmpeg_command("", "output.mp4")
    with pytest.raises(ValueError):
        build_ffmpeg_command("input.mkv", "")

def test_main_dry_run_logging(monkeypatch) -> None:
    """Test main dry-run logs correct info and redacts sensitive fields.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Raises:
        AssertionError: If log output is incorrect or not redacted.
    """
    import mkv_mp4_bulk_converter
    logs = []
    def fake_logger_info(msg, **kwargs):
        logs.append(kwargs)
    monkeypatch.setattr(mkv_mp4_bulk_converter.logger, "info", fake_logger_info)
    monkeypatch.setattr(mkv_mp4_bulk_converter, "find_mkv_files", lambda x: ["file1.mkv"])
    monkeypatch.setattr(mkv_mp4_bulk_converter, "build_ffmpeg_command", lambda x, y: ["ffmpeg", "-i", x, y])
    mkv_mp4_bulk_converter.main.callback("input", True, False, False)
    assert any("cmd" in log for log in logs)
    # Simulate sensitive field
    logs.clear()
    fake_logger_info("msg", api_key="secret", token="secret")
    assert all(val == "***REDACTED***" for k, val in logs[0].items() if k in ("api_key", "token"))

def test_main_subprocess_failure(monkeypatch) -> None:
    """Test main handles subprocess failure and logs error.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Raises:
        AssertionError: If error is not logged.
    """
    import mkv_mp4_bulk_converter
    errors = []
    def fake_logger_error(msg, **kwargs):
        errors.append(kwargs)
    monkeypatch.setattr(mkv_mp4_bulk_converter.logger, "error", fake_logger_error)
    monkeypatch.setattr(mkv_mp4_bulk_converter, "find_mkv_files", lambda x: ["file1.mkv"])
    monkeypatch.setattr(mkv_mp4_bulk_converter, "build_ffmpeg_command", lambda x, y: ["ffmpeg", "-i", x, y])
    class FakeResult:
        returncode = 1
        stderr = "fail"
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    mkv_mp4_bulk_converter.main.callback("input", False, False, False)
    assert any("stderr" in err for err in errors)

def test_main_permission_error(monkeypatch) -> None:
    """Test main handles permission error when removing file.

    Args:
        monkeypatch: Pytest monkeypatch fixture.

    Raises:
        AssertionError: If warning is not logged.
    """
    import mkv_mp4_bulk_converter
    warnings = []
    def fake_logger_warning(msg, **kwargs):
        warnings.append(kwargs)
    monkeypatch.setattr(mkv_mp4_bulk_converter.logger, "warning", fake_logger_warning)
    monkeypatch.setattr(mkv_mp4_bulk_converter, "find_mkv_files", lambda x: ["file1.mkv"])
    monkeypatch.setattr(mkv_mp4_bulk_converter, "build_ffmpeg_command", lambda x, y: ["ffmpeg", "-i", x, y])
    class FakeResult:
        returncode = 0
    monkeypatch.setattr("subprocess.run", lambda *a, **kw: FakeResult())
    monkeypatch.setattr("os.remove", mock.Mock(side_effect=PermissionError("denied")))
    mkv_mp4_bulk_converter.main.callback("input", False, False, False)
    assert any("error" in warn for warn in warnings)
def test_build_ffmpeg_command_with_spaces() -> None:
    """Test build_ffmpeg_command robustly quotes paths with spaces.

    Raises:
        AssertionError: If command does not quote paths with spaces.
    """
    input_path = "C:/Users/Test Folder/input file.mkv"
    output_path = "C:/Users/Test Folder/output file.mp4"
    cmd = build_ffmpeg_command(input_path, output_path)
    # ffmpeg expects quoted paths for spaces on Windows
    assert '"C:/Users/Test Folder/input file.mkv"' in cmd
    assert '"C:/Users/Test Folder/output file.mp4"' in cmd