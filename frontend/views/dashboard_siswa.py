import streamlit as st
import pandas as pd

# ==========================================
# 1. KONFIGURASI HALAMAN & STATE
# ==========================================
st.set_page_config(page_title="Dashboard Siswa - FastPresensi", layout="wide")

# Inisialisasi state untuk melacak apakah user sedang melihat detail kelas atau tidak
if "selected_class" not in st.session_state:
    st.session_state.selected_class = None

# ==========================================
# 2. DUMMY DATA
# ==========================================
data_user = {
    "nama": "Jovan Oberto Mishael Sinaga",
    "semester_aktif": "Semester Genap 2025/2026"
}

data_kelas_berlangsung = {
    "kode": "ER234405",
    "nama": "Interaksi Manusia dan Komputer (M)"
}

data_info_dashboard = {
    "tanggal_hari_ini": "Kamis, 4 Juni 2026",
    "pekan_ke": "14",
    "kelas_mendatang": "ER234402 - Konstruksi Perangkat Lunak (M)"
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

dummy_riwayat_pertemuan = pd.DataFrame([
    {"Tatap Muka": 1, "Jadwal": "Senin, 23 Februari 2026\n07.30 - 09.50\nTIF 113", "Status": "HADIR"},
    {"Tatap Muka": 2, "Jadwal": "Senin, 2 Maret 2026\n07.30 - 09.50\nTIF 113", "Status": "HADIR"},
    {"Tatap Muka": 3, "Jadwal": "Senin, 9 Maret 2026\n07.30 - 09.50\nTIF 113", "Status": "HADIR"},
    {"Tatap Muka": 4, "Jadwal": "Senin, 16 Maret 2026\n07.30 - 09.50\nTIF 113", "Status": "IZIN"},
    {"Tatap Muka": 5, "Jadwal": "Senin, 30 Maret 2026\n07.30 - 09.50\nTIF 113", "Status": "HADIR"},
    {"Tatap Muka": 6, "Jadwal": "Senin, 6 April 2026\n07.30 - 09.50\nTIF 113", "Status": "ALPA"}
])

# ==========================================
# 3. FUNGSI RENDER DETAIL FULL SCREEN
# ==========================================
# Perhatikan: Tidak ada lagi @st.dialog. Ini sekarang fungsi render biasa.
def render_detail_kelas(kelas):
    # Tombol Kembali
    if st.button("⬅️ Kembali ke Daftar Kelas"):
        st.session_state.selected_class = None
        st.rerun() # Refresh untuk memunculkan dashboard utama kembali
    
    st.write("")
    
    # Header Info Kelas
    st.markdown(f"### <span style='background-color:#1E3A8A; color:white; padding:4px; border-radius:4px;'>{kelas['kode']}</span> {kelas['nama']}", unsafe_allow_html=True)
    st.caption(f"📅 {kelas['jadwal'].split(' | ')[0]} 🕒 {kelas['jadwal'].split(' | ')[1]}")
    st.write(f"**Dosen:**\n{kelas['dosen']}")
    
    st.write("")
    st.caption("*Data rekapitulasi kehadiran diperbarui pukul 00.00 WIB setiap harinya.*")
    st.divider()
    
    # Grid Metrik Rekap Kehadiran
    c_hadir, c_izin, c_sakit, c_alpa, c_total = st.columns(5)
    with c_hadir: st.metric("HADIR", "4")
    with c_izin: st.metric("IZIN", "1")
    with c_sakit: st.metric("SAKIT", "0")
    with c_alpa: st.metric("ALPA", "1")
    with c_total: st.metric("TOTAL TATAP MUKA TERLAKSANA", "6")
    
    st.divider()
    
    # Bagian Tabel Riwayat
    st.caption("*Catatan: Surat izin tidak hadir diunggah maksimal sebelum kelas berakhir.*")
    st.dataframe(
        dummy_riwayat_pertemuan, 
        use_container_width=True,
        hide_index=True
    )
    
    st.divider()
    
    # Form Upload Izin
    with st.expander("📄 Ajukan Izin "):
        with st.form(f"form_izin_riwayat_{kelas['kode']}", border=False):
            alasan_izin = st.text_area("Keterangan/Alasan")
            file_bukti = st.file_uploader("Upload Surat Keterangan", type=["pdf", "jpg", "png"])
            submit_izin = st.form_submit_button("Kirim Pengajuan", use_container_width=True)
            
            if submit_izin:
                if file_bukti:
                    st.success(f"Pengajuan izin untuk {kelas['kode']} berhasil dikirim!")
                else:
                    st.warning("Harap lampirkan file bukti terlebih dahulu.")

# ==========================================
# 4. SIDEBAR NAVIGATION
# ==========================================
with st.sidebar:
    st.title("🎓 FastPresensi")
    st.caption("SISWA CONSOLE")
    st.divider()
    
    menu_selection = st.radio(
        "Menu",
        ["Attendance", "Settings"],
        label_visibility="collapsed"
    )
    
    st.write("")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear() # Ini juga akan menghapus state selected_class
        st.rerun()

# ==========================================
# 5. KONTEN HALAMAN
# ==========================================
if menu_selection == "Attendance":
    
    # === LOGIKA VIEW SWITCHING ===
    # Jika user sedang memilih kelas, HANYA render detail kelasnya (Full Screen Effect)
    if st.session_state.selected_class is not None:
        render_detail_kelas(st.session_state.selected_class)
        
    # Jika TIDAK ada kelas yang dipilih, render dashboard utama seperti biasa
    else:
        st.subheader("🎓 Dashboard Siswa")
        st.write("") 

        # --- ONGOING CLASS & PRESENSI SECTION ---
        with st.container(border=True):
            st.caption("Kelas yang sedang berlangsung")
            col_greet1, col_greet2 = st.columns(2)
            
            with col_greet1:
                st.write("") 
                st.subheader(f"**{data_kelas_berlangsung['kode']} - {data_kelas_berlangsung['nama']}**")
            
            with col_greet2:
                with st.form("form_absen", border=False):
                    token_input = st.text_input("Masukkan Token Presensi", placeholder="Ketik token 6 digit...")
                    submit_absen = st.form_submit_button("✅ Hadir", type="primary", use_container_width=True)
                    
                    if submit_absen:
                        if token_input:
                            st.success(f"Memproses presensi dengan token: {token_input}")
                        else:
                            st.error("Token tidak boleh kosong!")
                
                with st.expander("📄 Ajukan Izin (Upload Bukti)"):
                    with st.form("form_izin_berlangsung", border=False):
                        alasan_izin = st.text_area("Keterangan/Alasan")
                        file_bukti = st.file_uploader("Upload Surat Keterangan", type=["pdf", "jpg", "png"])
                        submit_izin = st.form_submit_button("Kirim Pengajuan", use_container_width=True)
                        
                        if submit_izin:
                            if file_bukti:
                                st.info("File berhasil dilampirkan, mengirim ke server...")
                            else:
                                st.warning("Harap lampirkan file bukti terlebih dahulu.")

        # --- INFO CARDS SECTION ---
        st.write("")
        col_info1, col_info2 = st.columns(2)
        with col_info1:
            with st.container(border=True):
                st.caption(f"Hari ini: {data_info_dashboard['tanggal_hari_ini']}")
                st.markdown(f"**Pekan Perkuliahan ke-{data_info_dashboard['pekan_ke']}**")
        with col_info2:
            with st.container(border=True):
                st.caption("Kuliah yang akan datang")
                st.markdown(f"**{data_info_dashboard['kelas_mendatang']}**")

        # --- DAFTAR KULIAH SECTION ---
        st.write("") 
        st.caption("Daftar Kuliah Anda")
        st.subheader(data_user['semester_aktif'])
        st.divider() 

        for kelas in daftar_kelas:
            with st.container(border=True):
                col_info, col_btn = st.columns([8, 2])
                
                with col_info:
                    st.markdown(f"**{kelas['kode']} | {kelas['nama']}**")
                    
                with col_btn:
                    # Jika tombol diklik, set state kelas yang dipilih dan refresh UI
                    if st.button("Lihat Detail", key=f"btn_detail_{kelas['kode']}", use_container_width=True):
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
       