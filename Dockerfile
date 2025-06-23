FROM python:3.9-slim

RUN apt-get update && apt-get install -y ffmpeg fonts-dejavu

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "bot.py"]
