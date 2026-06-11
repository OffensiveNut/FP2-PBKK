import streamlit as st


def init_session() -> None:
    if "access_token" not in st.session_state:
        st.session_state.access_token = None
        st.session_state.user_data = None


def login(token: str, user_data: dict) -> None:
    st.session_state.access_token = token
    st.session_state.user_data = user_data


def logout() -> None:
    st.session_state.clear()
    st.rerun()


def get_user() -> dict:
    return st.session_state.get("user_data") or {}


def get_role() -> str | None:
    user = get_user()
    return user.get("role") if user else None


def is_guru_or_admin() -> bool:
    role = get_role()
    return role in ("GURU", "ADMIN")
