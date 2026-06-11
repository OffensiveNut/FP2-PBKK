import uuid
from datetime import date

import streamlit as st

from utils.api_client import api_request

st.subheader("📚 Classes", divider=True)

today = date.today()


def _is_active(s: dict) -> bool:
    mulai = s.get("tanggal_mulai", "")
    selesai = s.get("tanggal_selesai", "")
    try:
        return date.fromisoformat(mulai) <= today <= date.fromisoformat(selesai)
    except Exception:
        return False


# ─── Semester Config ─────────────────────────────────────────────
with st.expander("📅 Semester Config", expanded=False):
    success, semesters = api_request("GET", "/semester/")
    if success and semesters:
        for s in semesters:
            c1, c2, c3, c4 = st.columns([3, 2, 1, 1])
            c1.write(f"**{s['nama_semester']}**")
            c2.write(s["tanggal_mulai"] + " — " + s["tanggal_selesai"])
            c3.write("✅ Aktif" if _is_active(s) else "❌ Tidak aktif")
            with c4:
                if st.button("Edit", key=f"sem_edit_{s['id']}"):
                    st.session_state.edit_semester = s

        if st.button("➕ Tambah Semester"):
            st.session_state.edit_semester = {"id": None, "nama_semester": "", "tanggal_mulai": str(today), "tanggal_selesai": str(today)}
    else:
        st.info("Belum ada semester. Buat semester baru.")

    edit_target = st.session_state.get("edit_semester")
    if edit_target:
        is_new = edit_target.get("id") is None
        with st.form("form_semester", border=True):
            nama = st.text_input("Nama Semester", value=edit_target.get("nama_semester", ""))
            mulai = st.date_input("Tanggal Mulai", value=date.fromisoformat(edit_target.get("tanggal_mulai", str(today))))
            selesai = st.date_input("Tanggal Selesai", value=date.fromisoformat(edit_target.get("tanggal_selesai", str(today))))
            c1, c2 = st.columns([1, 1])
            if c1.form_submit_button("💾 Simpan", type="primary", use_container_width=True):
                payload = {"nama_semester": nama, "tanggal_mulai": str(mulai), "tanggal_selesai": str(selesai)}
                if is_new:
                    ok, _ = api_request("POST", "/semester/", json=payload)
                else:
                    ok, _ = api_request("PUT", f"/semester/{edit_target['id']}", json=payload)
                if ok:
                    st.success("Semester disimpan")
                    st.session_state.edit_semester = None
                    st.rerun()
                else:
                    st.error(_)
            if c2.form_submit_button("Batal", use_container_width=True):
                st.session_state.edit_semester = None
                st.rerun()

# ─── Class List ─────────────────────────────────────────────────
st.write("")
success, kelas_list = api_request("GET", "/kelas/")

if not success:
    st.warning(kelas_list)
    st.stop()

c_search, c_add = st.columns([3, 1])
with c_add:
    if st.button("➕ Tambah Kelas", type="primary", use_container_width=True):
        st.session_state.show_add_kelas = True

if st.session_state.get("show_add_kelas"):
    with st.form("form_kelas", border=True):
        nama = st.text_input("Nama Kelas")
        deskripsi = st.text_area("Deskripsi")
        if st.form_submit_button("Simpan"):
            ok, _ = api_request("POST", "/kelas/", json={
                "nama_kelas": nama, "deskripsi": deskripsi,
            })
            if ok:
                st.success("Kelas dibuat")
                st.session_state.show_add_kelas = False
                st.rerun()

for k in (kelas_list or []):
    with st.expander(f"**{k['nama_kelas']}**"):
        c1, c2 = st.columns(2)
        c1.write(f"Deskripsi: {k.get('deskripsi', '-')}")
        with c2:
            if st.button("🗑️ Hapus", key=f"del_kelas_{k['id']}"):
                ok, _ = api_request("DELETE", f"/kelas/{k['id']}")
                if ok:
                    st.success("Kelas dihapus")
                    st.rerun()

        # ── Atur Guru ──
        with st.container(border=True):
            st.markdown("**👨‍🏫 Atur Guru**")
            success, guru_list = api_request("GET", "/users/", params={"role": "GURU"})
            if success and guru_list:
                selected = st.selectbox("Tambah Guru", guru_list, format_func=lambda g: f"{g['nama_lengkap']} ({g['username']})", key=f"guru_sel_{k['id']}")
                if st.button("Tambah", key=f"guru_add_{k['id']}"):
                    ok, _ = api_request("POST", f"/kelas/{k['id']}/guru", json={"user_id": selected["id"]})
                    if ok:
                        st.success("Guru ditambahkan")
                        st.rerun()

        # ── Atur Siswa ──
        with st.container(border=True):
            st.markdown("**👨‍🎓 Atur Siswa**")
            success, siswa_list = api_request("GET", "/users/", params={"role": "SISWA"})
            if success and siswa_list:
                selected = st.selectbox("Tambah Siswa", siswa_list, format_func=lambda s: f"{s['nama_lengkap']} ({s['username']})", key=f"siswa_sel_{k['id']}")
                if st.button("Tambah", key=f"siswa_add_{k['id']}"):
                    ok, _ = api_request("POST", f"/kelas/{k['id']}/siswa", json={"user_id": selected["id"]})
                    if ok:
                        st.success("Siswa ditambahkan")
                        st.rerun()

        # ── Atur Jadwal ──
        with st.container(border=True):
            st.markdown("**🕐 Atur Jadwal**")
            success, jadwal_list = api_request("GET", f"/kelas/{k['id']}/jadwal")
            if success and jadwal_list:
                for j in jadwal_list:
                    st.write(f"{j['hari']} {j['waktu_mulai']} — {j['waktu_selesai']}")
            with st.form(key=f"jadwal_form_{k['id']}", border=False):
                hari = st.selectbox("Hari", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"], key=f"hari_{k['id']}")
                mulai = st.time_input("Waktu Mulai", key=f"mulai_{k['id']}")
                selesai = st.time_input("Waktu Selesai", key=f"selesai_{k['id']}")
                if st.form_submit_button("Tambah Jadwal"):
                    ok, _ = api_request("POST", f"/kelas/{k['id']}/jadwal", json={
                        "hari": hari, "waktu_mulai": str(mulai), "waktu_selesai": str(selesai),
                    })
                    if ok:
                        st.success("Jadwal ditambahkan")
                        st.rerun()

        # ── Generate Pertemuan ──
        if st.button("🤖 Generate Pertemuan", key=f"gen_{k['id']}", type="primary"):
            ok, result = api_request("POST", f"/pertemuan/generate/{k['id']}")
            if ok:
                st.success(f"{result['jumlah_pertemuan']} pertemuan berhasil dibuat")
                st.rerun()
            else:
                st.error(result)
