import streamlit as st
import requests
import pandas as pd
import json
from pathlib import Path

FASTAPI_URL = "http://127.0.0.1:8000/recommend"
ARTIFACTS_PATH = Path("artifacts") / "items.json"

@st.cache_data # Cache the data load so it only runs once
def load_available_items():
    """Loads the list of all items from the items.json artifact."""
    try:
        with open(ARTIFACTS_PATH, 'r') as f:
            # items.json contains a list of strings
            items = json.load(f)
        return items
    except FileNotFoundError:
        st.error(f"🚨 Artifact not found: Check if the file exists at {ARTIFACTS_PATH.resolve()}")
        return []
    
available_items = load_available_items()
st.title("🛒 Market Basket Recommender Checkout")

    
#initalize or get session state for the cart
if 'cart' not in st.session_state:
    st.session_state.cart = []

# Display current cart
st.subheader("Your Current Cart:")

# --- Clear Cart Button ---
clear_clicked = st.button("🗑️ Clear cart", disabled=not st.session_state.cart)
if clear_clicked:
    st.session_state.cart = []
    st.rerun()

# Show cart contents
if st.session_state.cart:
    st.write(", ".join(st.session_state.cart))
else:
    st.write("*Cart is empty. Add an item below.*")

st.markdown("---")

# --- Add Item Form ---
with st.form("item_adder"):
    selected_item = st.selectbox("Select Item to Add:", available_items)
    submitted = st.form_submit_button("➕ Add to Cart & Get Recommendations")

    if submitted and selected_item not in st.session_state.cart:
        st.session_state.cart.append(selected_item)
        st.rerun()

# --- Recommendations Logic ---
if st.session_state.cart:
    st.subheader("💡 Recommendations:")
    try:
        # 1. Prepare and send POST request to FastAPI
        response = requests.post(
            FASTAPI_URL,
            json={"cart": st.session_state.cart}
        )
        response.raise_for_status() # Raise exception for bad status codes
        
        # 2. Display recommendations
        recs = response.json().get("recommendations", [])

        if recs:
            st.caption("Click ➕ to add a recommended item to your cart.")
            h1, h2, h3, h4, h5 = st.columns([5, 1.2, 1.2, 1.2, 1.1])
            h1.markdown("**item**"); h2.markdown("**score**"); h3.markdown("**confidence**"); h4.markdown("**lift**"); h5.markdown("**add**")

            for i, rec in enumerate(recs):
                c1, c2, c3, c4, c5 = st.columns([5, 1.2, 1.2, 1.2, 1.1])
                c1.write(rec["item"])
                c2.write(f"{rec['score']:.4f}")
                c3.write(f"{rec['confidence']:.4f}")
                c4.write(f"{rec['lift']:.4f}")

                disabled = rec["item"] in st.session_state.cart
                if c5.button("➕ Add", key=f"add_rec_{i}", disabled=disabled):
                    if rec["item"] not in st.session_state.cart:
                        st.session_state.cart.append(rec["item"])
                    st.rerun()
        else:
            st.info("No common patterns found for your current cart. Try adding another item!")

            
    except requests.exceptions.ConnectionError:
        st.error("🚨 FastAPI service not running. Please start uvicorn in a separate terminal.")
    except Exception as e:
        st.error(f"An error occurred: {e}")