import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

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
        st.error(f"Excel ෆයිල් එක කියවීමේ දෝෂයක්: {e}")
        return None

df = load_tariff_data()

# --- 4. ප්‍රධාන අතුරු මුහුණත (UI) ---
st.title("🇱🇰 Customs AI Pro - Ultimate")
st.markdown("### Powered by Gemini Structured Intelligence 🚀")

st.markdown("කරුණාකර භාණ්ඩයේ තොරතුරු නිවැරදිව ලබා දෙන්න:")

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

# --- 5. AI Chaining (පියවරෙන් පියවර ගණනය කිරීම) ---
if st.button("🔍 සම්පූර්ණ රේගු වාර්තාව සහ බදු ගණනය කරන්න"):
    if item_base_name and df is not None:
        with st.spinner('රේගු කේතය සහ බදු මුදල් සකස් කරමින් පවතී...'):
            try:
                # ---------------------------------------------------------
                # පියවර 1: AI එක ලවා හරියටම HS Code එක හොයාගැනීම (Classifier)
                # ---------------------------------------------------------
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Excel දත්ත යවන්නේ නෑ, ලොජික් එක විතරයි යවන්නේ
                classifier_prompt = f"""
                You are a strict Sri Lanka Customs HS Classification Engine. 
                Your ONLY job is to output the correct 8-digit HS code (e.g., 6211.43.92) for the following item based on Sri Lanka Tariff Chapter 62.
                
                Item: {item_base_name}
                Gender: {gender}
                Material: {material}
                Make: {make_type}
                Loom Type: {loom_type}

                CRITICAL LOGIC FOR SAREES:
                - Cotton (Handloom) = 6211.42.12
                - Cotton (Powerloom / Other) = 6211.42.92
                - Synthetic (Handloom) = 6211.43.12
                - Synthetic (Powerloom / Other) = 6211.43.92
                
                OUTPUT FORMAT: Return ONLY the 8-digit code. No extra text, no spaces. Example: 6211.43.92
                """
                
                hs_response = model.generate_content(classifier_prompt)
                target_hs_code = hs_response.text.strip()
                
                st.info(f"📌 AI විසින් හඳුනාගත් මූලික HS කේතය: **{target_hs_code}**")

                # ---------------------------------------------------------
                # පියවර 2: Python මගින් Excel එකෙන් ඒ පේළිය කපා ගැනීම (Finder - අලුත් ක්‍රමය)
                # ---------------------------------------------------------
                # Column නම් මොනවා වුණත්, මුළු ෂීට් එකෙන්ම අර ඉලක්කම් 8 තියෙන පේළිය හොයනවා
                mask = df.astype(str).apply(lambda x: x.str.contains(target_hs_code, regex=False)).any(axis=1)
                exact_row = df[mask]
                
                if exact_row.empty:
                    st.warning(f"අයියෝ මචං, AI එකෙන් දුන්න {target_hs_code} කේතය Excel ෂීට් එකේ කොහේවත් නෑ. Excel එකේ කේතය තියෙන්නේ වෙනස් විදිහකටද බලන්න.")
                else:
                    # ඒ පේළිය AI එකට කියවන්න පුළුවන් විදිහට හදාගන්නවා
                    row_data_string = exact_row.to_string(index=False)
                # පියවර 3: AI එක ලවා ගණනය කිරීම සහ රිපෝට් එක හැදීම (Calculator)
                # ---------------------------------------------------------
                report_prompt = f"""
                You are an Expert Sri Lanka Customs Officer.
                        
                Here is the exact matched tariff data row from the Excel sheet for HS Code {target_hs_code}:
                {row_data_string}

                        Import Data:
                        - CIF: Rs. {cif_value}
                        - Weight: {net_weight} kg
                        - Quantity: {quantity} units

                        Your Task:
                        1. Provide a professional Sinhala report based ONLY on this provided data row.
                        2. If CIF, Weight, and Quantity are > 0, calculate the duties (Gen Duty, VAT, PAL, Cess, etc.) using the rates IN THIS ROW ONLY. Show the math.
                        3. Use standard customs terminology. Do not translate 'Crocheted' to 'කිඹුල්' (use ගෙතූ).
                        """
                        
                        final_response = model.generate_content(report_prompt)
                        st.markdown(f'<div class="report-box">{final_response.text}</div>', unsafe_allow_html=True)

            except Exception as e:
                st.error(f"වාර්තාව සකස් කිරීමේදී ගැටලුවක් ආවා මචං: {e}")
    elif df is None:
        st.error("දත්ත ගොනුව (Excel file) කියවීමේ ගැටලුවක් ඇත.")
    else:
        st.warning("කරුණාකර මුලින්ම භාණ්ඩයේ නම ඇතුළත් කරන්න.")
