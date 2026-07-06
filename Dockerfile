FROM python:3.12-slim

WORKDIR /app

RUN apt update && apt install -y openjdk-25-jre

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]