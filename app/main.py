import os
import time
from datetime import date

import psycopg
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

DB_URL = (
    f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
    f"@{os.environ.get('DB_HOST', 'db')}:{os.environ.get('DB_PORT', '5432')}"
    f"/{os.environ['POSTGRES_DB']}"
)

SCHEMA = """
CREATE TABLE IF NOT EXISTS bookings (
    id           SERIAL PRIMARY KEY,
    court        VARCHAR(50) NOT NULL,
    name         VARCHAR(100) NOT NULL,
    booking_date DATE NOT NULL,
    hour         SMALLINT NOT NULL CHECK (hour BETWEEN 8 AND 22),
    created_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (court, booking_date, hour)
);
"""

app = FastAPI(title="BookLapang")


class BookingIn(BaseModel):
    court: str = Field(min_length=1, max_length=50)
    name: str = Field(min_length=1, max_length=100)
    booking_date: date
    hour: int = Field(ge=8, le=22)


def connect():
    return psycopg.connect(DB_URL, connect_timeout=3)


@app.on_event("startup")
def init_db():
    # database biasanya sudah healthy, retry hanya sebagai pengaman tambahan
    for attempt in range(10):
        try:
            with connect() as conn:
                conn.execute(SCHEMA)
            return
        except psycopg.OperationalError:
            time.sleep(2)
    raise RuntimeError("Tidak bisa terhubung ke database")


@app.get("/health")
def health():
    try:
        with connect() as conn:
            conn.execute("SELECT 1")
    except psycopg.Error:
        raise HTTPException(status_code=503, detail="database tidak tersedia")
    return {"status": "ok"}


@app.get("/bookings")
def list_bookings(booking_date: date | None = Query(default=None)):
    sql = "SELECT id, court, name, booking_date, hour FROM bookings"
    params: tuple = ()
    if booking_date:
        sql += " WHERE booking_date = %s"
        params = (booking_date,)
    sql += " ORDER BY booking_date, hour, court"
    with connect() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [
        {"id": r[0], "court": r[1], "name": r[2], "booking_date": r[3].isoformat(), "hour": r[4]}
        for r in rows
    ]


@app.post("/bookings", status_code=201)
def create_booking(b: BookingIn):
    try:
        with connect() as conn:
            row = conn.execute(
                "INSERT INTO bookings (court, name, booking_date, hour) "
                "VALUES (%s, %s, %s, %s) RETURNING id",
                (b.court, b.name, b.booking_date, b.hour),
            ).fetchone()
    except psycopg.errors.UniqueViolation:
        raise HTTPException(status_code=409, detail="Slot sudah dipesan")
    return {"id": row[0], **b.model_dump(mode="json")}


@app.get("/")
def index():
    return FileResponse("app/static/index.html")


app.mount("/static", StaticFiles(directory="app/static"), name="static")
