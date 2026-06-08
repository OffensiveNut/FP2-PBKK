import streamlit as st

st.set_page_config(page_title="Dashboard Guru - FastPresensi", layout="wide")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🎓 FastPresensi")
    
    st.divider()
    
    menu_selection = st.radio(
        "Menu",
        ["Attendance", "Settings"],
        label_visibility="collapsed"
    )
    
    st.write("")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.rerun()

# --- CONTENT LOGIC ---
if menu_selection == "Attendance":
    st.subheader("Dashboard Guru")
    st.caption("Daftar Kuliah Anda")
    st.divider()
    
    # Placeholder konten dashboard guru
    st.markdown(f"**ER234405 | Interaksi Manusia dan Komputer (M)**")
    st.caption("📅 Senin &nbsp; | &nbsp; 🕒 07:00 - 08:50 &nbsp; | &nbsp; 🏢 TIF 113")
    st.divider()

else:
    st.info("Halaman **Settings** sedang dalam tahap pengembangan.")