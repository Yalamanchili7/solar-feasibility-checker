FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system deps (if you need them later, keep minimal for now)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency list & install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Environment
ENV PYTHONUNBUFFERED=1

# Default command: user will pass --address at runtime
ENTRYPOINT ["python", "cli.py"]
