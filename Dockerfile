# ──────────────────────────────────────────────
# Imagem base com Python + Chrome para Selenium
# ──────────────────────────────────────────────
FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/opt/oracle/instantclient_19_19

# ──────────────────────────────────────────────
# Instala dependências + Google Chrome
# ──────────────────────────────────────────────
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    gnupg \
    ca-certificates \
    libnss3 \
    libfontconfig1 \
    libxss1 \
    libasound2t64 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libaio1t64 \
    --no-install-recommends && \
    curl -fsSL https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] \
        http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    CHROME_VERSION=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+') && \
    wget -q "https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip && \
    unzip /tmp/chromedriver.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
    chmod +x /usr/bin/chromedriver && \
    rm -rf /tmp/chromedriver* && \
    rm -rf /var/lib/apt/lists/*

# ──────────────────────────────────────────────
# Instala Oracle Instant Client 19c
# ──────────────────────────────────────────────
RUN wget -q https://download.oracle.com/otn_software/linux/instantclient/1919000/instantclient-basiclite-linux.x64-19.19.0.0.0dbru.zip \
        -O /tmp/oracle.zip && \
    unzip /tmp/oracle.zip -d /opt/oracle && \
    rm /tmp/oracle.zip && \
    echo /opt/oracle/instantclient_19_19 > /etc/ld.so.conf.d/oracle.conf && \
    ldconfig && \
    ln -s /usr/lib/x86_64-linux-gnu/libaio.so.1t64 /usr/lib/x86_64-linux-gnu/libaio.so.1

# ──────────────────────────────────────────────
# Diretório de trabalho
# ──────────────────────────────────────────────
WORKDIR /app

# ──────────────────────────────────────────────
# Instala dependências Python
# ──────────────────────────────────────────────
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt

# ──────────────────────────────────────────────
# Copia o código do projeto
# ──────────────────────────────────────────────
COPY . .

# ──────────────────────────────────────────────
# Roda o robô
# ──────────────────────────────────────────────
CMD ["python", "src/main.py"]