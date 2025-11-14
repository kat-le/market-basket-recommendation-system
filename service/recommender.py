import pandas as pd
from pathlib import Path
from typing import Union

class Recommender:
    def __init__(self, rules_path: Union[str, Path]):
        self.rules = pd.read_parquet(str(rules_path))

    def recommend(self, cart: list[str], top_k: int = 5) -> list[dict]:
        cart = sorted({(x or "").strip() for x in cart if isinstance(x, str) and x.strip()})
        if not cart:
            return []

        cart_set = set(cart)
        mask = self.rules["antecedents"].apply(lambda ants: set(ants).issubset(cart_set))
        sub = self.rules[mask]

        if sub.empty:
            return []

        cand = (sub[["consequent","score","confidence","lift"]]
                .groupby("consequent", as_index=False)
                .agg({"score":"max","confidence":"max","lift":"max"}))
        cand = cand[~cand["consequent"].isin(cart)]
        if cand.empty:
            return []

        cand = cand.sort_values(["score","confidence","lift"], ascending=False).head(top_k)
        return [
            {
                "item": row["consequent"],
                "score": float(row["score"]),
                "confidence": float(row["confidence"]),
                "lift": float(row["lift"])
            }
            for _, row in cand.iterrows()
        ]