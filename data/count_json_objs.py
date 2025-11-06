import os
import json

def count_json_objects_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return len(data)
            elif isinstance(data, dict):
                return 1
            else:
                return 0
    except Exception as e:
        print(f"⚠️ Error reading {filepath}: {e}")
        return 0

def count_json_objects_in_dir(root_dir):
    total_count = 0
    file_counts = {}

    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.json'):
                filepath = os.path.join(dirpath, filename)
                count = count_json_objects_in_file(filepath)
                file_counts[filepath] = count
                total_count += count

    return file_counts, total_count

if __name__ == "__main__":
    root_dir = os.path.dirname(os.path.abspath(__file__))
    file_counts, total = count_json_objects_in_dir(root_dir)

    print("\n📁 JSON Object Counts per File:")
    for path, count in file_counts.items():
        print(f"{path}: {count}")

    print(f"\n✅ Total JSON objects across all files: {total}")