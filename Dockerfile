FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
ENV TZ=Asia/Seoul
CMD ["python", "app.py"]
