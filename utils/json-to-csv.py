import json
import pandas as pd
import os
from rapidfuzz import process, fuzz

# --- FUNCTIONS ---
def fuzzy_map(source_list, target_list, threshold=80):
    mapping = {}
    for s in source_list:
        match = process.extractOne(s, target_list, scorer=fuzz.partial_ratio)
        if match and match[1] >= threshold:
            mapping[s] = match[0]
    return mapping

# --- PATHS ---
race = "MOONEE_VALLEY"
date = "2025-10-24"
input_folder = rf'.\utils\futures\json\{date}'
output_csv = rf'.\utils\futures\{race}_{date}.csv'
encoded_csv = r".\features\features_encoded.csv"

# --- HEADERS ---
csv_headers = [
    "Date","Track","Race Number","Horse","Barrier","Jockey","Trainer","SP",
    "Finish Position","Race Distance","Class","Track Condition","Weather",
    "Total Runners","Place","Win","SP_missing","JockeyWinRate","TrainerWinRate",
    "HorseWinRate","Jockey_ID","Trainer_ID","Horse_ID","Jockey_Enc","Trainer_Enc","Horse_Enc"
]

all_rows = []

# --- READ FUTURES JSON DATA ---
for root, dirs, files in os.walk(input_folder):
    for file in files:
        if file.endswith(".json"):
            path = os.path.join(root, file)
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            meeting = data.get("meeting", {})
            if not meeting:
                print(f"❌ No 'meeting' key in {file}")
                continue

            for runner in data.get("runners", []):
                sp = runner.get("fixedOdds", {}).get("returnWin")
                row = {
                    "Date": meeting.get("meetingDate"),
                    "Track": meeting.get("meetingName"),
                    "Race Number": data.get("raceNumber"),
                    "Horse": runner.get("runnerName", "").upper(),
                    "Barrier": runner.get("barrierNumber"),
                    "Jockey": runner.get("riderDriverName", "").upper(),
                    "Trainer": runner.get("trainerName", "").upper(),
                    "SP": sp,
                    "Finish Position": 0,
                    "Race Distance": data.get("raceDistance"),
                    "Class": data.get("raceClass"),
                    "Track Condition": meeting.get("trackCondition"),
                    "Weather": meeting.get("weatherCondition"),
                    "Total Runners": len(data.get('runners', [])),
                    "Place": 0,
                    "Win": 0,
                    "SP_missing": (0 if sp else 1),
                }
                all_rows.append(row)

# --- Convert futures data to DataFrame ---
df = pd.DataFrame(all_rows, columns=csv_headers[:17])
print(f"✅ Loaded {len(df)} future rows")

# --- Load encoded feature data ---
encoded = pd.read_csv(encoded_csv)
print(f"✅ Loaded {len(encoded)} encoded rows")

# --- Collapse encoded to unique horses (latest stats per horse) ---
encoded_unique = (
    encoded
    .sort_values(by="Date")  # ensure latest stats
    .groupby("Horse", as_index=False)
    .agg({
        "JockeyWinRate": "last",
        "TrainerWinRate": "last",
        "HorseWinRate": "last",
        "Jockey_ID": "last",
        "Trainer_ID": "last",
        "Horse_ID": "last",
        "Jockey_Enc": "last",
        "Trainer_Enc": "last",
        "Horse_Enc": "last",
        "Jockey": "last",
        "Trainer": "last"
    })
)
print(f"✅ Encoded collapsed from {len(encoded)} → {len(encoded_unique)} unique horses")

# --- Fuzzy map jockeys & trainers ---
jockey_map = fuzzy_map(df["Jockey"].unique(), encoded_unique["Jockey"].unique())
trainer_map = fuzzy_map(df["Trainer"].unique(), encoded_unique["Trainer"].unique())

df["Jockey"] = df["Jockey"].replace(jockey_map)
df["Trainer"] = df["Trainer"].replace(trainer_map)

print("✅ Fuzzy-mapped jockeys:", len(jockey_map))
print("✅ Fuzzy-mapped trainers:", len(trainer_map))

# --- Merge on Horse only ---
merged = df.merge(
    encoded_unique[
        ["Horse","JockeyWinRate","TrainerWinRate","HorseWinRate",
         "Jockey_ID","Trainer_ID","Horse_ID","Jockey_Enc","Trainer_Enc","Horse_Enc"]
    ],
    on="Horse",
    how="left"
)

# --- Drop duplicates just in case ---
merged = merged.drop_duplicates(subset=["Date","Track","Race Number","Horse"])

# --- Reorder columns to match CSV headers ---
merged = merged[csv_headers]

# --- Save to CSV ---
merged.to_csv(output_csv, index=False)
print(f"💾 Merged and saved to {output_csv}")
print(f"✅ Final shape: {merged.shape}")

# --- Optional: check matched horses ---
matched = merged["HorseWinRate"].notna().sum()
print(f"✅ Matched horses: {matched} / {len(df)} ({matched/len(df):.1%})")

print(merged.head(10))
