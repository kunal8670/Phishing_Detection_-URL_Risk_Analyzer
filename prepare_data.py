import pandas as pd
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from backend.services.feature_extractor import extract_features

ORIGINAL_CSV = os.path.join(
    os.path.dirname(__file__), "backend", "data", "original_dataset.csv"
)
GENERATED_CSV = os.path.join(
    os.path.dirname(__file__), "backend", "data", "generated_dataset.csv"
)
DATA_DIR = os.path.join(os.path.dirname(__file__), "backend", "data")

print("Loading original dataset...")
df = pd.read_csv(ORIGINAL_CSV)
print(f"Total URLs: {len(df)}")

feature_cols = [
    "URLLength",
    "DomainLength",
    "IsDomainIP",
    "TLDLength",
    "NoOfSubDomain",
    "NoOfLettersInURL",
    "LetterRatioInURL",
    "NoOfDigitsInURL",
    "DigitRatioInURL",
    "NoOfEqualsInURL",
    "NoOfQMarkInURL",
    "NoOfAmpersandInURL",
    "NoOfOtherSpecialCharsInURL",
    "SpecialCharRatioInURL",
    "HasObfuscation",
    "NoOfObfuscatedChar",
    "ObfuscationRatio",
    "IsHTTPS",
    "Bank",
    "Pay",
    "Crypto",
    "SuspiciousWords",
    "URLDepth",
    "AvgTokenLength",
]

rows = []
url_list = []
for i, (_, row) in enumerate(df.iterrows()):
    url = row["URL"]
    label = row["label"]
    try:
        features = extract_features(url)
        features["label"] = label
        rows.append(features)
        url_list.append(url)
    except Exception as e:
        print(f"  Error on row {i}: {url} -> {e}")

    if (i + 1) % 50000 == 0:
        print(f"  Processed {i + 1}/{len(df)}")

print(f"\nBuilding generated dataset with {len(rows)} rows...")
new_df = pd.DataFrame(rows)
new_df["URL"] = url_list
new_df.to_csv(GENERATED_CSV, index=False)
print(f"Saved to {GENERATED_CSV}")
print(f"Shape: {new_df.shape}")
print(f"Label distribution:\n{new_df['label'].value_counts()}")

from sklearn.model_selection import train_test_split

train_df, temp_df = train_test_split(
    new_df, test_size=0.30, random_state=42, stratify=new_df["label"]
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.50, random_state=42, stratify=temp_df["label"]
)

train_path = os.path.join(DATA_DIR, "train.csv")
val_path = os.path.join(DATA_DIR, "val.csv")
test_path = os.path.join(DATA_DIR, "test.csv")

train_df[feature_cols + ["label"]].to_csv(train_path, index=False)
val_df[feature_cols + ["label"]].to_csv(val_path, index=False)
test_df[["URL"] + feature_cols + ["label"]].to_csv(test_path, index=False)

print(f"\nSplit complete:")
print(f"  Train: {len(train_df)} rows -> {train_path} (features + label)")
print(f"  Val:   {len(val_df)} rows -> {val_path} (features + label)")
print(f"  Test:  {len(test_df)} rows -> {test_path} (URL + features + label)")
