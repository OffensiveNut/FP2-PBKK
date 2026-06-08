import streamlit as st
import pandas as pd
import random

# ==========================================
# 1. KONFIGURASI HALAMAN & STATE
# ==========================================
st.set_page_config(page_title="Dashboard Guru - FastPresensi", layout="wide")

# Inisialisasi state untuk melacak tampilan
if "selected_class" not in st.session_state:
    st.session_state.selected_class = None

if "active_token" not in st.session_state:
    st.session_state.active_token = None

# ==========================================
# 2. DUMMY DATA
# ==========================================
data_user = {
    "nama": "Budi Santoso, M.Kom.",
    "semester_aktif": "Semester Genap 2025/2026"
}

data_kelas_berlangsung = {
    "kode": "ER234405",
    "nama": "Interaksi Manusia dan Komputer (M)"
}

daftar_kelas = [
    {
        "kode": "ER234405", 
        "nama": "Interaksi Manusia dan Komputer (M)", 
        "jadwal": "Senin | 07:00 - 08:50 | TIF 113", 
        "dosen": "Hadziq Fabroyir, S.Kom., Ph.D."
    },
    {
        "kode": "ER234402", 
        "nama": "Konstruksi Perangkat Lunak (M)", 
        "jadwal": "Selasa | 09:00 - 11:30 | TIF 114", 
        "dosen": "Siska Arifiani, S.Kom., M.Kom."
    }
]

dummy_live_attendance = pd.DataFrame([
    {"NIM": "10293847", "Student Name": "Amanda Ripley", "Time": "08:02 AM", "Status": "HADIR"},
    {"NIM": "10293848", "Student Name": "David Bowman", "Time": "08:15 AM", "Status": "TELAT"},
    {"NIM": "10293849", "Student Name": "Ellen Ripley", "Time": "-", "Status": "ALPA"},
    {"NIM": "10293850", "Student Name": "Frank Poole", "Time": "08:00 AM", "Status": "HADIR"}
])

dummy_rekap_siswa = pd.DataFrame([
    {"NIM": "10293847", "Student Name": "Amanda Ripley", "Status": "HADIR"},
    {"NIM": "10293848", "Student Name": "David Bowman", "Status": "TELAT"},
    {"NIM": "10293849", "Student Name": "Ellen Ripley", "Status": "ALPA"},
    {"NIM": "10293850", "Student Name": "Frank Poole", "Status": "HADIR"},
    {"NIM": "10293851", "Student Name": "Sarah Jenkins", "Status": "IZIN"}
])

# ==========================================
# 3. FUNGSI RENDER DETAIL FULL SCREEN
# ==========================================
def render_detail_kelas(kelas):
    col_back, col_export = st.columns([8, 2])
    with col_back:
        if st.button("⬅️ Kembali ke Dashboard"):
            st.session_state.selected_class = None
            st.rerun()
    with col_export:
        st.button("📥 Export CSV", use_container_width=True, type="primary")
    
    st.write("")
    st.markdown(f"### <span style='background-color:#1E3A8A; color:white; padding:4px; border-radius:4px;'>{kelas['kode']}</span> {kelas['nama']}", unsafe_allow_html=True)
    st.caption(f"📅 {kelas['jadwal'].split(' | ')[0]} 🕒 {kelas['jadwal'].split(' | ')[1]}")
    st.divider()
    
    c_hadir, c_izin, c_sakit, c_alpa, c_total = st.columns(5)
    with c_hadir: st.metric("HADIR", "14")
    with c_izin: st.metric("IZIN", "0")
    with c_sakit: st.metric("SAKIT", "0")
    with c_alpa: st.metric("ALPA", "1")
    with c_total: st.metric("TOTAL MAHASISWA", "15")
    
    st.divider()
    st.subheader("Daftar Mahasiswa & Mark Manual")
    st.caption("Pilih status kehadiran secara manual jika presensi token gagal atau ada perubahan.")
    
    h1, h2, h3, h4 = st.columns([1, 2, 1, 3])
    h1.write("**NIM**")
    h2.write("**Nama Mahasiswa**")
    h3.write("**Status Saat Ini**")
    h4.write("**Mark Manual**")
    st.divider()
    
    for index, row in dummy_rekap_siswa.iterrows():
        c1, c2, c3, c4 = st.columns([1, 2, 1, 3])
        c1.write(row['NIM'])
        c2.write(row['Student Name'])
        c3.caption(f"**{row['Status']}**")
        
        with c4:
            b1, b2, b3, b4 = st.columns(4)
            with b1: 
                if st.button("H", key=f"H_{row['NIM']}", help="Hadir"): pass
            with b2: 
                if st.button("I", key=f"I_{row['NIM']}", help="Izin"): pass
            with b3: 
                if st.button("S", key=f"S_{row['NIM']}", help="Sakit"): pass
            with b4: 
                if st.button("A", key=f"A_{row['NIM']}", help="Alpa"): pass
        st.divider()

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("🎓 FastPresensi")
    st.caption("GURU CONSOLE")
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

