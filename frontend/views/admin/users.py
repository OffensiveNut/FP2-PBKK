import uuid

import streamlit as st

from utils.api_client import api_request, api_upload

st.subheader("👥 Users", divider=True)

# ─── Filter ──────────────────────────────────────────────────────
role_filter = st.segmented_control("Filter Role", ["All", "ADMIN", "GURU", "SISWA"], default="All")

# ─── Quick Create ────────────────────────────────────────────────
with st.expander("➕ Buat User Baru", expanded=False):
    with st.form("form_create_user", border=False):
        col = st.columns(2)
        username = col[0].text_input("Username")
        email = col[1].text_input("Email")
        nama_lengkap = st.text_input("Nama Lengkap")
        col2 = st.columns(2)
        role = col2[0].selectbox("Role", ["ADMIN", "GURU", "SISWA"])
        password = col2[1].text_input("Password (kosongkan untuk auto-generate)", type="password")
        if st.form_submit_button("➕ Create User", type="primary", use_container_width=True):
            payload = {
                "username": username,
                "email": email,
                "nama_lengkap": nama_lengkap,
                "role": role,
            }
            if password:
                payload["password"] = password
            ok, result = api_request("POST", "/users/", json=payload)
            if ok:
                msg = f"✅ User **{result['username']}** berhasil dibuat"
                if result.get("generated_password"):
                    msg += f" — Password: `{result['generated_password']}`"
                st.success(msg)
                st.rerun()
            else:
                st.error(result)

# ─── Bulk Upload ─────────────────────────────────────────────────
with st.expander("📤 Bulk Create via CSV", expanded=False):
    st.markdown("[📥 Download Template CSV](../example_users.csv)")
    uploaded = st.file_uploader("Upload CSV", type=["csv"])
    if uploaded:
        ok, result = api_upload("POST", "/users/bulk", uploaded)
        if ok:
            st.success(f"{len(result)} user berhasil dibuat")
            st.rerun()
        else:
            st.error(result)

# ─── User List ───────────────────────────────────────────────────
params = {}
if role_filter != "All":
    params["role"] = role_filter

success, users = api_request("GET", "/users/", params=params)
if not success:
    st.warning(users)
    st.stop()

st.write(f"**{len(users or [])} user**")
for u in (users or []):
    cols = st.columns([2, 2, 1, 1, 1])
    cols[0].write(f"**{u['nama_lengkap']}**  \n{u['username']}")
    cols[1].write(u["email"])
    cols[2].write(f"`{u['role']}`")
    if cols[3].button("✏️", key=f"edit_{u['id']}"):
        st.session_state.edit_user = u
    if cols[4].button("🗑️", key=f"del_{u['id']}"):
        ok, _ = api_request("DELETE", f"/users/{u['id']}")
        if ok:
            st.success("User dihapus")
            st.rerun()

# ─── Edit Modal ──────────────────────────────────────────────────
edit_target = st.session_state.get("edit_user")
if edit_target:
    with st.container(border=True):
        st.markdown(f"**Edit User: {edit_target['username']}**")
        with st.form("form_edit_user", border=False):
            uname = st.text_input("Username", value=edit_target.get("username", ""))
            eml = st.text_input("Email", value=edit_target.get("email", ""))
            nm = st.text_input("Nama Lengkap", value=edit_target.get("nama_lengkap", ""))
            rl = st.selectbox("Role", ["ADMIN", "GURU", "SISWA"], index=["ADMIN", "GURU", "SISWA"].index(edit_target["role"]))
            pw = st.text_input("Password Baru (kosongkan jika tidak diganti)", type="password")
            c1, c2 = st.columns(2)
            if c1.form_submit_button("💾 Simpan"):
                payload = {"username": uname, "email": eml, "nama_lengkap": nm, "role": rl}
                if pw:
                    payload["password"] = pw
                ok, _ = api_request("PUT", f"/users/{edit_target['id']}", json=payload)
                if ok:
                    st.success("User diupdate")
                    st.session_state.edit_user = None
                    st.rerun()
                else:
                    st.error(_)
            if c2.form_submit_button("Batal"):
                st.session_state.edit_user = None
                st.rerun()
