# FastPresensi

Sistem presensi sekolah berbasis web dengan FastAPI (backend) dan Streamlit (frontend).

## Tech Stack

| Layer | Teknologi |
|---|---|
| Backend | FastAPI, SQLAlchemy (async), PostgreSQL |
| Frontend | Streamlit |
| ORM | SQLAlchemy 2.0 + asyncpg |
| Migrasi | Alembic |
| Auth | JWT (PyJWT) + bcrypt (passlib) |
| Package Manager | uv (workspace monorepo) |

## Prerequisites

- Python >= 3.11
- PostgreSQL (running on `localhost:5432`)
- [uv](https://docs.astral.sh/uv/) (package manager)

## Setup

### 1. Clone & masuk direktori

```bash
git clone <repo-url> && cd FP2-PBKK
```

### 2. Konfigurasi environment

Salin `.env.example` ke `.env` dan sesuaikan:

```bash
cp .env.example .env
```

### 3. Buat database PostgreSQL

```bash
psql -U postgres -c "CREATE DATABASE fastpresensi;"
```

### 4. Install dependencies

```bash
uv sync
```

### 5. Jalankan migrasi database

```bash
cd backend && uv run alembic upgrade head
```

## Menjalankan Aplikasi

### Backend (FastAPI)

```bash
cd backend
uv run uvicorn app.main:app --reload
```

Server berjalan di `http://localhost:8000`.  
Dokumentasi API (Swagger): `http://localhost:8000/docs`

### Frontend (Streamlit)

```bash
cd frontend
uv run streamlit run main.py
```

Frontend berjalan di `http://localhost:8501`.

## Default Admin

Saat pertama kali backend dijalankan, user admin akan otomatis dibuat:

| Username | Password |
|---|---|
| `admin` | `admin123` |

Gunakan kredensial ini untuk login dan membuat user lain (guru/siswa).

## API Endpoints

### Auth & Users

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/v1/auth/login` | Public | Login, mengembalikan JWT |
| GET | `/api/v1/users/me` | Any | Profil user saat ini |
| GET | `/api/v1/users/` | Admin | Daftar semua user (`?role=GURU`/`SISWA`) |
| POST | `/api/v1/users/` | Admin | Buat user baru (password opsional → auto-generate) |
| GET | `/api/v1/users/{id}` | Admin | Detail user |
| PUT | `/api/v1/users/{id}` | Admin | Update user |
| DELETE | `/api/v1/users/{id}` | Admin | Hapus user |
| POST | `/api/v1/users/bulk` | Admin | Import user dari CSV |

### Semester Config

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| GET | `/api/v1/semester/` | Any | Daftar semester |
| POST | `/api/v1/semester/` | Admin | Buat semester baru |
| GET | `/api/v1/semester/{id}` | Any | Detail semester |
| PUT | `/api/v1/semester/{id}` | Admin | Update semester |
| DELETE | `/api/v1/semester/{id}` | Admin | Hapus semester |

### Kelas

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| GET | `/api/v1/kelas/` | Any | Daftar kelas |
| POST | `/api/v1/kelas/` | Admin | Buat kelas baru |
| GET | `/api/v1/kelas/{id}` | Any | Detail kelas (gurus + siswas) |
| PUT | `/api/v1/kelas/{id}` | Admin | Update kelas |
| DELETE | `/api/v1/kelas/{id}` | Admin | Hapus kelas |
| POST | `/api/v1/kelas/{id}/guru` | Admin | Tambah guru ke kelas |
| DELETE | `/api/v1/kelas/{id}/guru/{guru_id}` | Admin | Hapus guru dari kelas |
| POST | `/api/v1/kelas/{id}/siswa` | Admin | Tambah siswa ke kelas |
| DELETE | `/api/v1/kelas/{id}/siswa/{siswa_id}` | Admin | Hapus siswa dari kelas |
| GET | `/api/v1/kelas/{id}/jadwal` | Any | Jadwal kelas |
| POST | `/api/v1/kelas/{id}/jadwal` | Admin | Tambah jadwal kelas |
| PUT | `/api/v1/kelas/{id}/jadwal/{jadwal_id}` | Admin | Update jadwal |
| DELETE | `/api/v1/kelas/{id}/jadwal/{jadwal_id}` | Admin | Hapus jadwal |

### Pertemuan

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/v1/pertemuan/generate/{kelas_id}` | Guru/Admin | Generate pertemuan dari jadwal × semester |
| POST | `/api/v1/pertemuan/{kelas_id}/generate-token` | Guru/Admin | Buat pertemuan hari ini + token (`jenis_pertemuan`, `waktu_selesai`) |
| GET | `/api/v1/pertemuan/kelas/{kelas_id}` | Any | Daftar pertemuan per kelas |
| GET | `/api/v1/pertemuan/{id}` | Any | Detail pertemuan |
| PUT | `/api/v1/pertemuan/{id}` | Guru/Admin | Update pertemuan |
| DELETE | `/api/v1/pertemuan/{id}` | Guru/Admin | Hapus pertemuan |
| POST | `/api/v1/pertemuan/{id}/rotate-token` | Guru/Admin | Rotasi token presensi |

### Kehadiran

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/v1/kehadiran/token` | Siswa | Presensi via token |
| POST | `/api/v1/kehadiran/manual` | Guru/Admin | Presensi manual (upsert) |
| GET | `/api/v1/kehadiran/pertemuan/{pertemuan_id}` | Guru/Admin | Daftar presensi per pertemuan |
| GET | `/api/v1/kehadiran/siswa/{siswa_id}` | Siswa (sendiri) / Guru/Admin | Riwayat presensi siswa |
| GET | `/api/v1/kehadiran/export/pertemuan/{pertemuan_id}` | Guru/Admin | Download CSV rekap per pertemuan |
| GET | `/api/v1/kehadiran/export/kelas/{kelas_id}` | Guru/Admin | Download CSV rekap per kelas |

### Izin

| Method | Endpoint | Auth | Deskripsi |
|---|---|---|---|
| POST | `/api/v1/izin/` | Siswa | Ajukan izin |
| POST | `/api/v1/izin/upload` | Siswa | Upload bukti izin |
| GET | `/api/v1/izin/` | Guru/Admin | Daftar izin |
| GET | `/api/v1/izin/{id}` | Any | Detail izin |
| PUT | `/api/v1/izin/{id}/approve` | Guru/Admin | Setujui izin |
| PUT | `/api/v1/izin/{id}/reject` | Guru/Admin | Tolak izin |

## Database Schema

9 tables:

| Table | Keterangan |
|---|---|
| `users` | User (ADMIN, GURU, SISWA) |
| `semester_config` | Konfigurasi semester akademik |
| `kelas` | Data kelas, terikat ke semester |
| `kelas_guru` | Relasi banyak-ke-banyak kelas ↔ guru |
| `kelas_siswa` | Relasi banyak-ke-banyak kelas ↔ siswa |
| `jadwal_kelas` | Jadwal mingguan (hari, waktu mulai, waktu selesai) |
| `pertemuan` | Pertemuan spesifik hasil generate dari jadwal |
| `kehadiran` | Presensi siswa per pertemuan |
| `izin` | Pengajuan izin siswa |

## Struktur Proyek

```
FP2-PBKK/
├── backend/
│   ├── alembic/                  # Migrasi database
│   │   └── versions/             # File migrasi
│   ├── app/
│   │   ├── api/v1/endpoints/     # Route handlers
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   ├── semester_config.py
│   │   │   ├── kelas.py
│   │   │   ├── pertemuan.py
│   │   │   ├── kehadiran.py
│   │   │   └── izin.py
│   │   ├── core/                 # Konfigurasi, security, DB
│   │   ├── models/               # SQLAlchemy models (7 entity + 2 junction)
│   │   ├── schemas/              # Pydantic schemas
│   │   ├── services/             # Business logic
│   │   ├── utils/                # Utilities (csv_exporter, email_service, file_service)
│   │   └── main.py               # Entry point FastAPI
│   └── pyproject.toml
├── frontend/
│   ├── utils/                    # API client, state
│   ├── views/                    # Halaman (login, settings, admin/, guru/, siswa/)
│   ├── main.py                   # Entry point Streamlit (RBAC navigation)
│   └── pyproject.toml
└── pyproject.toml                # Workspace root
```
