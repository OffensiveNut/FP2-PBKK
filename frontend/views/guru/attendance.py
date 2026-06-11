import uuid
from datetime import datetime, timezone

import streamlit as st

from utils.api_client import api_download_text, api_request

st.subheader("📋 Attendance", divider=True)

now = datetime.now(timezone.utc)
hari_map = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
today_hari = hari_map[now.weekday()]

success, kelas_list = api_request("GET", "/kelas/")
if not success or not kelas_list:
    st.info("Belum ada kelas")
    st.stop()

# ─── Active Class ────────────────────────────────────────────────
with st.container(border=True):
    st.markdown("**🔝 Kelas Sedang Berlangsung**")

    active_kelas = None
    active_jadwal = None
    for k in kelas_list:
        ok, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
        if ok and jadwal:
            for j in jadwal:
                if j["hari"] == today_hari:
                    active_kelas = k
                    active_jadwal = j
                    break
        if active_kelas:
            break

    if active_kelas and active_jadwal:
        st.success(f"**{active_kelas['nama_kelas']}**  \n{active_jadwal['hari']} {active_jadwal['waktu_mulai']} — {active_jadwal['waktu_selesai']}")

        ok, pertemuan_list = api_request("GET", f"/pertemuan/kelas/{active_kelas['id']}")
        today_str = now.strftime("%Y-%m-%d")
        active_pertemuan = None
        if ok and pertemuan_list:
            for p in pertemuan_list:
                if p["tanggal_pertemuan"] == today_str:
                    active_pertemuan = p
                    break

        if active_pertemuan:
            c1, c2 = st.columns([2, 1])
            c1.markdown(f"**Token Presensi:** `{active_pertemuan['token_presensi']}`")
            if c2.button("🔄 Rotate Token", key="rotate_active"):
                ok, p2 = api_request("POST", f"/pertemuan/{active_pertemuan['id']}/rotate-token")
                if ok:
                    st.success(f"Token baru: `{p2['token_presensi']}`")
                    st.rerun()

            ok, hadir_list = api_request("GET", f"/kehadiran/pertemuan/{active_pertemuan['id']}")
            if ok and hadir_list:
                st.write(f"**Presensi ({len(hadir_list)} siswa)**")
                for h in hadir_list:
                    cols = st.columns([2, 1, 1])
                    cols[0].write(str(h.get("siswa_id", "-"))[:8] + "...")
                    cols[1].write(f"`{h['status_hadir']}`")
                    cols[2].write(h.get("waktu_presensi", "")[:16] if h.get("waktu_presensi") else "-")
        else:
            st.info("Belum ada pertemuan hari ini")
    else:
        st.info("Tidak ada kelas yang sedang berlangsung saat ini")

# ─── All Classes ─────────────────────────────────────────────────
st.write("")
st.markdown("**📚 Semua Kelas**")

for k in kelas_list:
    with st.expander(f"**{k['nama_kelas']}**"):
        ok, pertemuan_list = api_request("GET", f"/pertemuan/kelas/{k['id']}")
        if not ok or not pertemuan_list:
            st.caption("Belum ada pertemuan")
            continue

        for p in pertemuan_list:
            cols = st.columns([2, 1, 1])
            cols[0].write(p["tanggal_pertemuan"])
            cols[1].write(f"`{p['token_presensi']}`")
            if cols[2].button("Detail", key=f"detail_{p['id']}"):
                st.session_state.detail_pertemuan = p["id"] if st.session_state.get("detail_pertemuan") != p["id"] else None
                st.rerun()

            if st.session_state.get("detail_pertemuan") == p["id"]:
                with st.container(border=True):
                    st.markdown(f"**Token:** `{p['token_presensi']}`")
                    c1, c2 = st.columns([1, 1])
                    if c1.button("🔄 Rotate", key=f"rot_{p['id']}"):
                        ok, res = api_request("POST", f"/pertemuan/{p['id']}/rotate-token")
                        if ok:
                            st.success(f"Token baru: `{res['token_presensi']}`")
                            st.rerun()
                    csv_data = api_download_text(f"/kehadiran/export/pertemuan/{p['id']}")
                    if csv_data:
                        st.download_button("📥 Download CSV", csv_data, file_name=f"rekap_{p['id']}.csv", mime="text/csv", key=f"csv_{p['id']}")

                    ok_h, hadir = api_request("GET", f"/kehadiran/pertemuan/{p['id']}")
                    if ok_h and hadir:
                        st.write("**Presensi:**")
                        for h in hadir:
                            st.write(f"`{h['status_hadir']}` — {h.get('waktu_presensi', '-')} | siswa_id: {str(h['siswa_id'])[:8]}")
                    else:
                        st.info("Belum ada presensi")

                    ok_i, izin_list = api_request("GET", "/izin/")
                    kelas_izin = [iz for iz in (izin_list or []) if iz.get("pertemuan", {}).get("kelas_id") == k["id"]]
                    if kelas_izin:
                        st.write("**Izin Masuk:**")
                        for iz in kelas_izin:
                            st.write(f"Siswa: {str(iz['siswa_id'])[:8]} — `{iz['status_approval']}`")
                            if iz["status_approval"] == "PENDING":
                                c1, c2 = st.columns([1, 1])
                                if c1.button("✅ Approve", key=f"app_{iz['id']}"):
                                    api_request("PUT", f"/izin/{iz['id']}/approve")
                                    st.rerun()
                                if c2.button("❌ Reject", key=f"rej_{iz['id']}"):
                                    api_request("PUT", f"/izin/{iz['id']}/reject")
                                    st.rerun()
