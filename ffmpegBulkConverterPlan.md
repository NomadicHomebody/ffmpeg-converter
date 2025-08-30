
Problem Statement: I need to convert .mkv files to .mp4 files in order to guarantee support when attempting to run videos on my Jellyfin clients. I want a straight forward python script named `mkv-mp4-bulkConverter.py` that can take a folder containing .mkv files (along with potential images, text and other extra files) and convert all of the .mkv files into .mp4 files. This script should also delete (or replace) all of the .mkv files so only the .mp4 files remain without modifying/deleting/replacing any of the other extra non-video type files.

Requirements:
- Script takes in folder containing .mkv files as command line argument
- Script only modifies .mkv files by converting them to .mp4 format via ffmpeg
- file conversion parameters:
    - File Format: .mp4
    - Video Codec: HEVC (libx265)
    - Audio Codec: .aac
    - Audio Bitrate: 192k
    - Any other potential properties should be driven by the notion of maintain quality while keeping video size as small as possible
    - Reference to base for potential command to use for converting .mkv to .mp4:
        ```
        ffmpeg -i "D:\Library\JellyFin\Shows\Dragon Ball Super\test\[Yameii] Dragon Ball Super - S03E01 [English Dub] [CR WEB-DL 1080p] [85A02753].mkv" -c:v libx265 -crf 28 -c:a aac -b:a 192k output.mp4
        ```
- If reasonalbe to implement: Script displays status and update details (i.e. number of files to process, number of files processed/remaining to process, time remaining estimate, progress bar & percentage)