# Maddy AI Tutor

A semantic-search AI tutor built with Flask and sentence-transformers. It answers technical questions on AI, cybersecurity, and software engineering by matching questions to a knowledge base using sentence embeddings and cosine similarity.

**Author:** Madhav Deexit | B.Tech CSE (Cyber Security), Mentor: Dr. Rahul Saxena

## Features
- Semantic question matching (all-MiniLM-L6-v2, 384-dim embeddings)
- 52-topic knowledge base in an external JSON file
- Top-k retrieval: best answer plus related topics (the retrieval stage of RAG)
- Out-of-scope fallback using a tuned confidence threshold
- Security: rate limiting, input validation, sanitized user IDs
- Request logging with response times
- Evaluation script with accuracy metrics
- Dockerized deployment

## Architecture
User question -> Flask API -> sentence embedding -> cosine similarity vs. knowledge base -> best match + top-k related topics -> JSON response -> chat UI

## Evaluation
Run on 42 paraphrased questions (36 in-scope, 6 out-of-scope):

| Metric | Result |
|---|---|
| Overall accuracy | [88.1%] |
| In-scope accuracy | [86.1%] |
| Out-of-scope rejection | [100.0%] |
| Average response time | [16 ms] |

## Run locally
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000

## Run with Docker
```bash
docker build -t maddy-ai-tutor .
docker run -p 8080:5000 maddy-ai-tutor
```

## Run the evaluation
```bash
python evaluate.py
```

## Tech stack
Python, Flask, Flask-Limiter, sentence-transformers, PyTorch, Docker, Gunicorn

## Future work
SQLite persistence, FAISS for large knowledge bases, user authentication, mobile app