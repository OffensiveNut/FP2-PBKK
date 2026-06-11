import uuid
from datetime import datetime, timezone

import streamlit as st

from utils.api_client import api_request, api_upload
from utils.state import get_user, is_guru_or_admin

st.subheader("📋 Attendance", divider=True)

now = datetime.now(timezone.utc)
hari_map = ["SENIN", "SELASA", "RABU", "KAMIS", "JUMAT", "SABTU", "MINGGU"]
today_hari = hari_map[now.weekday()]

user = get_user()
siswa_id = user["id"]

# ─── Active Class ────────────────────────────────────────────────
success, kelas_list = api_request("GET", "/kelas/")
if not success or not kelas_list:
    st.info("Belum ada kelas")
    st.stop()

with st.container(border=True):
    st.markdown("**🔝 Kelas Sedang Berlangsung**")

    active_kelas = None
    for k in kelas_list:
        ok, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
        if ok and jadwal:
            for j in jadwal:
                if j["hari"] == today_hari:
                    active_kelas = k
                    break
        if active_kelas:
            break

    if active_kelas:
        st.success(f"**{active_kelas['nama_kelas']}**")

        today_str = now.strftime("%Y-%m-%d")
        ok, pertemuan_list = api_request("GET", f"/pertemuan/kelas/{active_kelas['id']}")
        active_pertemuan = None
        if ok and pertemuan_list:
            for p in pertemuan_list:
                if p["tanggal_pertemuan"] == today_str:
                    active_pertemuan = p
                    break

        if active_pertemuan:
            assert isinstance(active_pertemuan, dict)
            with st.form("form_token", border=False):
                token = st.text_input("Masukkan Token Presensi", placeholder="6 digit", max_chars=6)
                if st.form_submit_button("✅ Hadir", type="primary", use_container_width=True):
                    if token:
                        ok, msg = api_request("POST", "/kehadiran/token", json={
                            "pertemuan_id": active_pertemuan["id"],
                            "token": token,
                        })
                        if ok:
                            st.success("Presensi berhasil!")
                            st.rerun()
                        else:
                            st.error(msg)
                    else:
                        st.error("Token tidak boleh kosong")
        else:
            st.info("Belum ada pertemuan hari ini")

        # Form izin on active class
        if active_pertemuan:
            assert isinstance(active_pertemuan, dict)
            with st.expander("📄 Ajukan Izin"):
                with st.form("form_izin", border=False):
                    alasan = st.text_area("Alasan Izin")
                    file = st.file_uploader("Upload Bukti", type=["pdf", "jpg", "png"])
                    if st.form_submit_button("Kirim Izin", use_container_width=True):
                        if not alasan:
                            st.error("Alasan harus diisi")
                        else:
                            payload = {
                                "pertemuan_id": str(active_pertemuan["id"]),
                                "alasan": alasan,
                                "file_bukti": "",
                            }
                            if file:
                                ok, up = api_upload("POST", "/izin/upload", file)
                                if ok:
                                    payload["file_bukti"] = up.get("file_path", "")
                            ok, _ = api_request("POST", "/izin/", json=payload)
                            if ok:
                                st.success("Izin diajukan")
                                st.rerun()
                            else:
                                st.error(_)
    else:
        st.info("Tidak ada kelas yang sedang berlangsung")

# ─── All Classes ─────────────────────────────────────────────────
st.write("")
st.markdown("**📚 Kelas Saya**")

for k in kelas_list:
    with st.expander(f"**{k['nama_kelas']}**"):
        # Jadwal
        ok, jadwal = api_request("GET", f"/kelas/{k['id']}/jadwal")
        if ok and jadwal:
            st.caption("Jadwal:")
            for j in jadwal:
                st.write(f"{j['hari']} {j['waktu_mulai']} — {j['waktu_selesai']}")

        # My attendance history
        ok, kehadiran = api_request("GET", f"/kehadiran/siswa/{siswa_id}")
        if ok and kehadiran:
            st.write("**Riwayat Presensi:**")
            for h in kehadiran:
                if h.get("pertemuan", {}).get("kelas_id") == k["id"]:
                    st.write(f"{h.get('waktu_presensi', '')[:10]} — `{h['status_hadir']}` — {h['metode_presensi']}")
