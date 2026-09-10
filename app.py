import streamlit as st
from PIL import Image, ImageEnhance
import pytesseract
from otp_service import OTPService
from db_manager import DatabaseManager

# 1. पेज कॉन्फ़िगरेशन
st.set_page_config(
    page_title="AI Document & Office Assistant",
    page_icon="📄",
    layout="centered"
)

# डेटाबेस शुरू करें
DatabaseManager.init_db()

# कस्टम हेडर स्टाइल
st.markdown("""
<style>
    .main-title { text-align: center; color: #1e3a8a; margin-bottom: 2px; }
    .subtitle { text-align: center; color: #64748b; font-size: 14px; margin-bottom: 20px; }
    .stButton>button { border-radius: 8px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# 2. सुरक्षा व लॉगिन फ़ंक्शन
def check_auth():
    if st.session_state.get("authenticated", False):
        return True

    st.markdown("<h2 class='main-title'>AI Office Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>सुरक्षित लॉगिन सिस्टम</p>", unsafe_allow_html=True)

    tab_otp, tab_pin = st.tabs(["मोबाइल OTP", "सुरक्षा PIN"])

    with tab_otp:
        col_phone, col_btn = st.columns([2, 1])
        with col_phone:
            phone = st.text_input("मोबाइल नंबर", placeholder="9876543210", max_chars=10)
        with col_btn:
            st.write("")
            st.write("")
            if st.button("OTP भेजें", use_container_width=True):
                ok, msg = OTPService.dispatch_otp(phone)
                if ok:
                    st.success(msg)
                else:
                    st.error(msg)

        otp_val = st.text_input("6-अंकीय OTP", placeholder="123456", max_chars=6)
        if st.button("लॉगिन करें", type="primary", use_container_width=True):
            ok, msg = OTPService.verify_otp(otp_val)
            if ok:
                st.session_state["authenticated"] = True
                user = DatabaseManager.get_or_create_user(phone or "User")
                st.session_state["user_name"] = user["full_name"]
                st.rerun()
            else:
                st.error(msg)

    with tab_pin:
        pin = st.text_input("मास्टर PIN (डिफ़ॉल्ट: 1234)", type="password")
        if st.button("PIN से लॉगिन", use_container_width=True):
            if pin in ["1234", "office2026"]:
                st.session_state["authenticated"] = True
                st.session_state["user_name"] = "Sonu Saini (Admin)"
                st.rerun()
            else:
                st.error("गलत PIN दर्ज किया गया!")

    return False

if not check_auth():
    st.stop()

# 3. मुख्य ऐप (लॉगिन के बाद)
with st.sidebar:
    st.markdown(f"**यूज़र:** {st.session_state.get('user_name', 'Sonu Saini')}")
    st.markdown("**स्थिति:** ऑनलाइन")
    if st.button("लॉगआउट", use_container_width=True):
        st.session_state.clear()
        st.rerun()

st.markdown("<h2 class='main-title'>AI Document Scanner & OCR</h2>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>दस्तावेज़ की फोटो अपलोड करें और हिंदी व अंग्रेज़ी टेक्स्ट निकालें</p>", unsafe_allow_html=True)

# भाषा चयन
ocr_lang = st.radio(
    "दस्तावेज़ की भाषा चुनें:",
    ["हिंदी + English", "केवल English", "केवल हिंदी"],
    horizontal=True
)

if "हिंदी + English" in ocr_lang:
    lang_code = "hin+eng"
elif "हिंदी" in ocr_lang:
    lang_code = "hin"
else:
    lang_code = "eng"

uploaded = st.file_uploader("दस्तावेज़ की फोटो चुनें (JPG / PNG)", type=["png", "jpg", "jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="अपलोड किया गया दस्तावेज़", use_container_width=True)

    if st.button("OCR टेक्स्ट निकालें", type="primary", use_container_width=True):
        with st.spinner("OCR इंजन दस्तावेज़ पढ़ रहा है..."):
            try:
                # इमेज को साफ करें
                gray_img = img.convert('L')
                enhancer = ImageEnhance.Contrast(gray_img)
                enhanced_img = enhancer.enhance(1.5)

                # Tesseract OCR चलाएँ
                extracted_text = pytesseract.image_to_string(enhanced_img, lang=lang_code)

                if extracted_text.strip():
                    st.success("OCR सफलतापूर्वक पूरा हुआ!")
                    st.text_area("निकाला गया टेक्स्ट:", extracted_text, height=220)
                    st.download_button(
                        "टेक्स्ट फ़ाइल (.txt) डाउनलोड करें",
                        extracted_text,
                        file_name="extracted_document.txt",
                        use_container_width=True
                    )
                else:
                    # यदि पहली बार में खाली मिले तो सामान्य इमेज से प्रयास
                    fallback_text = pytesseract.image_to_string(img, lang="eng")
                    if fallback_text.strip():
                        st.success("OCR पूरा हुआ (मूल इमेज से):")
                        st.text_area("निकाला गया टेक्स्ट:", fallback_text, height=220)
                    else:
                        st.warning("फोटो में कोई स्पष्ट अक्षर नहीं मिले। कृपया साफ़ रोशनी वाली फोटो अपलोड करें।")

            except Exception as e:
                st.error(f"OCR इंजन त्रुटि: {str(e)}")
                st.info
