import os
import json
import tls_client
import pandas as pd
import time

input_root = r".\data\json_data" # JSON files per Month
output_root = r".\data\csv_data" # CSV files per Month
os.makedirs(output_root, exist_ok=True)

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.5',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}

for month_folder in sorted(os.listdir(input_root)):
    full_month_path = os.path.join(input_root, month_folder)
    if not os.path.isdir(full_month_path):
        continue

    month_output_path = os.path.join(output_root, month_folder)
    os.makedirs(month_output_path, exist_ok=True)

    for json_file in sorted(os.listdir(full_month_path)):
        if not json_file.endswith(".json"):
            continue

        race_date = json_file.replace(".json", "")
        day_output_path = os.path.join(month_output_path, f"{race_date}.csv")
        error_output_path = os.path.join(month_output_path, f"{race_date}_error.csv")

        # Skip today if file exists and no error file
        if os.path.exists(day_output_path) and not os.path.exists(error_output_path):
            print(f"🟡 Skipping {race_date}, already processed.")
            continue

        # Download racing links
        with open(os.path.join(full_month_path, json_file), "r") as f:
            race_links = json.load(f)

        previous_failed = []
        if os.path.exists(error_output_path):
            try:
                df_errors = pd.read_csv(error_output_path)
                previous_failed = df_errors["API URL"].tolist()
            except Exception as e:
                print(f"⚠️ Failed to read previous error file {error_output_path}: {e}")

        # If there is a file for the day that already exists → we will read it and complete it after the new attempts
        existing_rows = []
        if os.path.exists(day_output_path):
            try:
                existing_rows = pd.read_csv(day_output_path).to_dict(orient="records")
            except Exception as e:
                print(f"⚠️ Failed to read existing CSV {day_output_path}: {e}")

        total_race_links = [r for r in race_links if r.get("API URL") in previous_failed] if previous_failed else race_links

        daily_rows = []
        failed_apis = []

        session = tls_client.Session(client_identifier="chrome_118", random_tls_extension_order=True)

        for race in total_race_links:
            api_url = race.get("API URL")
            print(f"📡 Fetching: {api_url}")
            try:
                response = session.get(api_url, headers=headers)
                if response.status_code == 200:
                    try:
                        race_data = response.json()
                        if not isinstance(race_data, dict):
                            print(f"⚠️ Unexpected response (not dict) at {api_url}")
                            failed_apis.append({"API URL": api_url})
                            continue

                        meeting_info = race_data.get("meeting", {})
                        race_day = meeting_info.get("meetingDate", "")[:10]
                        if not race_day or race_day != race_date:
                            print(f"⚠️ Skipping {api_url} due to date mismatch")
                            failed_apis.append({"API URL": api_url})
                            continue

                        track = meeting_info.get("meetingName", "")
                        race_number = race_data.get("raceNumber", "")
                        race_distance = race_data.get("raceDistance", "")
                        race_class = race_data.get("raceClassConditions", "")
                        if isinstance(race_class, dict):
                            race_class = race_class.get("class", "")

                        track_condition = race.get("Track Condition", "")
                        weather = race.get("Weather", "")

                        results_list = race_data.get("results", [])
                        position_map = {}
                        for pos, item in enumerate(results_list, 1):
                            if isinstance(item, list) and item:
                                position_map[item[0]] = pos

                        runners = race_data.get("runners", [])
                        for runner in runners:
                            runner_number = runner.get("runnerNumber")
                            daily_rows.append({
                                "Date": race_date,
                                "Track": track,
                                "Race Number": race_number,
                                "Horse": runner.get("runnerName"),
                                "Barrier": runner.get("barrierNumber"),
                                "Jockey": runner.get("riderDriverName"),
                                "Trainer": runner.get("trainerName"),
                                "SP": runner.get("fixedOdds", {}).get("returnWin"),
                                "Finish Position": position_map.get(runner_number),
                                "Race Distance": race_distance,
                                "Class": race_class,
                                "Track Condition": track_condition,
                                "Weather": weather,
                                "Total Runners": len(runners)
                            })
                    except Exception as parse_error:
                        print(f"❌ Error parsing response from {api_url}: {parse_error}")
                        failed_apis.append({"API URL": api_url})
                else:
                    print(f"❌ Failed to fetch {api_url} - status {response.status_code}")
                    failed_apis.append({"API URL": api_url})
            except Exception as e:
                print(f"❌ Error fetching {api_url}: {e}")
                failed_apis.append({"API URL": api_url})

        # Save collected + old data (if present)
        if daily_rows or existing_rows:
            all_rows = existing_rows + daily_rows
            pd.DataFrame(all_rows).to_csv(day_output_path, index=False)
            print(f"✅ Saved total {len(all_rows)} rows to {day_output_path}")

        if failed_apis:
            pd.DataFrame(failed_apis).to_csv(error_output_path, index=False)
            print(f"⚠️ Saved {len(failed_apis)} failed URLs to {error_output_path}")
        else:
            if os.path.exists(error_output_path):
                os.remove(error_output_path)
                print(f"🧹 Removed error file {error_output_path} (all recovered)")

        session = None
        print("🛑 Closed session.")
        time.sleep(10)
