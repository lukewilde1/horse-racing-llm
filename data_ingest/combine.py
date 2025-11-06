import os
import pandas as pd

# Edit this path if your work folder location is different.
input_root = r".\data\csv_data"  # Folder containing Month Folders
output_file = r".\data\final_combined_racing_data.csv"  # Name of the final merge file

# List of all collected data
all_data = []

# Tracks to include
# tracks_to_include = ["ROSEHILL", "RANDWICK"]

# Passing through each month inside csv_data
for month_folder in sorted(os.listdir(input_root)):
    month_path = os.path.join(input_root, month_folder)
    if not os.path.isdir(month_path):
        continue

    # Passing through every day within the month
    for file in sorted(os.listdir(month_path)):
        if file.endswith(".csv") and not file.endswith("_error.csv"):
            file_path = os.path.join(month_path, file)
            try:
                df = pd.read_csv(file_path)

                # Filter only tracks_to_include
                # df = df[df['Track'].str.upper().isin(tracks_to_include)]

                df = df.map(lambda x: x.upper() if isinstance(x, str) else x)
                
                all_data.append(df)
                print(f"✅ Loaded: {file_path}")
            except Exception as e:
                print(f"❌ Error loading {file_path}: {e}")

# Merge all data
if all_data:
    combined_df = pd.concat(all_data, ignore_index=True)
    combined_df.to_csv(output_file, index=False)
    print(f"\n📁 Saved combined CSV to: {output_file}")
    print(f"📊 Total rows: {len(combined_df)}")
else:
    print("⚠️ No data found to combine.")
