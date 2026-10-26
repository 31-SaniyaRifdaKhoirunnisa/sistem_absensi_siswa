import csv
import os
from datetime import date, datetime

# Folder penyimpanan data
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
LAPORAN_DIR = os.path.join(BASE_DIR, "laporan")

FILE_SISWA = os.path.join(DATA_DIR, "siswa.csv")
FILE_ABSENSI = os.path.join(DATA_DIR, "absensi.csv")

STATUS = ["Hadir", "Izin", "Sakit", "Alpa"]


def siapkan_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(LAPORAN_DIR, exist_ok=True)

    if not os.path.exists(FILE_SISWA):
        with open(FILE_SISWA, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["nis", "nama"])

    if not os.path.exists(FILE_ABSENSI):
        with open(FILE_ABSENSI, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tanggal", "nis", "nama", "status"])


def baca_csv(nama_file):
    with open(nama_file, "r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def simpan_csv(nama_file, kolom, data):
    with open(nama_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=kolom)
        writer.writeheader()
        writer.writerows(data)


def input_tidak_kosong(pesan):
    while True:
        nilai = input(pesan).strip()
        if nilai:
            return nilai
        print("Input tidak boleh kosong!")


def input_tanggal():
    while True:
        nilai = input(
            "Tanggal absensi (YYYY-MM-DD), kosong = hari ini: "
        ).strip()

        if not nilai:
            return date.today().isoformat()

        try:
            return datetime.strptime(
                nilai, "%Y-%m-%d"
            ).date().isoformat()
        except ValueError:
            print("Format salah! Contoh: 2026-10-19")


def tambah_siswa():
    siswa = baca_csv(FILE_SISWA)

    print("\n=== TAMBAH SISWA ===")
    nis = input_tidak_kosong("Masukkan NIS: ")

    if any(s["nis"] == nis for s in siswa):
        print("NIS sudah terdaftar!")
        return

    nama = input_tidak_kosong("Masukkan nama siswa: ")
    siswa.append({"nis": nis, "nama": nama})

    simpan_csv(FILE_SISWA, ["nis", "nama"], siswa)
    print("Data siswa berhasil disimpan!")


def tampilkan_siswa():
    siswa = baca_csv(FILE_SISWA)

    print("\n=== DAFTAR SISWA ===")
    if not siswa:
        print("Belum ada siswa.")
        return

    print("-" * 50)
    print(f"{'NIS':<15} {'NAMA':<30}")
    print("-" * 50)

    for s in siswa:
        print(f"{s['nis']:<15} {s['nama']:<30}")

    print("-" * 50)
    print(f"Jumlah siswa: {len(siswa)}")


def catat_absensi():
    siswa = baca_csv(FILE_SISWA)

    print("\n=== CATAT ABSENSI ===")
    if not siswa:
        print("Tambahkan data siswa terlebih dahulu.")
        return

    tanggal = input_tanggal()
    absensi = baca_csv(FILE_ABSENSI)

    data_hari_ini = {
        a["nis"]: a for a in absensi
        if a["tanggal"] == tanggal
    }

    for s in siswa:
        print(f"\nNIS  : {s['nis']}")
        print(f"Nama : {s['nama']}")

        if s["nis"] in data_hari_ini:
            lama = data_hari_ini[s["nis"]]["status"]
            print(f"Status sebelumnya: {lama}")
            pilihan = input("Ubah status? (y/n): ").strip().lower()
            if pilihan != "y":
                continue

        print("1. Hadir")
        print("2. Izin")
        print("3. Sakit")
        print("4. Alpa")

        pilihan = input("Pilih status (1-4): ").strip()

        if pilihan not in ["1", "2", "3", "4"]:
            print("Pilihan tidak valid. Siswa dilewati.")
            continue

        status = STATUS[int(pilihan) - 1]

        data_hari_ini[s["nis"]] = {
            "tanggal": tanggal,
            "nis": s["nis"],
            "nama": s["nama"],
            "status": status
        }

        print(f"Absensi {s['nama']} dicatat: {status}")

    data_lain = [
        a for a in absensi if a["tanggal"] != tanggal
    ]
    data_lain.extend(data_hari_ini.values())

    simpan_csv(
        FILE_ABSENSI,
        ["tanggal", "nis", "nama", "status"],
        data_lain
    )

    print("\nAbsensi selesai diproses!")


def rekap_absensi():
    siswa = baca_csv(FILE_SISWA)
    absensi = baca_csv(FILE_ABSENSI)

    print("\n=== REKAP ABSENSI SISWA ===")

    if not siswa:
        print("Belum ada data siswa.")
        return

    mulai = input(
        "Tanggal awal (YYYY-MM-DD), kosong = semua: "
    ).strip()
    akhir = ""

    if mulai:
        try:
            mulai = datetime.strptime(
                mulai, "%Y-%m-%d"
            ).date().isoformat()
        except ValueError:
            print("Format tanggal awal salah.")
            return

        akhir = input("Tanggal akhir (YYYY-MM-DD): ").strip()

        try:
            akhir = datetime.strptime(
                akhir, "%Y-%m-%d"
            ).date().isoformat()
        except ValueError:
            print("Format tanggal akhir salah.")
            return

        if akhir < mulai:
            print("Tanggal akhir tidak boleh sebelum tanggal awal.")
            return

    hasil = []

    for s in siswa:
        hitung = {status: 0 for status in STATUS}

        for a in absensi:
            if a["nis"] != s["nis"]:
                continue

            if mulai and not (mulai <= a["tanggal"] <= akhir):
                continue

            if a["status"] in hitung:
                hitung[a["status"]] += 1

        hasil.append({
            "nis": s["nis"],
            "nama": s["nama"],
            "hadir": hitung["Hadir"],
            "izin": hitung["Izin"],
            "sakit": hitung["Sakit"],
            "alpa": hitung["Alpa"],
            "total": sum(hitung.values())
        })

    print("-" * 86)
    print(
        f"{'NIS':<12} {'NAMA':<22} {'HADIR':>6} "
        f"{'IZIN':>6} {'SAKIT':>6} {'ALPA':>6} {'TOTAL':>7}"
    )
    print("-" * 86)

    for r in hasil:
        print(
            f"{r['nis']:<12} {r['nama']:<22} "
            f"{r['hadir']:>6} {r['izin']:>6} "
            f"{r['sakit']:>6} {r['alpa']:>6} "
            f"{r['total']:>7}"
        )

    print("-" * 86)

    nama_laporan = (
        f"rekap_{mulai}_sampai_{akhir}.csv"
        if mulai else "rekap_semua.csv"
    )
    lokasi = os.path.join(LAPORAN_DIR, nama_laporan)

    simpan_csv(
        lokasi,
        ["nis", "nama", "hadir", "izin", "sakit", "alpa", "total"],
        hasil
    )
    print(f"Laporan tersimpan di: {lokasi}")


def laporan_absensi_harian():
    absensi = baca_csv(FILE_ABSENSI)

    print("\n=== LAPORAN ABSENSI HARIAN ===")
    tanggal = input_tanggal()

    hasil = [
        a for a in absensi if a["tanggal"] == tanggal
    ]

    if not hasil:
        print("Belum ada absensi untuk tanggal tersebut.")
        return

    lokasi = os.path.join(
        LAPORAN_DIR, f"absensi_{tanggal}.csv"
    )

    simpan_csv(
        lokasi,
        ["tanggal", "nis", "nama", "status"],
        hasil
    )

    print(f"\nTanggal laporan: {tanggal}")
    print(f"Jumlah data absensi: {len(hasil)}")

    for status in STATUS:
        jumlah = sum(1 for a in hasil if a["status"] == status)
        print(f"{status}: {jumlah}")

    print(f"Laporan tersimpan di: {lokasi}")


def menu():
    siapkan_file()

    while True:
        print("\n" + "=" * 42)
        print("       SISTEM ABSENSI SISWA")
        print("=" * 42)
        print("1. Tambah siswa")
        print("2. Lihat daftar siswa")
        print("3. Catat absensi")
        print("4. Lihat rekap dan simpan laporan")
        print("5. Buat laporan absensi harian")
        print("0. Keluar")
        print("=" * 42)

        pilihan = input("Pilih menu (0-5): ").strip()

        if pilihan == "1":
            tambah_siswa()
        elif pilihan == "2":
            tampilkan_siswa()
        elif pilihan == "3":
            catat_absensi()
        elif pilihan == "4":
            rekap_absensi()
        elif pilihan == "5":
            laporan_absensi_harian()
        elif pilihan == "0":
            print("Terima kasih. Data tetap tersimpan.")
            break
        else:
            print("Menu tidak tersedia. Silakan pilih kembali.")


if __name__ == "__main__":
    try:
        menu()
    except (OSError, csv.Error) as error:
        print(f"Terjadi kesalahan saat mengakses file: {error}")