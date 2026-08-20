import os

labels_dir = "labels"
# Get the absolute path to labels directory
base_dir = os.path.dirname(os.path.abspath(__file__))
labels_path = os.path.join(base_dir, labels_dir)

renamed_count = 0
skipped_count = 0

if not os.path.exists(labels_path):
    print(f"Directory not found: {labels_path}")
else:
    for filename in os.listdir(labels_path):
        if "%5C" in filename:
            # Split by %5C and take the last part
            new_filename = filename.split("%5C")[-1]
            
            old_filepath = os.path.join(labels_path, filename)
            new_filepath = os.path.join(labels_path, new_filename)
            
            # Check if the file already exists to avoid overwriting
            if os.path.exists(new_filepath):
                print(f"Warning: {new_filename} already exists, skipping {filename}")
                skipped_count += 1
                continue
                
            os.rename(old_filepath, new_filepath)
            renamed_count += 1
            
    print(f"Renamed {renamed_count} files.")
    if skipped_count > 0:
        print(f"Skipped {skipped_count} files due to name conflicts.")
