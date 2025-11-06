import pandas as pd
from sklearn.preprocessing import LabelEncoder

def encode_with_win_rates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds performance-based encodings (win rates) and label-encoded IDs
    for Jockeys and Trainers.

    Expected columns:
        - 'Jockey'
        - 'Trainer'
        - 'Finish Position'  (numeric)

    Returns:
        df with new columns:
            'Win', 'JockeyWinRate', 'TrainerWinRate',
            'Jockey_ID', 'Trainer_ID',
            'Jockey_Enc', 'Trainer_Enc'
    """

    # --- 1️⃣ Mark wins --------------------------------------------------------
    df["Win"] = df["Finish Position"].apply(lambda x: 1 if x == 1 else 0)

    # --- 2️⃣ Compute win rates -----------------------------------------------
    jockey_win_rate = (
        df.groupby("Jockey")["Win"]
          .mean()
          .reset_index(name="JockeyWinRate")
    )

    trainer_win_rate = (
        df.groupby("Trainer")["Win"]
          .mean()
          .reset_index(name="TrainerWinRate")
    )

    # --- 3️⃣ Merge into main DataFrame ---------------------------------------
    df = df.merge(jockey_win_rate, on="Jockey", how="left")
    df = df.merge(trainer_win_rate, on="Trainer", how="left")

    # --- 4️⃣ Handle missing values (new or rare names) -----------------------
    df["JockeyWinRate"].fillna(df["JockeyWinRate"].mean(), inplace=True)
    df["TrainerWinRate"].fillna(df["TrainerWinRate"].mean(), inplace=True)

    # --- 5️⃣ Label Encode categorical IDs ------------------------------------
    le_jockey = LabelEncoder()
    le_trainer = LabelEncoder()

    df["Jockey_ID"] = le_jockey.fit_transform(df["Jockey"])
    df["Trainer_ID"] = le_trainer.fit_transform(df["Trainer"])

    # --- 6️⃣ Assign final encoded numeric features ---------------------------
    df["Jockey_Enc"] = df["JockeyWinRate"]
    df["Trainer_Enc"] = df["TrainerWinRate"]

    return df
