FROM python:3.11-slim

# ── Cài các gói hệ thống cần thiết cho matplotlib ──
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# ── Thiết lập thư mục làm việc ──
WORKDIR /app

# ── Copy requirements trước để tận dụng Docker cache ──
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy toàn bộ source code ──
COPY . .

# ── Mở port mặc định của Streamlit ──
EXPOSE 8501

# ── Lệnh khởi chạy dashboard ──
CMD ["streamlit", "run", "dashboard/app.py", "--server.headless=true", "--server.port=8501"]