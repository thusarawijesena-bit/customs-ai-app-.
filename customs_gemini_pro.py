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

query = st.text_input("ඇඳුමේ නම ගහන්න (උදා: boy's casual denim trouser):")

# --- 5. AI ගණනය කිරීම ---
if st.button("🔍 සම්පූර්ණ රේගු වාර්තාව ගණනය කරන්න"):
    if query and df is not None:
        with st.spinner('රේගු වාර්තාව සකස් කරමින් පවතී...'):
            try:
                search_term = query.lower()
                # අදාළ වචනය තියෙන පේළි තෝරාගැනීම
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                relevant_data = df[mask]

                if relevant_data.empty:
                    st.warning("සමාවෙන්න, මේ භාණ්ඩයට අදාළ දත්ත එක්සෙල් ෂීට් එකේ හොයාගන්න බැරි වුණා.")
                else:
                    # මුල් පේළි 3 පමණක් AI එකට යැවීම (Quota බේරා ගැනීමට)
                    data_to_send = relevant_data.head(3).to_string()

                    ai_prompt = f"""
                    You are a Sri Lanka Customs expert.
                    Calculate the total customs duty and taxes for the following item.
                    Item: {query}
                    
                    Here is the exactly relevant data row from the customs tariff guide:
                    {data_to_send}

                    Please calculate the duties and provide a highly detailed, professional breakdown in Sinhala language.
                    """

                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content(ai_prompt)

                    # රිපෝට් එක ලස්සන කොටුවක පෙන්නනවා
                    st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"වාර්තාව සකස් කිරීමේදී ගැටලුවක් ආවා මචං: {e}")
    elif df is None:
        st.error("දත්ත ගොනුව (Excel file) කියවීමේ ගැටලුවක් ඇත.")
    else:
        st.warning("කරුණාකර භාණ්ඩයේ නම ඇතුළත් කරන්න.")
