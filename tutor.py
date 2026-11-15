from sentence_transformers import SentenceTransformer, util
import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_PATH = os.path.join(BASE_DIR, 'maddyknowledgedatabase.json')  # Path to your knowledge base JSON file
THRESHOLD = 0.35  # change this to tune accuracy vs. out-of-scope rejection


class AITutor:
    def __init__(self):
        print("Loading sentence-transformers model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

        with open(KB_PATH, 'r', encoding='utf-8') as f:
            self.maddyknowledgedatabase = json.load(f)
        print(f"Loaded {len(self.maddyknowledgedatabase)} topics from maddyknowledgedatabase.json")

        print("Encoding knowledge base...")
        self.question_embeddings = self.model.encode(
            [item['question'] for item in self.maddyknowledgedatabase],
            convert_to_tensor=True
        )
        print("✓ Model loaded and ready!")

        self.history = []
        self.stats = {'total_questions': 0, 'avg_confidence': 0, 'topics_covered': 0}

    def answer_question(self, user_question):
        """Find the best matching answer using semantic similarity."""
        user_embedding = self.model.encode(user_question, convert_to_tensor=True)
        similarity_scores = util.cos_sim(user_embedding, self.question_embeddings)[0]

        best_idx = similarity_scores.argmax().item()
        confidence = float(similarity_scores[best_idx].item())
        confidence_percent = int(confidence * 100)

        if confidence < THRESHOLD:
            answer = ("I'm not sure about that yet. Try asking about AI, machine learning, "
                      "cybersecurity, Python, blockchain, or cloud computing.")
            topic = "Out of scope"
        else:
            best_match = self.maddyknowledgedatabase[best_idx]
            answer = best_match['answer']
            topic = best_match['topic']

        self.history.append({
            'user_question': user_question,
            'ai_answer': answer,
            'confidence': confidence_percent,
            'topic': topic,
            'timestamp': datetime.now().isoformat()
        })

        self.stats['total_questions'] += 1
        self.stats['avg_confidence'] = int(sum(h['confidence'] for h in self.history) / len(self.history))
        self.stats['topics_covered'] = len(set(h['topic'] for h in self.history if h['topic'] != 'Out of scope'))

        return answer, confidence_percent, topic

    def show_topics(self):
        """Return sorted list of all topics."""
        return sorted(set(item['topic'] for item in self.maddyknowledgedatabase))

    def related_topics(self, user_question, k=3):
        """Top-k retrieval: return the closest topics after the best match."""
        user_embedding = self.model.encode(user_question, convert_to_tensor=True)
        hits = util.semantic_search(user_embedding, self.question_embeddings, top_k=k)[0]
        related = []
        for hit in hits[1:]:  # skip the best match, it is already the answer
            if hit['score'] >= 0.30:
                related.append({
                    'topic': self.maddyknowledgedatabase[hit['corpus_id']]['topic'],
                    'confidence': int(hit['score'] * 100)
                })
        return related

    def get_stats(self):
        return self.stats

    def save_session(self, user_id):
        filename = os.path.join(BASE_DIR, f'session_{user_id}.json')
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({'history': self.history, 'stats': self.stats}, f, indent=4)