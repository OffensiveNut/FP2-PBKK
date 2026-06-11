import streamlit as st

from utils.api_client import api_login
from utils.state import login

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
                    is_success, result = api_login(username, password)

                    if is_success:
                        if not isinstance(result, dict):
                            st.error("Format respons tidak valid")
                            st.stop()

                        login(result["access_token"], result["user"])
                        st.success("✅ Login berhasil!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
