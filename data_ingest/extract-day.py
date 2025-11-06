import os
import json
import tls_client
import time
from datetime import datetime, timedelta

proxies = {
    'http':'http://4shwoyr59p0kvkg-country-au:xoq1rhg4r19c3yu@rp.scrapegw.com:6060',
    'https':'http://4shwoyr59p0kvkg-country-au:xoq1rhg4r19c3yu@rp.scrapegw.com:6060'
}
session = tls_client.Session(client_identifier="chrome_118", random_tls_extension_order=True)

# EndDate must not be current day
start_date = datetime(2023, 1, 1)
end_date = datetime(2023, 3, 30)
api_base = "https://api.beta.tab.com.au/v1/historical-results-service/NSW/racing"

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'en-US,en;q=0.5',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
}

def create_intervals():
    # --- Create 3-month intervals ---
    start_date = datetime(2024, 9, 1)
    end_date = datetime(2024, 12, 31)

    dates = []
    current = start_date

    while current <= end_date:
        dates.append(current)
        month = current.month + 3
        year = current.year + (month - 1) // 12
        month = ((month - 1) % 12) + 1
        current = current.replace(year=year, month=month)

    return dates

def pull_data(start_date, end_date):
    output_folder = r".\data\json_data" # JSON data
    os.makedirs(output_folder, exist_ok=True)

    current_month = start_date.replace(day=1)

    locations = ["NSW", "SA", "WA", "QLD", "ACT", "VIC", "NT", "HKG"]

    while current_month <= end_date:
        month_str = current_month.strftime("%Y-%m")
        print(f"\n📆 Start downloading month: {month_str}")

        month_attempt = 1
        while month_attempt <= 3:
            print(f"\n🔁 attempt {month_attempt} for month {month_str}")

            current_date = current_month
            failed_days = []

            while current_date.month == current_month.month and current_date <= end_date:
                date_str = current_date.strftime("%Y-%m-%d")
                month_folder = os.path.join(output_folder, month_str)
                os.makedirs(month_folder, exist_ok=True)
                output_file = os.path.join(month_folder, f"{date_str}.json")

                if os.path.exists(output_file):
                    print(f"🟡 {date_str}: Already exists, skipping.")
                    current_date += timedelta(days=1)
                    continue

                success = False
                for attempt in range(1, 4):
                    print(f"🔄 {date_str}: Attempt {attempt}...")
                    try:
                        response = session.get(f"{api_base}/{date_str}", headers=headers)
                        if response.status_code == 200:
                            data = response.json()
                            race_api_urls = []

                            for meeting in data.get("meetings", []):
                                if (meeting.get("countryCode") == "AUS" or meeting.get("location") in locations) and meeting.get("raceType") == "R":
                                    venue = meeting.get("venueMnemonic")
                                    race_type = meeting.get("raceType")
                                    weatherCondition = meeting.get('weatherCondition','')
                                    trackCondition = meeting.get('trackCondition','')
                                    for race in meeting.get("races", []):
                                        race_number = race.get("raceNumber")
                                        if all([date_str, venue, race_type, race_number]):
                                            race_url = f"{api_base}/{date_str}/{venue}/{race_type}/races/{race_number}"
                                            race_api_urls.append({
                                                "Date": date_str,
                                                "Venue": venue,
                                                "Race Number": race_number,
                                                "Race Type": race_type,
                                                'Track Condition':trackCondition,
                                                'Weather':weatherCondition,
                                                "API URL": race_url
                                            })

                            with open(output_file, "w") as f:
                                json.dump(race_api_urls, f, indent=2)

                            print(f"✅ {date_str}: {len(race_api_urls)} races saved.")
                            success = True
                            break
                        else:
                            print(f"❌ {date_str}: Status code {response.status_code}: Message {response.text}")
                    except Exception as e:
                        print(f"❌ {date_str}: Error - {e}")
                    time.sleep(2.5)

                if not success:
                    failed_days.append(current_date)

                current_date += timedelta(days=1)

            if not failed_days:
                print(f"✅ All days of the month {month_str} have been loaded successfully.")
                break
            else:
                print(f"⚠️ {len(failed_days)} days in month {month_str} could not be loaded. Try again...")
                month_attempt += 1

        current_month = (current_month + timedelta(days=32)).replace(day=1)

dates = create_intervals()
# --- Run pull_data for each range ---
for i in range(len(dates) - 1):
    start = dates[i]
    end = dates[i + 1]
    pull_data(start, end)