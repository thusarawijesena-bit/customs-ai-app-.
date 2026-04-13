import streamlit as st
import google.generativeai as genai
import pandas as pd

# --- 1. පිටුවේ පෙනුම සහ ඩිසයින් ---
st.set_page_config(page_title="Customs AI Pro - Ultimate", page_icon="🇱🇰", layout="wide")

st.markdown("""
<style>
    .report-box {
        background-color: #1E293B;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #475569;
        color: #E2E8F0;
        line-height: 1.7;
    }
</style>
""", unsafe_allow_html=True)

# --- 2. API යතුර ලබා ගැනීම ---
api_key = st.secrets["GEMINI_API_KEY"]
if api_key:
    genai.configure(api_key=api_key)

# --- 3. එක්සෙල් දත්ත කියවීම ---
@st.cache_data
def load_tariff_data():
    try:
        df = pd.read_excel('tariff_62.csv.xlsx')
        return df
    except Exception as e:
        return None

df = load_tariff_data()

# --- 4. ප්‍රධාන අතුරු මුහුණත (UI) ---
st.title("🇱🇰 Customs AI Pro - Ultimate")
st.markdown("### Powered by Gemini Structured Intelligence 🚀")

st.markdown("කරුණාකර භාණ්ඩයේ තොරතුරු නිවැරදිව ලබා දෙන්න:")

# විස්තර අහන කොටු
col1, col2 = st.columns(2)
with col1:
    item_base_name = st.text_input("භාණ්ඩයේ නම (උදා: shirt, trouser, saree):")
    gender = st.selectbox("කාණ්ඩය (Gender):", ["Unspecified (දන්නේ නැත)", "Men's / Boys", "Women's / Girls"])
    loom_type = st.selectbox("වියපු ආකාරය (Loom Type):", ["Unspecified (දන්නේ නැත)", "Handloom (අත්යන්ත්‍ර)", "Powerloom (බලවේග යන්ත්‍ර)"])

with col2:
    material = st.selectbox("අමුද්‍රව්‍ය (Material):", ["Unspecified (දන්නේ නැත)", "Cotton (කපු)", "Synthetic/Polyester", "Silk", "Wool"])
    make_type = st.selectbox("නිෂ්පාදන ක්‍රමය (Make):", ["Unspecified (දන්නේ නැත)", "Woven (වියන ලද)", "Knitted / Crocheted (ගෙතූ)"])

st.markdown("---")
st.markdown("### 🧮 බදු ගණනය කිරීම සඳහා දත්ත (Duty Calculator):")

col3, col4, col5 = st.columns(3)
with col3:
    cif_value = st.number_input("CIF වටිනාකම (LKR):", min_value=0.0, step=1000.0)
with col4:
    net_weight = st.number_input("ශුද්ධ බර - Net Weight (kg):", min_value=0.0, step=1.0)
with col5:
    quantity = st.number_input("ඒකක ගණන - Quantity:", min_value=0, step=1)

# --- 5. AI ගණනය කිරීම ---
if st.button("🔍 සම්පූර්ණ රේගු වාර්තාව සහ බදු ගණනය කරන්න"):
    if item_base_name and df is not None:
        with st.spinner('රේගු වාර්තාව සහ බදු මුදල් සකස් කරමින් පවතී...'):
            try:
                search_term = item_base_name.lower()
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                relevant_data = df[mask]

                if relevant_data.empty:
                    st.warning("සමාවෙන්න, මේ භාණ්ඩයට අදාළ දත්ත එක්සෙල් ෂීට් එකේ හොයාගන්න බැරි වුණා.")
                else:
                    data_to_send = relevant_data.head(50).to_string()

                    # මෙතන තමයි AI එකේ මොළේට දෙන තද නියෝග ටික තියෙන්නේ
                    ai_prompt = f"""
                    You are an Expert Sri Lanka Customs Officer.
                    The user is asking for the customs duty calculation for the following item:
                    - Base Item: {item_base_name}
                    - Gender: {gender}
                    - Material: {material}
                    - Make: {make_type}
                    - Loom Type: {loom_type}
                    
                    Here is the import data for calculation:
                    - CIF Value (LKR): Rs. {cif_value}
                    - Net Weight: {net_weight} kg
                    - Quantity: {quantity} units

                    Here are the relevant data rows extracted from the customs tariff guide:
                    {data_to_send}

                    CRITICAL CLASSIFICATION LOGIC FOR SAREES (HS 6211.4x):
                    You MUST follow this strict hierarchy for Women's/girls' garments:
                    1. Fabric Type (e.g., Cotton = 6211.42, Man-made/Synthetic = 6211.43).
                    2. Loom Type (CRITICAL RULE: Handloom and Powerloom have DIFFERENT 8-digit codes. NEVER say there is no distinction. For Synthetic Sarees under 6211.43, Handloom is 6211.43.12. If the user selects Powerloom, you MUST classify it under "Other" which is strictly 6211.43.92).
                    3. Print/Style (Batik vs. Other).

                    TRANSLATION & TONE RULES:
                    - Provide the final report in highly professional, formal Sinhala Customs terminology.
                    - NEVER use absurd literal translations like "කිඹුල්". Use "ගෙතූ හෝ ගෙතුම් කටුවෙන් ගෙතූ නොවන" for "not knitted or crocheted".

                    Your Task:
                    1. Find the exact matching HS Code row based on the strict logic above (e.g., Output exactly 6211.43.92 for Synthetic Powerloom Saree).
                    2. Explain the classification logic briefly in the report.
                    3. IF CIF Value, Weight, and Quantity are provided (greater than 0), accurately CALCULATE the payable duties in Sri Lankan Rupees (LKR). Show the math breakdown clearly.
                    """

                    model = genai.GenerativeModel('gemini-2.5-flash')
                    response = model.generate_content(ai_prompt)

                    st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"වාර්තාව සකස් කිරීමේදී ගැටලුවක් ආවා මචං: {e}")
    elif df is None:
        st.error("දත්ත ගොනුව (Excel file) කියවීමේ ගැටලුවක් ඇත.")
    else:
        st.warning("කරුණාකර මුලින්ම භාණ්ඩයේ නම ඇතුළත් කරන්න.")
