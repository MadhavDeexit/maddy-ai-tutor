from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from tutor import AITutor
import json
import logging
import re
import time

# ---------- Logging (MLOps monitoring) ----------
logging.basicConfig(
    filename='tutor.log',
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s'
)

app = Flask(__name__)
CORS(app)

# ---------- Rate limiting (API security) ----------
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per hour"]
)

print("Loading AI model...")
tutor = AITutor()
print("✓ Ready to answer questions!")

MAX_QUESTION_LENGTH = 300


def clean_input(text):
    """Basic input validation: trim, limit length, strip HTML tags."""
    text = str(text).strip()
    text = re.sub(r'<[^>]*>', '', text)
    return text[:MAX_QUESTION_LENGTH]


def safe_user_id(user_id):
    """Only allow letters, numbers and underscores (prevents path tricks in filenames)."""
    return re.sub(r'[^a-zA-Z0-9_]', '', str(user_id))[:40] or 'guest'


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/ask', methods=['POST'])
@limiter.limit("10 per minute")
def ask_question():
    start = time.time()
    data = request.get_json(silent=True) or {}
    question = clean_input(data.get('question', ''))
    user_id = safe_user_id(data.get('user_id', 'guest'))

    if not question:
        logging.warning(f"Empty question from {get_remote_address()}")
        return jsonify({'answer': 'Please type a question.', 'confidence': 0, 'topic': 'Invalid'}), 400

    answer, confidence, topic = tutor.answer_question(question)
    related = tutor.related_topics(question) if topic != "Out of scope" else []
    tutor.save_session(user_id)

    elapsed_ms = int((time.time() - start) * 1000)
    logging.info(f"user={user_id} | q='{question}' | topic={topic} | conf={confidence}% | {elapsed_ms}ms")

    return jsonify({'answer': answer, 'confidence': confidence, 'topic': topic, 'related': related})

@app.errorhandler(429)
def too_many_requests(e):
    logging.warning(f"Rate limit hit from {get_remote_address()}")
    return jsonify({'answer': 'Too many questions! Please wait a minute and try again.',
                    'confidence': 0, 'topic': 'Rate limited'}), 429


@app.route('/api/topics', methods=['GET'])
def get_topics():
    return jsonify(tutor.show_topics())


@app.route('/api/history/<user_id>', methods=['GET'])
def get_history(user_id):
    try:
        with open(f'session_{safe_user_id(user_id)}.json', 'r') as f:
            return jsonify(json.load(f).get('history', []))
    except Exception:
        return jsonify([])


@app.route('/api/stats/<user_id>', methods=['GET'])
def get_stats(user_id):
    try:
        with open(f'session_{safe_user_id(user_id)}.json', 'r') as f:
            return jsonify(json.load(f).get('stats', {}))
    except Exception:
        return jsonify({'total_questions': 0, 'avg_confidence': 0, 'topics_covered': 0})


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=5000)