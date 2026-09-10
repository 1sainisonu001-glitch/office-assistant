import streamlit as st
from PIL import Image, ImageEnhance, ImageFilter
import pytesseract
from otp_service import OTPService
from db_manager import DatabaseManager

# पेज कॉन्फ़िगरेशन
st.set_page_config(
    page_title="AI Document & Office Assistant",
    page_icon="📄",
    layout="centered"
)

DatabaseManager.init_db()

# कस्टम हेडर स्टाइल
st.markdown("""
<style>
    .main-title { text-align: center; color: #1e3a8a; margin-bottom: 2px; }
    .subtitle { text-align: center; color: #64748b; font-size: 14px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

def check_auth():
    if st.session_state.get("authenticated", False):
        return True

    st.markdown("<h2 class='main-title'>🔐 AI Office Assistant</h2>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>सुरक्षित लॉगिन सिस्टम</p>", unsafe_allow_html=True)

    tab_otp, tab_pin = st.tabs(["📱 मोबाइल OTP", "🔑 सुरक्षा PIN"])

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

        otp_val = st.text_input("6-अंकीय OTP", placeholder="••••••", max_chars=6)
        if st.button("लॉगिन करें 🚀", type="primary", use_container_width=True):
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
