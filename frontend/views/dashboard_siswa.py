import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Siswa - FastPresensi", layout="wide")

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

# Dummy data tambahan untuk list expander daftar kelas
daftar_kelas = [
    {
        "kode": "ER234405", 
        "nama": "Interaksi Manusia dan Komputer (M)", 
        "jadwal": "Senin | 07:00 - 08:50 | TIF 113", 
        "presensi": "Hadir 12 dari 14 Pertemuan"
    },
    {
        "kode": "ER234402", 
        "nama": "Konstruksi Perangkat Lunak (M)", 
        "jadwal": "Selasa | 09:00 - 11:30 | TIF 114", 
        "presensi": "Hadir 14 dari 14 Pertemuan"
    },
    {
        "kode": "ER234408", 
        "nama": "Kecerdasan Buatan", 
        "jadwal": "Kamis | 13:00 - 15:30 | TIF 105", 
        "presensi": "Hadir 10 dari 14 Pertemuan"
    }
]

# ==========================================
# 3. SIDEBAR NAVIGATION
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
        st.session_state.clear()
        st.rerun()

# ==========================================
# 4. KONTEN HALAMAN
# ==========================================
if menu_selection == "Attendance":
    # --- HEADER SECTION ---
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
            
            # Form izin utama untuk kelas yang sedang berlangsung
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

    # Implementasi List Expander untuk Setiap Mata Kuliah
    for kelas in daftar_kelas:
        with st.expander(f"🎒 **{kelas['kode']} | {kelas['nama']}**"):
            
            # Grid untuk Jadwal dan Riwayat Presensi
            col_jadwal, col_riwayat = st.columns(2)
            
            with col_jadwal:
                st.markdown("**📅 Jadwal & Lokasi**")
                st.caption(kelas['jadwal'])
                
            with col_riwayat:
                st.markdown("**📊 Riwayat Presensi**")
                st.caption(kelas['presensi'])
            
            st.divider()
            
            # Integrasi Form Izin di dalam Expander Kelas
            st.markdown("**📄 Ajukan Izin Susulan / Pra-Izin**")
            
            # Perhatikan tambahan parameter 'key' yang unik berdasarkan kode kelas
            with st.form(f"form_izin_riwayat_{kelas['kode']}", border=False):
                alasan_izin_riwayat = st.text_area("Keterangan/Alasan")
                file_bukti_riwayat = st.file_uploader("Upload Surat Keterangan", type=["pdf", "jpg", "png"])
                submit_izin_riwayat = st.form_submit_button("Kirim Pengajuan", use_container_width=True)
                
                if submit_izin_riwayat:
                    if file_bukti_riwayat:
                        st.info(f"File izin untuk {kelas['kode']} berhasil dilampirkan, mengirim ke server...")
                    else:
                        st.warning("Harap lampirkan file bukti terlebih dahulu.")

else:
    # --- SETTINGS PAGE ---
    st.subheader("Settings")
    st.info("Halaman **Settings** sedang dalam tahap pengembangan.")