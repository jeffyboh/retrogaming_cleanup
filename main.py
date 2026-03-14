import os
import hashlib
import csv
import configparser
from pathlib import Path

def get_md5(file_path):
    """Generates an MD5 hash for a file using a buffer to save memory."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return f"Error: {e}"

def catalog_roms():
    # Load Configuration
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    roots = [r.strip() for r in config['SETTINGS']['root_folders'].split(',')]
    output_file = config['SETTINGS']['output_file']
    
    data_list = []

    for root_dir in roots:
        print(f"Scanning: {root_dir}...")
        root_path = Path(root_dir)
        
        if not root_path.exists():
            print(f"Skipping {root_dir}: Path not found.")
            continue

        # Walk through all subdirectories
        for current_path, dirs, files in os.walk(root_path):
            for file in files:
                # Skip files in excluded folders
                skip_folders = [s.strip() for s in config['SETTINGS']['skip_folder'].split(',')]
                # Check if any part of the relative path matches a skip folder
                relative_path = Path(current_path).relative_to(root_path)
                if any(part in skip_folders for part in relative_path.parts):
                    continue
                file_full_path = Path(current_path) / file
                
                # Logic to determine Gaming System:
                # We want the folder name directly under the root_path
                relative_path = file_full_path.relative_to(root_path)
                system_name = relative_path.parts[0] if relative_path.parts else "Unknown"

                # Extract file details
                game_name = file_full_path.stem  # Filename without extension
                file_type = file_full_path.suffix.replace('.', '')
                
                print(f"Hashing: {game_name} ({system_name})...")
                md5_hash = get_md5(file_full_path)

                data_list.append({
                    "Gaming System Name": system_name,
                    "Game": game_name,
                    "File Type": file_type,
                    "File Location": str(file_full_path),
                    "MD5 Hash": md5_hash
                })

    # Save to CSV (Spreadsheet compatible)
    keys = ["Gaming System Name", "Game", "File Type", "File Location", "MD5 Hash"]
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        dict_writer = csv.DictWriter(f, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(data_list)

    print(f"\nSuccess! Catalog saved to {output_file}")

if __name__ == "__main__":
    catalog_roms()