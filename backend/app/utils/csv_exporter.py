import csv
import io

from app.models.kehadiran import Kehadiran
from app.models.kelas import Kelas
from app.models.pertemuan import Pertemuan
from app.models.user import User


def export_kehadiran_to_csv(
    kehadiran_list: list[Kehadiran],
    kelas: Kelas | None = None,
) -> str:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Nama Siswa",
        "Username",
        "NIS",
        "Kelas",
        "Tanggal Pertemuan",
        "Deskripsi Pertemuan",
        "Status Hadir",
        "Metode Presensi",
        "Waktu Presensi",
    ])

    for k in kehadiran_list:
        siswa: User | None = k.siswa
        pertemuan: Pertemuan | None = k.pertemuan
        nama_kelas = kelas.nama_kelas if kelas else (pertemuan.kelas.nama_kelas if pertemuan else "-")

        writer.writerow([
            siswa.nama_lengkap if siswa else "-",
            siswa.username if siswa else "-",
            siswa.id if siswa else "-",
            nama_kelas,
            pertemuan.tanggal_pertemuan if pertemuan else "-",
            pertemuan.deskripsi if pertemuan else "-",
            k.status_hadir.value,
            k.metode_presensi.value,
            k.waktu_presensi.isoformat() if k.waktu_presensi else "-",
        ])

    return output.getvalue()
