from datetime import datetime, timezone

import streamlit as st
import pandas as pd

from utils.api_client import api_download_text, api_request

now = datetime.now(timezone.utc)
hari_map = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
today_hari = hari_map[now.weekday()]
today_str = now.strftime("%Y-%m-%d")

st.subheader("📋 Attendance", divider=True)

success, kelas_list = api_request("GET", "/kelas/")
if not success or not kelas_list:
    st.info("Belum ada kelas")
    st.stop()


def get_siswa_dict(kelas_id: str) -> dict[str, dict]:
    ok, detail = api_request("GET", f"/kelas/{kelas_id}")
    if ok:
        return {s["id"]: s for s in detail.get("siswas", [])}
    return {}


def render_detail_kelas(k: dict):
    col_back, col_export = st.columns([8, 2])
    with col_back:
        if st.button("⬅️ Kembali ke Dashboard", use_container_width=True):
            st.session_state.selected_class = None
            st.rerun()

    ok_j, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
    jadwal_str = ", ".join(f"{j['hari']} {j['waktu_mulai']}—{j['waktu_selesai']}" for j in (jadwal or []))

    st.write("")
    st.markdown(f"### {k['nama_kelas']}")
    if jadwal_str:
        st.caption(f"🕐 {jadwal_str}")

    ok_p, pertemuan_list = api_request("GET", f"/pertemuan/kelas/{k['id']}")

    if not ok_p or not pertemuan_list:
        st.info("Belum ada pertemuan. Generate pertemuan terlebih dahulu.")
        if st.button("🤖 Generate Pertemuan", type="primary"):
            ok, _ = api_request("POST", f"/pertemuan/generate/{k['id']}")
            if ok:
                st.success("Pertemuan berhasil dibuat")
                st.rerun()
        st.stop()

    sel_key = f"selected_pertemuan_{k['id']}"
    pertemuan_labels = {f"{p['tanggal_pertemuan']} — {p.get('jenis_pertemuan', '')}": p for p in pertemuan_list}
    selected_label = st.selectbox("Pilih Pertemuan", list(pertemuan_labels.keys()),
                                  index=len(pertemuan_list) - 1, key=sel_key)
    p = pertemuan_labels[selected_label]
    ok_h, hadir_list = api_request("GET", f"/kehadiran/pertemuan/{p['id']}")

    siswa_map = get_siswa_dict(k["id"])

    total = len(siswa_map)
    hadir = len([h for h in (hadir_list or []) if h["status_hadir"] == "HADIR"])
    izin_c = len([h for h in (hadir_list or []) if h["status_hadir"] == "IZIN"])
    sakit = len([h for h in (hadir_list or []) if h["status_hadir"] == "SAKIT"])
    alpa = len([h for h in (hadir_list or []) if h["status_hadir"] == "ALPA"])

    st.divider()
    c_hadir, c_izin, c_sakit, c_alpa, c_total = st.columns(5)
    with c_hadir: st.metric("HADIR", hadir)
    with c_izin: st.metric("IZIN", izin_c)
    with c_sakit: st.metric("SAKIT", sakit)
    with c_alpa: st.metric("ALPA", alpa)
    with c_total: st.metric("TOTAL SISWA", total)

    st.divider()
    st.markdown(f"**Token Presensi:** `{p['token_presensi']}` | **Tanggal:** {p['tanggal_pertemuan']}")
    c1, c2 = st.columns([1, 1])
    if c1.button("🔄 Rotate Token", use_container_width=True):
        ok2, p2 = api_request("POST", f"/pertemuan/{p['id']}/rotate-token")
        if ok2:
            st.success(f"Token baru: `{p2['token_presensi']}`")
            st.rerun()
    csv_data = api_download_text(f"/kehadiran/export/pertemuan/{p['id']}")
    if csv_data:
        st.download_button("📥 Download CSV", csv_data, file_name=f"rekap_{p['id']}.csv", mime="text/csv")

    st.divider()
    st.subheader("Daftar Mahasiswa & Mark Manual")
    st.caption("Pilih status kehadiran secara manual jika presensi token gagal atau ada perubahan.")

    hadir_by_siswa = {h["siswa_id"]: h for h in (hadir_list or [])}

    h1, h2, h3, h4 = st.columns([2, 3, 1, 3])
    h1.write("**Nama**")
    h2.write("**Username**")
    h3.write("**Status**")
    h4.write("**Mark Manual**")

    for sid, s in siswa_map.items():
        cols = st.columns([2, 3, 1, 3])
        cols[0].write(s.get("nama_lengkap", "-"))
        cols[1].write(s.get("username", "-"))
        existing = hadir_by_siswa.get(sid)
        cols[2].write(f"**{existing['status_hadir']}**" if existing else "**—**")
        with cols[3]:
            b1, b2, b3, b4 = st.columns(4)
            if b1.button("H", key=f"H_{sid}_{p['id']}", help="Hadir", use_container_width=True):
                api_request("POST", "/kehadiran/manual", json={"pertemuan_id": str(p["id"]), "siswa_id": sid, "status_hadir": "HADIR"})
                st.rerun()
            if b2.button("I", key=f"I_{sid}_{p['id']}", help="Izin", use_container_width=True):
                api_request("POST", "/kehadiran/manual", json={"pertemuan_id": str(p["id"]), "siswa_id": sid, "status_hadir": "IZIN"})
                st.rerun()
            if b3.button("S", key=f"S_{sid}_{p['id']}", help="Sakit", use_container_width=True):
                api_request("POST", "/kehadiran/manual", json={"pertemuan_id": str(p["id"]), "siswa_id": sid, "status_hadir": "SAKIT"})
                st.rerun()
            if b4.button("A", key=f"A_{sid}_{p['id']}", help="Alpa", use_container_width=True):
                api_request("POST", "/kehadiran/manual", json={"pertemuan_id": str(p["id"]), "siswa_id": sid, "status_hadir": "ALPA"})
                st.rerun()

    st.divider()
    st.subheader("Izin Masuk")
    ok_i, izin_list = api_request("GET", "/izin/")
    pertemuan_ids = {p["id"] for p in (pertemuan_list or [])}
    kelas_izin = [iz for iz in (izin_list or []) if iz["pertemuan_id"] in pertemuan_ids]
    if kelas_izin:
        for iz in kelas_izin:
            s_info = siswa_map.get(iz["siswa_id"], {})
            s_name = s_info.get("nama_lengkap", str(iz["siswa_id"])[:8])
            st.write(f"**{s_name}** — `{iz['status_approval']}` — {iz.get('alasan', '')}")
            if iz["status_approval"] == "PENDING":
                c1, c2 = st.columns([1, 1])
                if c1.button("✅ Approve", key=f"app_{iz['id']}", use_container_width=True):
                    api_request("PUT", f"/izin/{iz['id']}/approve")
                    st.rerun()
                if c2.button("❌ Reject", key=f"rej_{iz['id']}", use_container_width=True):
                    api_request("PUT", f"/izin/{iz['id']}/reject")
                    st.rerun()
    else:
        st.info("Belum ada izin masuk")


