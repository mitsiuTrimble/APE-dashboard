#python copy_frame_trajectories.py /path/to/input /path/to/output

import os
import shutil
import argparse
import re

def is_valid_trajectory_file(filename):
    return re.fullmatch(r'frame_trajectory(\d*)\.txt', filename) is not None

def copy_valid_files(input_dir, output_dir):
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if is_valid_trajectory_file(file):
                # Construct full input path
                full_input_path = os.path.join(root, file)

                # Compute relative path to maintain folder structure
                relative_path = os.path.relpath(full_input_path, input_dir)
                output_file_path = os.path.join(output_dir, relative_path)

                # Create target directory if it doesn't exist
                os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                # Copy the file
                shutil.copy2(full_input_path, output_file_path)
                print(f"Copied: {relative_path}")

def main():
    parser = argparse.ArgumentParser(description="Copy frame_trajectory*.txt files preserving folder structure.")
    parser.add_argument("input_folder", help="Path to the input folder")
    parser.add_argument("output_folder", help="Path to the output folder")
    args = parser.parse_args()

    copy_valid_files(args.input_folder, args.output_folder)

if __name__ == "__main__":
    main()
