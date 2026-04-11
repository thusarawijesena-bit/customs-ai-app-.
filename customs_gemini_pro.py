import streamlit as st
import google.generativeai as genai
import pandas as pd
import json  # <-- මෙන්න මේක තමයි අඩුවෙලා තිබුණේ!
# Excel දත්ත RAM එකේ තබා ගැනීමේ ෆන්ක්ෂන් එක
@st.cache_data
def load_tariff_data():
    try:
        df = pd.read_excel('tariff_62.csv.xlsx')
        return df.to_string()
    except Exception as e:
        return None

# --- 1. SETUP & CONFIGURATION ---
st.set_page_config(page_title="Customs AI Pro - Ultimate", page_icon="🇱🇰", layout="wide")

st.markdown("""
<style>
    .big-font { font-size:20px !important; color: #93C5FD; font-weight: bold;} 
    .report-box { 
        background-color: #1E293B; /* අඳුරු, ඇසට සුවදායී පසුබිමක් */
        padding: 25px; 
        border-radius: 12px; 
        border: 1px solid #475569; 
        color: #E2E8F0; /* දිලිසෙන්නේ නැති මෘදු අළු/සුදු පැහැයක් */
        line-height: 1.7;
        font-size: 16px;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar for API Key
st.sidebar.markdown("### ⚙️ සැකසුම්")
api_key = st.sidebar.text_input("Gemini API Key එක ඇතුළත් කරන්න:", type="password")

if api_key:
    genai.configure(api_key=api_key)

st.title("🇱🇰 Customs AI Pro - Ultimate")
st.markdown("### Powered by Gemini Structured Intelligence 🚀")

# --- 2. USER INPUT ---
query = st.text_input("ඇඳුමේ නම ගහන්න (උදා: boy's casual denim trouser):")

# --- 3. AI STRUCTURED EXTRACTOR ---
@st.cache_data 
def extract_parameters_with_ai(query):
    # Free & Stable Model
    model = genai.GenerativeModel # මෙන්න මේ විදිහට වෙනස් කරන්න
    model = genai.GenerativeModel  # ෆන්ක්ෂන් එක ඇතුළෙයි, යට බොත්තම ළඟයි තැන් දෙකේම මේක දාන්න:
    # ෆන්ක්ෂන් එක ඇතුළෙයි, යට බොත්තම ළඟයි තැන් දෙකේම මේක දාන්න:
   # ෆන්ක්ෂන් එක ඇතුළෙයි, යට බොත්තම ළඟයි තැන් දෙකේම මේක දාන්න:
    model = genai.GenerativeModel('models/gemini-flash-latest')
    
    prompt = f"""
    You are an expert Data Extractor. Extract details from the user's clothing query into strict JSON.
    Do NOT guess. If info is missing, output "unknown".
    
    Query: "{query}"
    
    Format EXACTLY like this JSON:
    {{
        "item": "base item name (e.g. trouser, shirt)",
        "gender": "men", "women", or "unknown",
        "fabric": "woven", "knitted", or "unknown",
        "material": "cotton", "synthetic", "wool", "silk", or "unknown"
    }}
    """
    try:
        response = model.generate_content(prompt)
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        return {"error": str(e)}

if query:
    if not api_key:
        st.error("කරුණාකර වම් පසින් API Key එක ඇතුළත් කරන්න.")
        st.stop()
        
    with st.spinner("🧠 AI මොළය දත්ත විශ්ලේෂණය කරමින් පවතී..."):
        ai_data = extract_parameters_with_ai(query)
        
    if "error" in ai_data:
        st.error(f"AI එකත් එක්ක සම්බන්ධ වීමේ ගැටලුවක්! හේතුව: {ai_data['error']}")
    else:
        st.markdown("<p class='big-font'>🤖 AI ග්‍රහණය කරගත් දත්ත:</p>", unsafe_allow_html=True)
        st.json(ai_data)
        
        st.info("💡 මචං, නිවැරදිම HS Code එක දෙන්න මට තව පොඩි විස්තර ටිකක් ඕනෑ:")

        col1, col2, col3 = st.columns(3)

        with col1:
            default_gender = 0 if ai_data.get("gender") == "men" else 1 if ai_data.get("gender") == "women" else 0
            gender_label = "කා සඳහාද? (Gender)"
            if ai_data.get("gender") in ["men", "women"]:
                gender_label += f" - 🤖 AI: {ai_data.get('gender').title()}"
            final_gender = st.radio(gender_label, ["Men/Boys", "Women/Girls"], index=default_gender)

        with col2:
            default_fabric = 0 if ai_data.get("fabric") == "woven" else 1 if ai_data.get("fabric") == "knitted" else 0
            fabric_label = "රෙදි වර්ගය (Fabric)"
            if ai_data.get("fabric") in ["woven", "knitted"]:
                fabric_label += f" - 🤖 AI: {ai_data.get('fabric').title()}"
            final_fabric = st.radio(fabric_label, ["Woven (වියන ලද)", "Knitted (ගෙතූ)"], index=default_fabric)

        with col3:
            materials_list = ["Cotton (කපු)", "Synthetic (කෘතිම)", "Wool (ලොම්)", "Silk (සේද)", "Other (වෙනත්)"]
            mat_guess = ai_data.get("material", "unknown").lower()
            
            default_mat = 0 
            if "synthetic" in mat_guess or "polyester" in mat_guess: default_mat = 1
            elif "wool" in mat_guess: default_mat = 2
            elif "silk" in mat_guess: default_mat = 3
            
            mat_label = "අමුද්‍රව්‍ය (Material)"
            if mat_guess != "unknown":
                 mat_label += f" - 🤖 AI: {mat_guess.title()}"
                 
            final_material = st.selectbox(mat_label, materials_list, index=default_mat)
# රෙදි වියන ක්‍රමය (Weaving Method)
        weaving_method = st.radio("වියන ක්‍රමය (Weaving Method)", ["Powerloom (බලවේග යන්ත්‍ර/Mill-made)", "Handloom (අත්යන්ත්‍ර)"])
        # --- 4. HS CODE & DUTY CALCULATION ---
        st.markdown("---") 
        
        item_name = ai_data.get('item', 'Item')
        final_query = f"{final_gender} {final_fabric} {final_material} {item_name}"
        
        # අපි බොත්තම ඔබන්න කලින් CIF එකත් අහගමු!
        st.markdown("### 💰 බදු ගණනය කිරීම සඳහා (Duty Calculator)")
        cif_value = st.number_input("භාණ්ඩයේ CIF වටිනාකම රුපියල් (LKR) වලින් ඇතුළත් කරන්න:", min_value=0.0, value=100000.0, step=1000.0)
        
        
        # මේක තමයි බොත්තම පටන් ගන්න තැන
        if st.button("🔍 සම්පූර්ණ රේගු වාර්තාව ගණනය කරන්න", type="primary"):
            with st.spinner("AI මොළය රේගු නීති සහ බදු පරීක්ෂා කරමින් පවතී... 📚"):
                
                try:
                    # 1. RAM එකෙන් දත්ත ගැනීම (පට්ට වේගවත් කෑල්ල)
                    tariff_database_text = load_tariff_data()
                    
                    if tariff_database_text is None:
                        st.error("tariff_62.csv.xlsx ෆයිල් එක හොයාගන්න බෑ මචං.")
                        st.stop()
                        
                    # 2. අලුත් RAG Prompt එක
                    hs_prompt = f"""
                    ඔබ ශ්‍රී ලංකාවේ ප්‍රවීණ රේගු නිලධාරියෙකි. පහත දැක්වෙන්නේ ශ්‍රී ලංකා රේගුවේ නිල තීරුබදු දත්ත ගබඩාවයි (Official Customs Tariff Data).

                    --- OFFICIAL TARIFF DATA ---
                    {tariff_database_text}
                    ----------------------------

                    පහත දැක්වෙන භාණ්ඩය සඳහා ඉහත දත්ත ගබඩාව (OFFICIAL TARIFF DATA) මත පමණක් පදනම්ව සම්පූර්ණ රේගු වාර්තාවක් සිංහලෙන් ලබා දෙන්න.

                    භාණ්ඩයේ විස්තරය: {final_query}
                    වියන ක්‍රමය: {weaving_method}
                    CIF වටිනාකම (LKR): {cif_value}

                    🚨 විශේෂ රේගු අවවාදය (STRICT RAG RULES): 
                    1. ඔබ අනුමාන කර අසත්‍ය HS කේත (Hallucinations) නිර්මාණය නොකළ යුතුය. 
                    2. ඉහත ලබා දී ඇති දත්ත ගබඩාව (OFFICIAL TARIFF DATA) පරීක්ෂා කර, භාණ්ඩයේ විස්තරයට සහ වියන ක්‍රමයට (උදා: Handloom ද Powerloom ද යන්න) හරියටම ගැළපෙන ඉලක්කම් 8 කින් යුත් HS කේතය (National Subdivision ද ඇතුළුව) සොයාගන්න. අගට XX යෙදීමෙන් වළකින්න.
                    3. අදාළ HS කේතයට අදාළව දත්ත ගබඩාවේ සඳහන් වී ඇති නිවැරදි බදු ප්‍රතිශතයන් පමණක් බදු වගුව සඳහා යොදාගන්න.

                    කරුණාකර පහත ව්‍යූහයට (Format) අනුව පමණක් පිළිතුර ලබා දෙන්න:
                    1. **නිවැරදි HS කේතය (8-digit):** අදාළ HS කේතය සහ විස්තරය.
                    2. **බදු ප්‍රතිශත වගුව:** (දත්ත ගබඩාවෙන් ලබාගත් නිවැරදි ප්‍රතිශතයන් පෙන්වන Markdown Table එකක්).
                    3. **බදු ගණනය කිරීම (Duty Calculator):** දී ඇති LKR {cif_value} CIF අගය මත පදනම්ව ගණනය කිරීම්.
                    4. **අවශ්‍ය බලපත්‍ර සහ අනුමැති (Licenses & Approvals):** ICL හෝ SLSI අවශ්‍යතාවය.
                    """
                    
                    # 3. AI එකෙන් උත්තරය ගැනීම
                    model = genai.GenerativeModel('models/gemini-flash-latest')
                    hs_response = model.generate_content(hs_prompt)
                    
                    st.success("🎉 රේගු වාර්තාව සාර්ථකව සකස් කරන ලදී!")
                    st.markdown(f"<div class='report-box'>{hs_response.text}</div>", unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"වාර්තාව සකස් කිරීමේදී ගැටලුවක් ආවා මචං: {e}")