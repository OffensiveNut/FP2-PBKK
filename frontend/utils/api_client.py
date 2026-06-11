from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
import streamlit as st
from dotenv import load_dotenv

_dotenv_path = Path(__file__).resolve().parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=_dotenv_path)

BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000/api/v1")


def api_request(
    method: str,
    path: str,
    *,
    json: dict | None = None,
    params: dict | None = None,
) -> tuple[bool, Any]:
    url = f"{BASE_URL}{path}"
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.request(
            method, url, headers=headers, json=json, params=params, timeout=10
        )

        if resp.status_code == 204:
            return True, None
        if resp.status_code in (200, 201):
            return True, resp.json()
        if resp.status_code == 401:
            st.session_state.clear()
            st.rerun()
            return False, "Sesi habis"

        detail = ""
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        return False, detail

    except requests.exceptions.ConnectionError:
        return False, "Gagal terhubung ke server. Pastikan backend berjalan."
    except requests.exceptions.Timeout:
        return False, "Server tidak merespon. Coba lagi."
    except Exception as e:
        return False, str(e)


def api_login(username: str, password: str) -> tuple[bool, Any]:
    url = f"{BASE_URL}/auth/login"
    try:
        resp = requests.post(url, json={"username": username, "password": password}, timeout=10)
        if resp.status_code == 200:
            return True, resp.json()
        if resp.status_code == 401:
            return False, "Username atau password salah"
        return False, resp.json().get("detail", f"Error {resp.status_code}")
    except requests.exceptions.ConnectionError:
        return False, "Gagal terhubung ke server backend"
    except Exception as e:
        return False, str(e)


def api_upload(method: str, path: str, file: Any, data: dict | None = None) -> tuple[bool, Any]:
    url = f"{BASE_URL}{path}"
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.request(
            method, url, headers=headers, files={"file": file}, data=data, timeout=30
        )
        if resp.status_code in (200, 201):
            return True, resp.json()
        return False, resp.json().get("detail", f"Error {resp.status_code}")
    except Exception as e:
        return False, str(e)
