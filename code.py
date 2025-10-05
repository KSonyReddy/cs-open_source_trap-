import pandas as pd
from difflib import SequenceMatcher
from datetime import datetime
import matplotlib.pyplot as plt

# ---------------------------------------------------------------
# STEP 1: Load dataset
# ---------------------------------------------------------------
df = pd.read_csv("packages_metadata.csv")

# ---------------------------------------------------------------
# STEP 2: Typo-squatting Detection
# ---------------------------------------------------------------

popular_packages = ["requests", "numpy", "pandas", "react", "express"]

def is_typosquat(pkg_name, ref_list, threshold=0.85):
    for ref in ref_list:
        ratio = SequenceMatcher(None, pkg_name, ref).ratio()
        if ratio >= threshold and pkg_name != ref:
            return True
    return False

# Apply detection
df["typo_suspect"] = df["name"].apply(lambda x: is_typosquat(x, popular_packages))

# ---------------------------------------------------------------
# STEP 3: Abandoned Package Detection
# ---------------------------------------------------------------
def is_abandoned(last_update, years=2):
    try:
        last = datetime.strptime(last_update, "%Y-%m-%d")
        return (datetime.now() - last).days > years * 365
    except:
        return False

df["abandoned"] = df["last_updated"].apply(is_abandoned)

# ---------------------------------------------------------------
# STEP 4: Revived Package Detection
# ---------------------------------------------------------------
def is_revived(last_update, downloads, threshold=10000):
    try:
        last = datetime.strptime(last_update, "%Y-%m-%d")
        inactive = (datetime.now() - last).days > 730  # 2 years
        return inactive and downloads > threshold
    except:
        return False

df["revived_risk"] = df.apply(
    lambda row: is_revived(row["last_updated"], row["downloads"]), axis=1
)

# ---------------------------------------------------------------
# STEP 5: Risk Scoring System
# ---------------------------------------------------------------

df["risk_score"] = (
    df["typo_suspect"].astype(int) * 2 +
    df["abandoned"].astype(int) * 1 +
    df["revived_risk"].astype(int) * 3
)

# Convert risk score to risk level (categorical)
def categorize_risk(score):
    if score == 0:
        return "Low"
    elif score <= 3:
        return "Medium"
    else:
        return "High"

df["risk_level"] = df["risk_score"].apply(categorize_risk)

# ---------------------------------------------------------------
# STEP 6: Save Results
# ---------------------------------------------------------------
df.to_csv("enhanced_supply_chain_risks.csv", index=False)
print("✅ Analysis complete! Results saved to enhanced_supply_chain_risks.csv")

# ---------------------------------------------------------------
# STEP 7: Summary Output
# ---------------------------------------------------------------
print("\n--- SAMPLE OUTPUT ---")
print(df[["name", "ecosystem", "typo_suspect", "abandoned", "revived_risk", "risk_level"]])

# ---------------------------------------------------------------
# STEP 8: Visualization (Optional but Recommended)
# ---------------------------------------------------------------
# Bar chart: Count of risk levels by ecosystem
summary = df.groupby(["ecosystem", "risk_level"]).size().unstack(fill_value=0)

summary.plot(kind="bar", stacked=True, figsize=(8, 5))
plt.title("Supply Chain Risk Levels by Ecosystem")
plt.xlabel("Ecosystem")
plt.ylabel("Number of Packages")
plt.legend(title="Risk Level")
plt.tight_layout()
plt.show()
