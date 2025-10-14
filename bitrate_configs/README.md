# Bitrate Configuration Files

This directory (`bitrate_configs`) contains JSON files that define the bitrate mappings used by the FFMPEG Bulk Converter application for its "Optimized" bitrate conversion feature. Each JSON file represents a different quality profile, allowing users to easily switch between various bitrate settings.

## File Structure

Each JSON file in this directory follows a specific structure:

```json
{
    "<resolution>": {
        "<input_video_codec>": {
            "<output_video_codec>": "<bitrate_value>"
        }
    }
}
```

*   `<resolution>`: The resolution of the video (e.g., "720p", "1080p", "1440p", "2160p").
*   `<input_video_codec>`: The codec of the original input video (e.g., "h264", "hevc", "av1").
*   `<output_video_codec>`: The target codec for the output video (e.g., "h264", "hevc", "av1").
*   `<bitrate_value>`: The recommended bitrate for the given conversion, specified as a string (e.g., "5M" for 5 Mbps).

## Quality Profiles

The following quality profiles are provided:

*   `max_quality.json`: Highest quality, with bitrates scaled up from the high-quality profile.
*   `high_quality.json`: A reference high-quality profile. This is the base for scaling other profiles.
*   `balanced_quality.json`: A balanced quality profile, with bitrates scaled down from the high-quality profile.
*   `low_quality.json`: A lower quality profile, with further reduced bitrates.
*   `min_quality.json`: The lowest quality profile, with significantly reduced bitrates (subject to a minimum of 1 Mbps).

## Resolution Matching

When using the "Optimized" bitrate setting, the application will attempt to match the input video's resolution to the resolutions defined in the selected quality profile's JSON file.

If the input video's resolution does not exactly match a resolution in the configuration file, the application will automatically round **up** to the nearest supported resolution. For example, if the supported resolutions are "720p" and "1080p", an input video with a resolution of "900p" will be treated as "1080p" for the purpose of selecting the appropriate bitrate.

If the input video's resolution is higher than the highest resolution defined in the configuration file, the application will use the highest defined resolution.

## Generating and Customizing Bitrate Profiles

The `generate_bitrate_configs.py` script is used to create and update these JSON configuration files. It uses `high_quality.json` as a base and applies scaling factors to generate the other quality profiles.

### How to Use `generate_bitrate_configs.py`

1.  **Review `high_quality.json`:** If you wish to customize the base bitrate settings, edit the `bitrate_configs/high_quality.json` file directly.
2.  **Modify Scaling Factors (Optional):** If you want to adjust how the other quality profiles are scaled, you can edit the `quality_profiles` dictionary within `generate_bitrate_configs.py`.
3.  **Run the Script:** Execute the script from the project's root directory:
    ```bash
    python generate_bitrate_configs.py
    ```
    This will regenerate all the `*.json` files in the `bitrate_configs` directory based on your `high_quality.json` and any modified scaling factors.

### Adding New Quality Profiles

To add a new quality profile:

1.  **Edit `generate_bitrate_configs.py`:** Add a new entry to the `quality_profiles` dictionary with your desired profile name and scaling factor.
2.  **Run the Script:** Execute `python generate_bitrate_configs.py` to generate the new JSON file.
3.  **Update `converter_app.py` (GUI):** Add the new profile name to the `quality_profiles` list in the `ConverterApp` class to make it available in the GUI dropdown.

By following these steps, you can easily manage and customize the bitrate settings for your video conversions.