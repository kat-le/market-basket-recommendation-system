import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
csv_path = ROOT / "data" / "transactions.csv"
art_dir  = ROOT / "artifacts"
art_dir.mkdir(parents=True, exist_ok=True)

# --- 1) Load CSV with 5 item columns ---
ITEM_COLS = ["item_1", "item_2", "item_3", "item_4", "item_5"]
df = pd.read_csv(csv_path)

# keep only the columns we need and drop fully empty rows
keep_cols = ["transaction_id"] + ITEM_COLS
df = df[keep_cols].dropna(how="all")

# --- 2) Build baskets list from item_1..item_5 (ignore blanks/NaN/duplicates) ---
def row_to_items(row):
    items = []
    for c in ITEM_COLS:
        val = row.get(c, None)
        if isinstance(val, str):
            v = val.strip()
            if v:
                items.append(v)
        elif pd.notna(val):
            items.append(str(val).strip())
    # unique & sorted for stability
    return sorted(set([x for x in items if x]))

baskets = df.apply(row_to_items, axis=1).tolist()
# filter out empty baskets if any
baskets = [b for b in baskets if b]

# --- 3) One-hot encode baskets ---
te = TransactionEncoder()
oht = te.fit_transform(baskets)
oht_df = pd.DataFrame(oht, columns=te.columns_)

# --- 4) FP-Growth + rules (tune minsup / confidence if needed) ---
freq  = fpgrowth(oht_df, min_support=0.003, use_colnames=True)
rules = association_rules(freq, metric="confidence", min_threshold=0.1)

# keep single-item consequents & clean columns
def to_sorted_list(x):
    return sorted(list(x)) if not isinstance(x, str) else [x]

rules["antecedents"] = rules["antecedents"].apply(to_sorted_list)
rules["consequents"] = rules["consequents"].apply(to_sorted_list)
rules = rules[rules["consequents"].apply(len) == 1].copy()
rules["consequent"]  = rules["consequents"].str[0]
rules["score"]       = rules["confidence"] * rules["lift"]

keep = ["antecedents","consequent","support","confidence","lift","score"]
rules_small = rules[keep].sort_values(["score","confidence","lift"], ascending=False).reset_index(drop=True)

# --- 5) Save artifacts for API & UI ---
items = sorted({i for basket in baskets for i in basket})
pd.Series(items).to_json(art_dir / "items.json", orient="values")
rules_small.to_parquet(art_dir / "rules.parquet", index=False)

print("Saved:")
print(f" - {art_dir/'items.json'}")
print(f" - {art_dir/'rules.parquet'}")
print(f"Stats: baskets={len(baskets)}, items={len(items)}, rules={len(rules_small)}")
