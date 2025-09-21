FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential gcc g++ \
    libatlas-base-dev gfortran \
    curl git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Pre-create processed dir
RUN mkdir -p data/processed outputs && chmod +x entrypoint.sh

EXPOSE 8501 8000
CMD ["./entrypoint.sh"]
