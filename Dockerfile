FROM python:3.11-slim
WORKDIR /app
# Install minimal system deps for Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libcairo2 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*
# Copy requirements
COPY requirements.txt .
# Install Python deps
RUN pip install --no-cache-dir -r requirements.txt
# Install ONLY chromium (important)
RUN playwright install chromium
# Copy app
COPY addNew.py createDb.py functions.py main.py /app/
# Optional cleanup (reduce size)
RUN rm -rf /usr/share/doc /usr/share/man /usr/share/locale/*
CMD ["python", "main.py"]