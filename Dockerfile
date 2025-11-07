# ---- Base image ----
FROM python:3.11-slim

# ---- Set working dir ----
WORKDIR /app

# ---- Install system deps ----
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
 && rm -rf /var/lib/apt/lists/*

# ---- Copy project files ----
COPY . .

# ---- Install Python deps ----
RUN pip install --no-cache-dir -r requirements.txt

# ---- Expose Streamlit port ----
EXPOSE 8501

# ---- Default command: Streamlit ----
CMD ["streamlit", "run", "src/ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
