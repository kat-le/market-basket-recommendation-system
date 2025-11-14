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
