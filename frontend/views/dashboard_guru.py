import streamlit as st


st.set_page_config(page_title="Dashboard Guru - FastPresensi", layout="wide")

#dummy data
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

#tidak kepikiran tampilan jelasnya sementara dashboard guru hanya menampilkan tanggal dan semua list kelas yang ada

st.caption("Daftar Kuliah Anda")
st.subheader(data_user['semester_aktif'])
st.divider() 

# TODO (Backend): Lakukan perulangan (for-loop) di sini berdasarkan response GET /jadwal
# Item Mata Kuliah 1 (Contoh)
st.markdown(f"**{data_kelas_berlangsung['kode']} | {data_kelas_berlangsung['nama']}**")
st.caption("📅 Senin &nbsp; | &nbsp; 🕒 07:00 - 08:50 &nbsp; | &nbsp; 🏢 TIF 113")

st.divider()