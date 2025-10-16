FROM python:3.11-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc python3-dev libffi-dev libssl-dev tzdata && \
    rm -rf /var/lib/apt/lists/*
ENV TZ=Asia/Seoul PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY . .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --default-timeout=120 --prefer-binary -r requirements.txt
CMD ["python", "app.py"]
