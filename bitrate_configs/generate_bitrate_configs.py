import json
import os

def scale_bitrate(bitrate_str, scale_factor, min_bitrate_mbps=1):
    if bitrate_str == "N/A":
        return bitrate_str
    try:
        value = float(bitrate_str.replace('M', ''))
        scaled_value = round(value * scale_factor)
        # Ensure minimum bitrate
        if scaled_value < min_bitrate_mbps:
            scaled_value = min_bitrate_mbps
        return f"{scaled_value}M"
    except ValueError:
        return bitrate_str

def generate_configs():
    config_dir = "bitrate_configs"
    high_quality_path = os.path.join(config_dir, "high_quality.json")

    if not os.path.exists(high_quality_path):
        print(f"Error: {high_quality_path} not found. Cannot generate other configs.")
        return

    with open(high_quality_path, "r") as f:
        high_quality_map = json.load(f)

    quality_profiles = {
        "max_quality": 1.25,
        "balanced_quality": 0.8,
        "low_quality": 0.6,
        "min_quality": 0.4,
    }

    for profile_name, scale_factor in quality_profiles.items():
        scaled_map = {}
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