import streamlit as st
import requests
import json

# --- API endpoint for products ---
PRODUCT_API = "https://hackathon-apis.vercel.app/api/products"

# --- LLM endpoint URL (replace with your own if needed) ---
LLM_API_URL = "http://localhost:8000/v1/chat/completions"

# --- Custom CSS for pink background and white labels ---
custom_css = """
<style>
    .stApp {
        background-color: #ff69b4;
        color: white !important;
    }
    h1, h2, h3, h4, h5, h6, label, .stMarkdown, .stTextInput > label, .stTextArea > label {
        color: white !important;
    }
    .stButton > button {
        background-color: white !important;
        color: #ff69b4 !important;
        font-weight: bold;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
    }
    .stButton > button:hover {
        background-color: #ffe4ec !important;
        color: #c2185b !important;
    }
    .stSpinner > div > div {
        border-color: white !important;
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Fetch product list as JSON ---
@st.cache_data(ttl=3600)
def fetch_products():
    try:
        response = requests.get(PRODUCT_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        st.error("API response is not a list.")
        return []
    except requests.RequestException as e:
        st.error(f"Error fetching products: {e}")
        return []

# --- Filter product list based on user query ---
def filter_products(products, query):
    query = query.lower().strip()
    filtered = []
    for product in products:
        if not isinstance(product, dict):
            continue
        name = str(product.get("name", "")).lower()
        desc = str(product.get("description", "")).lower()
        category = str(product.get("category", "")).lower()
        if query in name or query in desc or query in category:
            filtered.append(product)
    return filtered

# --- Format product info for display ---
def format_products(products):
    if not products:
        return "❌ No matching products found."
    result = ""
    for p in products:
        result += f"""
**🛍️ {p.get('name', 'Unnamed Product')}**
- 💬 {p.get('description', 'No description')}
- 💲 Price: `{p.get('price', 'N/A')}`
- 📦 Category: `{p.get('category', 'N/A')}`

"""
    return result

# --- Send request to custom LLM endpoint ---
def ask_shopping_assistant(user_query, matched_products):
    context = json.dumps(matched_products[:5], indent=2)
    payload = {
        "model": "gpt-3.5-turbo",  # You can rename this based on your LLM
        "messages": [
            {"role": "system", "content": "You are a helpful shopping assistant for furnitures. Provide smart product suggestions and insights in a concise manner. Return only five suggestions."},
            {"role": "user", "content": user_query},
            {"role": "assistant", "content": f"Here are some products:\n{context}"}
        ]
    }

    try:
        response = requests.post(LLM_API_URL, json=payload)
        response.raise_for_status()
        result = response.json()
        return {
            "content": result["choices"][0]["message"]["content"],
            "model": result.get("model", ""),
            "usage": result.get("usage", {})
        }
    except Exception as e:
        return {"error": f"⚠️ Error from LLM API: {str(e)}"}

# --- Streamlit UI ---
st.title("🛍️ Smart Shopping Agent")

user_input = st.text_input("What are you looking for?", placeholder="e.g., sofa, chair, table etc.")
if st.button("Search") and user_input:
    with st.spinner("🔎 Searching products..."):
        all_products = fetch_products()
        matched = filter_products(all_products, user_input)

    # Display matching products
    st.subheader("📦 Matching Products")
    st.markdown(format_products(matched[:5]))

    # Get and display AI recommendation
    with st.spinner("💡 Getting AI recommendation..."):
        ai_response = ask_shopping_assistant(user_input, matched)

    st.subheader("🤖 Assistant Suggestion")
    if "error" in ai_response:
        st.error(ai_response["error"])
    else:
        st.markdown(ai_response["content"])
