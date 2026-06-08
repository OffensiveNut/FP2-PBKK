import streamlit as st
from utils.api_client import api_login


st.set_page_config(page_title="Login - FastPresensi", layout="centered")

with st.container(border=True):
    st.subheader("🔐 Login FastPresensi")
    
    with st.form("form_login", border=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login", type="primary", use_container_width=True)
        
        if submit_login:
            if not username or not password:
                st.warning("⚠️ Silakan isi username dan password terlebih dahulu.")
            else:
                with st.spinner("Memeriksa kredensial..."):
                    
                    # ==========================================
                    # T🚀  BYPASS LOGIN
                    # ==========================================
                    uname_lower = username.lower()
                    if uname_lower in ["admin", "guru", "siswa"]:
                        # Langsung buat sesi palsu tanpa nembak API
                        st.session_state["access_token"] = "token_palsu_untuk_ui_testing"
                        st.session_state["user_data"] = {"role": uname_lower.upper()}
                        
                        st.success(f"✅ Bypass mode: Masuk sebagai {uname_lower.upper()}...")
                        st.rerun()
                        
                    # ==========================================
                    # 🔒 REAL CODE LOGIC
                    # ==========================================
                    else:
                        is_success, result = api_login(username, password)
                        
                        if is_success:
                            st.session_state["access_token"] = result["access_token"]
                            st.session_state["user_data"] = result["user"]
                            st.success("✅ Login berhasil! Mengarahkan ke dashboard...")
                            st.rerun()
                        else:
                            st.error(f"❌ {result}")