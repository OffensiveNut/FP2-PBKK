import streamlit as st


st.set_page_config(page_title="login - FastPresensi", layout="centered")



with st.container(border=True):
    st.subheader("🔐 Login FastPresensi")
    with st.form("form_login", border=False):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit_login = st.form_submit_button("Login")
        
    