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

sems_ok, semesters = api_request("GET", "/semester/")
semester_options = {s["nama_semester"]: s["id"] for s in (semesters or [])}
semester_names = list(semester_options.keys()) if sems_ok else []

c_search, c_add = st.columns([3, 1])
with c_add:
    if st.button("➕ Tambah Kelas", type="primary", use_container_width=True):
        st.session_state.show_add_kelas = True

if st.session_state.get("show_add_kelas"):
    with st.form("form_kelas", border=True):
        nama = st.text_input("Nama Kelas")
        deskripsi = st.text_area("Deskripsi")
        if semester_names:
            sem_nama = st.selectbox("Semester", semester_names)
            sem_id = semester_options[sem_nama]
        else:
            st.warning("Buat semester terlebih dahulu")
            sem_id = None
        if st.form_submit_button("Simpan", disabled=not bool(sem_id)):
            ok, _ = api_request("POST", "/kelas/", json={
                "nama_kelas": nama, "deskripsi": deskripsi, "semester_id": str(sem_id),
            })
            if ok:
                st.success("Kelas dibuat")
                st.session_state.show_add_kelas = False
                st.rerun()

for k in (kelas_list or []):
    with st.expander(f"**{k['nama_kelas']}**"):
        okd, detail = api_request("GET", f"/kelas/{k['id']}")
        gurus = detail.get("gurus", []) if okd else []
        siswas = detail.get("siswas", []) if okd else []

        c1, c2 = st.columns(2)
        c1.write(f"Deskripsi: {k.get('deskripsi', '-')}")
        with c2:
            if st.button("🗑️ Hapus", key=f"del_kelas_{k['id']}"):
                api_request("DELETE", f"/kelas/{k['id']}")
                st.rerun()

        # ── Atur Guru ──
        with st.container(border=True):
            guru_ids = {g["id"] for g in gurus}
            st.markdown(f"**👨‍🏫 Guru ({len(gurus)})**")
            for g in gurus:
                cols = st.columns([3, 1])
                cols[0].write(f"{g['nama_lengkap']} ({g['username']})")
                if cols[1].button("🗑️", key=f"guru_rm_{k['id']}_{g['id']}"):
                    api_request("DELETE", f"/kelas/{k['id']}/guru/{g['id']}")
                    st.rerun()

            if st.button("➕ Tambah Guru", key=f"guru_tmbh_{k['id']}"):
                key = f"show_guru_add_{k['id']}"
                st.session_state[key] = not st.session_state.get(key, False)

            if st.session_state.get(f"show_guru_add_{k['id']}"):
                all_ok, all_gurus = api_request("GET", "/users/", params={"role": "GURU"})
                if all_ok and all_gurus:
                    available = [g for g in all_gurus if g["id"] not in guru_ids]
                    names = {f"{g['nama_lengkap']} ({g['username']})": g["id"] for g in available}
                    selected = st.multiselect("Pilih Guru", list(names.keys()), key=f"guru_sel_{k['id']}")
                    if st.button("✅ Konfirmasi", key=f"guru_confirm_{k['id']}"):
                        for name in selected:
                            api_request("POST", f"/kelas/{k['id']}/guru", json={"user_id": names[name]})
                        st.rerun()

        # ── Atur Siswa ──
        with st.container(border=True):
            siswa_ids = {s["id"] for s in siswas}
            st.markdown(f"**👨‍🎓 Siswa ({len(siswas)})**")
            for s in siswas:
                cols = st.columns([3, 1])
                cols[0].write(f"{s['nama_lengkap']} ({s['username']})")
                if cols[1].button("🗑️", key=f"siswa_rm_{k['id']}_{s['id']}"):
                    api_request("DELETE", f"/kelas/{k['id']}/siswa/{s['id']}")
                    st.rerun()

            if st.button("➕ Tambah Siswa", key=f"siswa_tmbh_{k['id']}"):
                key = f"show_siswa_add_{k['id']}"
                st.session_state[key] = not st.session_state.get(key, False)

            if st.session_state.get(f"show_siswa_add_{k['id']}"):
                all_ok, all_siswa = api_request("GET", "/users/", params={"role": "SISWA"})
                if all_ok and all_siswa:
                    available = [s for s in all_siswa if s["id"] not in siswa_ids]
                    names = {f"{s['nama_lengkap']} ({s['username']})": s["id"] for s in available}
                    selected = st.multiselect("Pilih Siswa", list(names.keys()), key=f"siswa_sel_{k['id']}")
                    if st.button("✅ Konfirmasi", key=f"siswa_confirm_{k['id']}"):
                        for name in selected:
                            api_request("POST", f"/kelas/{k['id']}/siswa", json={"user_id": names[name]})
                        st.rerun()

        # ── Atur Jadwal ──
        with st.container(border=True):
            st.markdown("**🕐 Atur Jadwal**")
            success, jadwal_list = api_request("GET", f"/kelas/{k['id']}/jadwal")
            if success and jadwal_list:
                for j in jadwal_list:
                    cols = st.columns([2, 1, 1])
                    cols[0].write(f"{j['hari']} {j['waktu_mulai']} — {j['waktu_selesai']}")
                    edit_key = f"jadwal_edit_{j['id']}"
                    if cols[1].button("✏️", key=f"edit_{j['id']}"):
                        st.session_state[edit_key] = not st.session_state.get(edit_key, False)
                    if cols[2].button("🗑️", key=f"del_{j['id']}"):
                        api_request("DELETE", f"/kelas/{k['id']}/jadwal/{j['id']}")
                        st.rerun()
                    if st.session_state.get(edit_key):
                        with st.form(key=f"jadwal_edit_form_{j['id']}", border=True):
                            cur_hari = st.selectbox("Hari", ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"],
                                                    index=["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"].index(j['hari']),
                                                    key=f"ehari_{j['id']}")
                            cur_mulai = st.time_input("Waktu Mulai", key=f"emulai_{j['id']}")
                            cur_selesai = st.time_input("Waktu Selesai", key=f"eselesai_{j['id']}")
                            ec1, ec2 = st.columns(2)
                            if ec1.form_submit_button("💾 Simpan", type="primary", use_container_width=True):
                                api_request("PUT", f"/kelas/{k['id']}/jadwal/{j['id']}", json={
                                    "hari": cur_hari, "waktu_mulai": str(cur_mulai), "waktu_selesai": str(cur_selesai),
                                })
                                st.session_state[edit_key] = False
                                st.rerun()
                            if ec2.form_submit_button("Batal", use_container_width=True):
                                st.session_state[edit_key] = False
                                st.rerun()
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
