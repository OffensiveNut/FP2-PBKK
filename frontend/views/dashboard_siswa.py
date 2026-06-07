import streamlit as st

# ==========================================
# 1. KONFIGURASI HALAMAN
# ==========================================
st.set_page_config(page_title="Dashboard Siswa - FastPresensi", layout="wide")


# ==========================================
# 2. DUMMY DATA (Panduan Integrasi Backend)
# ==========================================
# TODO (Backend): Ganti dictionary ini dengan response requests.get() dari FastAPI
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


# ==========================================
# 3. KOMPONEN UI UTAMA
# ==========================================

# --- HEADER SECTION ---
col_logo, col_logout, col_button = st.columns([9, 1, 1])

with col_logo:
    st.subheader("🎓 FastPresensi")

with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        # TODO (Backend): Tambahkan logika hapus token JWT dari session di sini
        st.session_state.clear()
        st.toast("Berhasil Logout!")

with col_button:
    if st.button("Go to Admin Dashboard", use_container_width=True):
        
        st.switch_page("views/dashboard_admin.py")

st.write("") 


# --- ONGOING CLASS & PRESENSI SECTION ---
with st.container(border=True):
    st.caption("Kelas yang sedang berlangsung")
    
    col_greet1, col_greet2 = st.columns(2)
    
    # Kiri: Info Kelas
    with col_greet1:
        st.write("") 
        st.subheader(f"**{data_kelas_berlangsung['kode']} - {data_kelas_berlangsung['nama']}**")
    
    # Kanan: Aksi Presensi & Izin
    with col_greet2:
        # Form Presensi Utama
        with st.form("form_absen", border=False):
            token_input = st.text_input("Masukkan Token Presensi", placeholder="Ketik token 6 digit...")
            
            submit_absen = st.form_submit_button("✅ Hadir", type="primary", use_container_width=True)
            
            if submit_absen:
                # TODO (Backend): Panggil fungsi POST /presensi menggunakan token_input
                if token_input:
                    st.success(f"Memproses presensi dengan token: {token_input}")
                else:
                    st.error("Token tidak boleh kosong!")
        
        # Form Izin 
        with st.expander("📄 Ajukan Izin (Upload Bukti)"):
            with st.form("form_izin", border=False):
                alasan_izin = st.text_area("Keterangan/Alasan")
                file_bukti = st.file_uploader("Upload Surat Keterangan", type=["pdf", "jpg", "png"])
                submit_izin = st.form_submit_button("Kirim Pengajuan", use_container_width=True)
                
                if submit_izin:
                    # TODO (Backend): Panggil fungsi POST /izin form-data
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

# TODO (Backend): Lakukan perulangan (for-loop) di sini berdasarkan response GET /jadwal
# Item Mata Kuliah 1 (Contoh)
st.markdown(f"**{data_kelas_berlangsung['kode']} | {data_kelas_berlangsung['nama']}**")
st.caption("📅 Senin &nbsp; | &nbsp; 🕒 07:00 - 08:50 &nbsp; | &nbsp; 🏢 TIF 113")

st.divider()