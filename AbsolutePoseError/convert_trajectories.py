import os

def convert_csv_to_tum(input_path):
    output_path = os.path.splitext(input_path)[0] + ".tum"
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        lines = infile.readlines()
        # Skip first 2 header/comment lines
        data_lines = lines[2:]
        for line in data_lines:
            line = line.strip()
            if line:
                outfile.write(line + '\n')
    print(f"✅ Converted CSV: {input_path} → {output_path}")

def convert_txt_to_tum(input_path):
    output_path = os.path.splitext(input_path)[0] + ".tum"
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            line = line.strip()
            if line:
                # You could add validation here if needed
                outfile.write(line + '\n')
    print(f"✅ Converted TXT: {input_path} → {output_path}")

def convert_all_trajectories_in_folder(folder="."):
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            full_path = os.path.join(folder, filename)
            convert_csv_to_tum(full_path)
        elif filename.endswith(".txt"):
            full_path = os.path.join(folder, filename)
            convert_txt_to_tum(full_path)

if __name__ == "__main__":
    convert_all_trajectories_in_folder()
