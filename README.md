# BookLapang

Aplikasi web sederhana untuk memesan lapangan badminton dan futsal per jam. Projek ini dibuat untuk tugas Cloud Computing (BINUS) dan fokus pada containerization: aplikasi multi-tier (web + API + PostgreSQL) yang berjalan penuh di Docker Compose.

## Latar belakang
Pemesanan lapangan di sekitar kampus umumnya lewat chat WhatsApp, sehingga jadwal sering bentrok dan pemesan tidak tahu jam mana yang masih kosong. BookLapang menyimpan jadwal di basis data dan menolak pesanan pada slot yang sudah terisi.

## Teknologi
FastAPI (Python 3.12), PostgreSQL 16, Docker, Docker Compose. Frontend berupa satu halaman HTML yang disajikan oleh container yang sama dengan API.

## Cara menjalankan
Prasyarat: Docker Desktop atau Docker Engine dengan plugin Compose.

```bash
git clone <URL-REPO-ANDA>
cd booklapang
cp .env.example .env        # lalu ubah POSTGRES_PASSWORD
docker compose up -d --build
```

Buka http://localhost:8000

Menjalankan Adminer (profile `tools`) di http://localhost:8080:
```bash
docker compose --profile tools up -d
```
Server: `db`, pengguna dan password sesuai `.env`.

Menghentikan aplikasi (data tetap tersimpan di volume):
```bash
docker compose down
```
Menghentikan sekaligus menghapus data:
```bash
docker compose down -v
```

## Endpoint
| Method | Path | Keterangan | Status |
|---|---|---|---|
| GET | /health | cek aplikasi dan koneksi database | 200, 503 |
| GET | /bookings?booking_date=YYYY-MM-DD | daftar pesanan | 200 |
| POST | /bookings | buat pesanan | 201, 409 (slot terisi), 422 (input salah) |

Contoh:
```bash
curl -i -X POST localhost:8000/bookings -H "Content-Type: application/json" \
  -d '{"court":"Badminton A","name":"Naufal","booking_date":"2026-11-15","hour":19}'
```

## Struktur
```
app/main.py            API dan koneksi database
app/static/index.html  halaman web
Dockerfile             multi-stage build
docker-compose.yml     app, db, adminer (profile tools)
.env.example           contoh konfigurasi
```

