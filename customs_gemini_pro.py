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
model = genai.GenerativeModel('gemini-3-flash-preview')
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


               # --- 4. ප්‍රධාන අතුරු මුහුණත (UI) - ස්මාර්ට් ක්‍රමය ---
st.title("🇱🇰 Customs AI Pro - Ultimate")
st.markdown("### Powered by Gemini Structured Intelligence 🚀")

st.markdown("කරුණාකර භාණ්ඩයේ තොරතුරු නිවැරදිව ලබා දෙන්න:")

# කොටු දෙකකට කඩලා ලස්සනට තොරතුරු අහනවා
col1, col2 = st.columns(2)

with col1:
    item_base_name = st.text_input("භාණ්ඩයේ නම (උදා: shirt, trouser, saree):")
    gender = st.selectbox("කාණ්ඩය (Gender):", ["Unspecified (දන්නේ නැත)", "Men's / Boys", "Women's / Girls"])
    # නව කොටස: වියපු ආකාරය (Handloom / Powerloom)
    loom_type = st.selectbox("වියපු ආකාරය (Loom Type):", ["Unspecified (දන්නේ නැත)", "Handloom (අත්යන්ත්‍ර)", "Powerloom (බලවේග යන්ත්‍ර)"])

with col2:
    material = st.selectbox("අමුද්‍රව්‍ය (Material):", ["Unspecified (දන්නේ නැත)", "Cotton (කපු)", "Synthetic/Polyester", "Silk", "Wool"])
    make_type = st.selectbox("නිෂ්පාදන ක්‍රමය (Make):", ["Unspecified (දන්නේ නැත)", "Woven (වියන ලද)", "Knitted / Crocheted (ගෙතූ)"])

# --- 5. AI ගණනය කිරීම ---
if st.button("🔍 සම්පූර්ණ රේගු වාර්තාව ගණනය জ্ঞකරන්න"):
    if item_base_name and df is not None:
        with st.spinner('රේගු වාර්තාව සකස් කරමින් පවතී...'):
            try:
                # 1. එක්සෙල් එකෙන් හොයන්නේ ප්‍රධාන නම විතරයි (උදා: shirt)
                search_term = item_base_name.lower()
                mask = df.astype(str).apply(lambda x: x.str.contains(search_term, case=False)).any(axis=1)
                relevant_data = df[mask]

                if relevant_data.empty:
                    st.warning("සමාවෙන්න, මේ භාණ්ඩයට අදාළ දත්ත එක්සෙල් ෂීට් එකේ හොයාගන්න බැරි වුණා.")
                else:
                    data_to_send = relevant_data.head(5).to_string()

                    # 2. AI එකට දෙන අලුත්ම නියෝගය (Smart Prompt)
                    ai_prompt = f"""
                    You are a Sri Lanka Customs expert.
                    The user is asking for the customs duty for the following item:
                    - Base Item: {item_base_name}
                    - Gender: {gender}
                    - Material: {material}
                    - Make (Woven/Knitted): {make_type}
                    - Loom Type (Handloom/Powerloom): {loom_type}
                    
                    Here are the relevant data rows extracted from the customs tariff guide:
                    {data_to_send}

                    Your Task:
                    1. Analyze the provided data rows. 
                    2. Find the row that best matches the specific Material, Make, Gender, and Loom Type requested by the user.
                    3. IF the user selected "Unspecified" for some options, clearly explain to the user in the report that duties vary based on those missing details.
                    4. Calculate the total duties based on the most accurate row.

                    Provide a highly detailed, professional breakdown in Sinhala language.
                    """

                    # මොඩල් එකේ නම 'gemini-pro' විදිහට වෙනස් කළා (404 Error එක හදන්න)
                    model = genai.GenerativeModel('gemini-3-flash')
                    response = model.generate_content(ai_prompt)

                    st.markdown(f'<div class="report-box">{response.text}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"වාර්තාව සකස් කිරීමේදී ගැටලුවක් ආවා මචං: {e}")
    elif df is None:
        st.error("දත්ත ගොනුව (Excel file) කියවීමේ ගැටලුවක් ඇත.")
    else:
        st.warning("කරුණාකර මුලින්ම භාණ්ඩයේ නම ඇතුළත් කරන්න.")           
