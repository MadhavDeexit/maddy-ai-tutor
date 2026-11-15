FROM python:3.11-slim

WORKDIR /app

# CPU-only PyTorch keeps the image much smaller
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download the model at build time so startup is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

COPY . .

EXPOSE 5000

# 1 worker: the model is loaded once and rate limits stay consistent
CMD ["gunicorn", "--workers", "1", "--timeout", "120", "--bind", "0.0.0.0:5000", "app:app"]