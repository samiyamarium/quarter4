import streamlit as st
import requests
import json
from openai import OpenAI

# --- Setup OpenAI client using Streamlit secrets ---
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except KeyError:
    st.error("⚠️ OpenAI API key not found. Please configure 'OPENAI_API_KEY' in secrets.toml or Streamlit Cloud.")
    st.stop()
except Exception as e:
    st.error(f"⚠️ Error initializing OpenAI client: {e}")
    st.stop()

# --- API endpoint for products ---
PRODUCT_API = "https://hackathon-apis.vercel.app/api/products"

# --- Custom CSS for pink background and white labels ---
custom_css = """
<style>
    .stApp {
        background-color: #ff69b4;  /* Pink background */
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
@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_products():
    try:
        response = requests.get(PRODUCT_API, timeout=10)
        response.raise_for_status()
        data = response.json()  # Fetch as JSON
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

# --- Format product info for display in UI ---
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

# --- Ask OpenAI for product suggestions and return JSON response ---
def ask_shopping_assistant(user_query, matched_products):
    context = json.dumps(matched_products[:5], indent=2)
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Changed to gpt-3.5-turbo for broader access
            messages=[
                {"role": "system", "content": "You are a helpful shopping assistant for furnitures.Provide smart product suggestions and insights in a concise manner. five suggestions of furnitures only"},
                {"role": "user", "content": user_query},
                {"role": "assistant", "content": f"Here are some products:\n{context}"}
            ]
        )
        # Convert OpenAI response to JSON
        response_json = {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        return response_json
    except Exception as e:
        return {"error": f"⚠️ OpenAI error: {str(e)}"}

# --- Streamlit UI ---
st.title("🛍️ Smart Shopping Agent")

user_input = st.text_input("What are you looking for?", placeholder="e.g.,sofa,chair,table etc")
if st.button("Search") and user_input:
    with st.spinner("🔎 Searching products..."):
        all_products = fetch_products()
        matched = filter_products(all_products, user_input)

    # Display matching products
    st.subheader("📦 Matching Products")
    st.markdown(format_products(matched[:5]))

    # Display raw JSON for products
   # st.subheader("📄 Raw Product JSON")
    #st.json(matched[:5])  # Display JSON of matched products

    # Get and display AI recommendation
    #with st.spinner("💡 Getting AI recommendation..."):
     #   ai_response = ask_shopping_assistant(user_input, matched)
    
