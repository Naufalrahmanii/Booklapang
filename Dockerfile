# ---------- Stage 1: builder ----------
FROM python:3.12.8-slim-bookworm AS builder

WORKDIR /build

# virtualenv terpisah supaya mudah disalin ke stage runtime
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH" \
    PIP_NO_CACHE_DIR=1

# dependency disalin lebih dulu agar layer ini ter-cache selama requirements.txt tidak berubah
COPY requirements.txt .
RUN pip install -r requirements.txt

# ---------- Stage 2: runtime ----------
FROM python:3.12.8-slim-bookworm AS runtime

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# hanya virtualenv hasil build yang dibawa, tanpa cache pip atau alat build
COPY --from=builder /opt/venv /opt/venv

# source code disalin paling akhir karena paling sering berubah
COPY app ./app

# jalankan sebagai user biasa, bukan root
RUN useradd --system --no-create-home appuser
USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
