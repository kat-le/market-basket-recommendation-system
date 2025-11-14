from fastapi import FastAPI
from pydantic import BaseModel
from pathlib import Path
from recommender import Recommender

app = FastAPI(title="Market Basket Recommender", version="1.0")

# load artifacts created earlier
RULES_PATH = Path(__file__).resolve().parents[1] / "artifacts" / "rules.parquet"
REC = Recommender(RULES_PATH)

class CartIn(BaseModel):
    cart: list[str]

@app.post("/recommend")
def recommend(inp: CartIn):
    return {"recommendations": REC.recommend(inp.cart, top_k=5)}