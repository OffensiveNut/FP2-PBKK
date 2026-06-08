from fastapi import APIRouter

from app.api.v1.endpoints import auth, izin, kehadiran, kelas, semester_config, users

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(kelas.router, prefix="/kelas", tags=["kelas"])
router.include_router(kehadiran.router, prefix="/kehadiran", tags=["kehadiran"])
router.include_router(izin.router, prefix="/izin", tags=["izin"])
router.include_router(
    semester_config.router, prefix="/semester", tags=["semester"]
)