# ─── Full-Screen Detail ──────────────────────────────────────────
if st.session_state.get("selected_class") is not None:
    render_detail_kelas(st.session_state.selected_class)
    st.stop()

# ─── Live Attendance ─────────────────────────────────────────────
st.write("")
with st.container(border=True):
    st.caption("🔴 Live Attendance (Sesi Berlangsung)")

    active_kelas = None
    active_jadwal = None
    for k in kelas_list:
        ok_j, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
        if ok_j and jadwal:
            for j in jadwal:
                if j["hari"] == today_hari:
                    active_kelas = k
                    active_jadwal = j
                    break
        if active_kelas:
            break

    if active_kelas and active_jadwal:
        st.subheader(f"**{active_kelas['nama_kelas']}**")
        st.caption(f"{active_jadwal['hari']} {active_jadwal['waktu_mulai']} — {active_jadwal['waktu_selesai']}")

        ok_p, pertemuan_list = api_request("GET", f"/pertemuan/kelas/{active_kelas['id']}")
        active_pertemuan = None
        if ok_p and pertemuan_list:
            for p in pertemuan_list:
                if p["tanggal_pertemuan"] == today_str:
                    active_pertemuan = p
                    break

        col_token, col_live = st.columns([1.5, 2.5])

        with col_token:
            with st.container(border=True):
                st.markdown("#### ⊕ Mulai Pertemuan")
                jenis = st.selectbox("Tipe Pertemuan", ["OFFLINE", "ONLINE"], key=f"jenis_{active_kelas['id']}")
                waktu_selesai = st.text_input("Waktu Selesai", placeholder="10:30", key=f"ws_{active_kelas['id']}")
                if st.button("Mulai Pertemuan", type="primary", use_container_width=True):
                    params = {"jenis_pertemuan": jenis}
                    if waktu_selesai:
                        params["waktu_selesai"] = f"{waktu_selesai}:00"
                    ok, result = api_request("POST", f"/pertemuan/{active_kelas['id']}/generate-token", params=params)
                    if ok:
                        st.session_state[f"token_{active_kelas['id']}"] = result["token_presensi"]
                        st.rerun()
                    else:
                        st.error(result)

            st.write("")
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.8rem; font-weight: bold; color: gray; margin-bottom: 10px;'>ACTIVE ATTENDANCE TOKEN</div>", unsafe_allow_html=True)
                session_token = st.session_state.get(f"token_{active_kelas['id']}")
                if active_pertemuan:
                    token = active_pertemuan["token_presensi"]
                    st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>{token}</h1>", unsafe_allow_html=True)
                    if st.button("🔄 Rotate", use_container_width=True):
                        ok2, p2 = api_request("POST", f"/pertemuan/{active_pertemuan['id']}/rotate-token")
                        if ok2:
                            st.session_state[f"token_{active_kelas['id']}"] = p2["token_presensi"]
                            st.rerun()
                elif session_token:
                    st.markdown(f"<h1 style='text-align: center; color: #ff4b4b; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>{session_token}</h1>", unsafe_allow_html=True)
                else:
                    st.markdown("<h1 style='text-align: center; color: gray; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>--- ---</h1>", unsafe_allow_html=True)

        with col_live:
            st.caption("📋 Live Attendance Report")
            hadir_list = []
            if active_pertemuan:
                ok_h, hadir_list = api_request("GET", f"/kehadiran/pertemuan/{active_pertemuan['id']}")
            if hadir_list:
                siswa_map = get_siswa_dict(active_kelas["id"])
                rows = []
                for h in hadir_list:
                    s = siswa_map.get(h["siswa_id"], {})
                    rows.append({
                        "Nama": s.get("nama_lengkap", str(h["siswa_id"])[:8]),
                        "Waktu": h.get("waktu_presensi", "")[11:19] if h.get("waktu_presensi") else "-",
                        "Status": h["status_hadir"],
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada presensi")
    else:
        col_token, col_live = st.columns([1.5, 2.5])
        with col_token:
            with st.container(border=True):
                st.markdown("#### ⊕ New Session (Pertemuan)")
                st.info("Tidak ada jadwal untuk hari ini")
            st.write("")
            with st.container(border=True):
                st.markdown("<div style='text-align: center; font-size: 0.8rem; font-weight: bold; color: gray; margin-bottom: 10px;'>ACTIVE ATTENDANCE TOKEN</div>", unsafe_allow_html=True)
                st.markdown("<h1 style='text-align: center; color: gray; font-size: 3.5rem; margin-top: -20px; margin-bottom: -10px;'>--- ---</h1>", unsafe_allow_html=True)
        with col_live:
            st.caption("📋 Live Attendance Report")
            st.info("Tidak ada kelas yang berlangsung hari ini")

# ─── Class List ──────────────────────────────────────────────────
st.write("")
st.caption("📚 Daftar Kuliah Anda")
st.divider()

for k in kelas_list:
    ok_j, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
    jadwal_str = ", ".join(f"{j['hari']} {j['waktu_mulai']}—{j['waktu_selesai']}" for j in (jadwal or []))

    with st.container(border=True):
        col_info, col_btn = st.columns([8, 2])
        with col_info:
            st.markdown(f"**{k['nama_kelas']}**")
            if jadwal_str:
                st.caption(f"📅 {jadwal_str}")
            else:
                st.caption("Belum ada jadwal")
        with col_btn:
            if st.button("Lihat Detail Kelas", key=f"btn_detail_{k['id']}", use_container_width=True):
                st.session_state.selected_class = k
                st.rerun()
