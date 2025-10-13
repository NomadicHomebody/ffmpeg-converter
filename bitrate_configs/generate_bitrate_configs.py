import json
import os

# This script generates bitrate configuration files for different quality profiles.
# It uses a 'high_quality.json' as a base and scales its bitrate values
# to create 'max_quality.json', 'balanced_quality.json', 'low_quality.json', and 'min_quality.json'.

def scale_bitrate(bitrate_str, scale_factor, min_bitrate_mbps=1):
    """
    Scales a given bitrate string by a scale factor, ensuring a minimum bitrate.

    Args:
        bitrate_str (str): The bitrate value as a string (e.g., "5M").
        scale_factor (float): The factor by which to scale the bitrate.
        min_bitrate_mbps (int): The minimum allowed bitrate in Mbps.

    Returns:
        str: The scaled bitrate value as a string (e.g., "6M").
    """
    if bitrate_str == "N/A":
        return bitrate_str
    try:
        # Extract numerical value, assuming 'M' for Mbps
        value = float(bitrate_str.replace('M', ''))
        scaled_value = round(value * scale_factor)
        # Ensure minimum bitrate
        if scaled_value < min_bitrate_mbps:
            scaled_value = min_bitrate_mbps
        return f"{scaled_value}M"
    except ValueError:
        # Return original string if parsing fails
        return bitrate_str

def generate_configs():
    """
    Generates bitrate configuration JSON files for various quality profiles.
    Reads 'high_quality.json' as a base and applies predefined scaling factors.
    """
    config_dir = "bitrate_configs"
    high_quality_path = os.path.join(config_dir, "high_quality.json")

    if not os.path.exists(high_quality_path):
        print(f"Error: {high_quality_path} not found. Cannot generate other configs. Please ensure high_quality.json exists.")
        return

    with open(high_quality_path, "r") as f:
        high_quality_map = json.load(f)

    # Define quality profiles and their scaling factors relative to high_quality.json
    # These factors can be adjusted to fine-tune the bitrate for each quality level.
    quality_profiles = {
        "max_quality": 1.25,       # 25% increase from high_quality
        "balanced_quality": 0.8,   # 20% decrease from high_quality
        "low_quality": 0.6,        # 40% decrease from high_quality
        "min_quality": 0.4,        # 60% decrease from high_quality
    }

    for profile_name, scale_factor in quality_profiles.items():
        scaled_map = {}
        # Iterate through the high_quality_map and apply scaling
        for resolution, input_codecs in high_quality_map.items():
            scaled_map[resolution] = {}
            for input_codec, output_codecs in input_codecs.items():
                scaled_map[resolution][input_codec] = {}
                for output_codec, bitrate in output_codecs.items():
                    scaled_map[resolution][input_codec][output_codec] = scale_bitrate(bitrate, scale_factor)
        
        output_path = os.path.join(config_dir, f"{profile_name}.json")
        with open(output_path, "w") as f:
            json.dump(scaled_map, f, indent=4)
        print(f"Generated {output_path}")

if __name__ == "__main__":
    generate_configs()