# ==========================================
# 5. KONTEN HALAMAN UTAMA
# ==========================================
if menu_selection == "Attendance":
    
    if st.session_state.selected_class is not None:
        render_detail_kelas(st.session_state.selected_class)
        
    else:
        st.subheader("👨‍🏫 Dashboard Guru")
        st.write("") 

        # --- ONGOING CLASS & LIVE ATTENDANCE ---
        with st.container(border=True):
            st.caption("🔴 Live Attendance (Sesi Berlangsung)")
            st.subheader(f"**{data_kelas_berlangsung['kode']} - {data_kelas_berlangsung['nama']}**")
            st.divider()
            
            col_token, col_live = st.columns([1.5, 2.5])
            
            with col_token:
                # Blok 1: Form Pembuatan Sesi Baru
                with st.container(border=True):
                    st.markdown("#### ⊕ New Session (Pertemuan)")
                    st.write("")
                    
                    st.text_input("DESCRIPTION", placeholder="e.g. Advanced Mathematics Lec 4")
                    st.selectbox("SESSION TYPE", ["Offline (Tatap Muka)", "Online (Daring)", "Hybrid"])
                    st.time_input("END TIME (WAKTU SELESAI)")
                    
                    st.write("")
                    if st.button("Generate Token", type="primary", use_container_width=True):
                        st.session_state.active_token = f"{random.randint(100, 999)} {random.randint(100, 999)}"
                        st.rerun()
                        
                st.write("") # Spacer antar blok
                
                # Blok 2: Tampilan Token Aktif
                with st.container(border=True):
                    st.markdown("<div style='text-align: center; font-size: 0.8rem; font-weight: bold; color: gray; margin-bottom: 10px;'>ACTIVE ATTENDANCE TOKEN</div>", unsafe_allow_html=True)
                    
                    if st.session_state.active_token:
                        st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>{st.session_state.active_token}</h1>", unsafe_allow_html=True)
                        st.markdown("<div style='text-align: center; color: gray; font-size: 0.9rem;'>⏱️ Expires in 45:20</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<h1 style='text-align: center; color: gray; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>--- ---</h1>", unsafe_allow_html=True)
                        st.write("")
                            
            with col_live:
                st.caption("📋 Live Attendance Report")
                st.dataframe(dummy_live_attendance, use_container_width=True, hide_index=True)


        # --- DAFTAR KULIAH SECTION (CLASS LIST) ---
        st.write("") 
        st.caption("📚 Daftar Kuliah Anda")
        st.subheader(data_user['semester_aktif'])
        st.divider() 

        for kelas in daftar_kelas:
            with st.container(border=True):
                col_info, col_btn = st.columns([8, 2])
                
                with col_info:
                    st.markdown(f"**{kelas['kode']} | {kelas['nama']}**")
                    st.caption(f"📅 {kelas['jadwal']}")
                    
                with col_btn:
                    if st.button("Lihat Detail Kelas", key=f"btn_detail_{kelas['kode']}", use_container_width=True):
                        st.session_state.selected_class = kelas
                        st.rerun()

else:
     # ==========================================
    # --- HALAMAN SETTINGS (Sama untuk semua role) ---
    # ==========================================
    st.subheader("⚙️ Account Settings")
    st.caption("Kelola informasi profil, email, dan keamanan akun Anda.")
    st.divider()

    # Data Dummy User (Bisa dihubungkan dengan st.session_state["user_data"] nantinya)
    dummy_profile = {
        "full_name": "Jovan Oberto Mishael Sinaga",
        "username": "jovanoberto",
        "email": "jovan@fastpresensi.edu",
        "phone": "+62 812-3456-7890",
        "role": "SISWA" # Akan dinamis tergantung siapa yang login
    }

    # Membagi layout menjadi dua kolom utama
    col_profile, col_security = st.columns([1.2, 1])

    # --- KOLOM KIRI: EDIT PROFIL ---
    with col_profile:
        st.markdown("**👤 Informasi Profil**")
        with st.container(border=True):
            # Gunakan st.form agar halaman tidak refresh setiap kali mengetik satu huruf
            with st.form("form_edit_profile", border=False):
                # Field Role dibuat disabled karena user tidak boleh ganti role sendiri
                st.text_input("Role Akun", value=dummy_profile["role"], disabled=True)
                
                st.text_input("Nama Lengkap", value=dummy_profile["full_name"])
                st.text_input("Username", value=dummy_profile["username"])
                
                c_email, c_phone = st.columns(2)
                with c_email:
                    st.text_input("Email", value=dummy_profile["email"])
                with c_phone:
                    st.text_input("Nomor Telepon", value=dummy_profile["phone"])
                
                st.write("")
                submit_profile = st.form_submit_button("Simpan Perubahan Profil", type="primary")
                
                if submit_profile:
                    # TODO: Panggil API PUT /user/profile di sini
                    st.success("✅ Informasi profil berhasil diperbarui!")

    # --- KOLOM KANAN: SECURITY & PREFERENCES ---
    with col_security:
        st.markdown("**🔒 Keamanan (Ganti Password)**")
        with st.container(border=True):
            with st.form("form_edit_password", border=False):
                st.text_input("Password Saat Ini", type="password", placeholder="Masukkan password lama...")
                st.text_input("Password Baru", type="password", placeholder="Minimal 8 karakter")
                st.text_input("Konfirmasi Password Baru", type="password")
                
                st.write("")
                submit_password = st.form_submit_button("Update Password", type="primary")
                
                if submit_password:
                    # TODO: Panggil API PUT /user/password di sini
                    st.success("✅ Password berhasil diubah!")
        
        st.write("")
       