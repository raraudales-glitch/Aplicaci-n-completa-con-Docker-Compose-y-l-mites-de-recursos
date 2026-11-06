
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

COPY app.py .

RUN pip install --no-cache-dir -r requirements.txt



ENV APP_NOMBRE=g1-cpus-api

EXPOSE 5000

CMD ["python", "app.py"]
