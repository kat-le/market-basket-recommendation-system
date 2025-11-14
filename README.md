# Market Basket Analysis & Recommender System

This project builds an association-rule–based recommender system using transaction data. It applies market basket analysis to uncover relationships between items frequently purchased together, and then serves personalized recommendations through a simple web interface.

# Key Features

* Automated rule generation using FP-Growth (fast, scalable).
* Clean modular pipeline separating data prep, model, and UI layers.
* Interactive UI for testing and visualizing recommendations.
* Artifacts saved for easy reuse by APIs or dashboards.

# Quick Start 

## 1) Create a virtual env & install deps
```
python3 -m venv .venv
source .venv/bin/activate        
python -m pip install -U pip
pip install -r requirements.txt
```
## 2) Build artifacts (rules + item list)
```
python notebooks/build_rules.py
```
This saves:
* artifacts/rules.parquet – association rules
* artifacts/items.json – list of all items for the UI dropdown

## 3) Run the API (terminal 1)
```
cd service
python -m uvicorn app:app --reload
```
* FastAPI will listen on http://127.0.0.1:8000.

## 4) Run the UI (terminal 2)
```
streamlit run UI/ui.py
```
