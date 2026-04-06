import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

class WebHallucinationDetector:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.threshold = 0.3  # similarity threshold

    # =========================
    # CLEAN TEXT
    # =========================
    def clean_text(self, text):
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        return text.strip()

    # =========================
    # FETCH WEB DATA
    # =========================
    def fetch_web_data(self, query):
        try:
            url = f"https://www.google.com/search?q={query}"
            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            response = requests.get(url, headers=headers, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")

            snippets = []

            # Extract Google search snippets
            for g in soup.find_all("div", class_="BNeawe s3v9rd AP7Wnd"):
                text = g.get_text()
                if len(text) > 50:  # filter short/noisy text
                    snippets.append(text)

            return snippets[:3]  # top 3 snippets

        except Exception:
            return []

    # =========================
    # SUMMARIZE RESPONSE
    # =========================
    def summarize_response(self, output):
        # Take only first meaningful line (avoids long-text mismatch)
        lines = output.split("\n")
        for line in lines:
            if len(line.strip()) > 20:
                return line[:300]
        return output[:300]

    # =========================
    # KEYWORD OVERLAP
    # =========================
    def keyword_overlap(self, text1, text2):
        words1 = set(self.clean_text(text1).split())
        words2 = set(self.clean_text(text2).split())
        return len(words1 & words2)

    # =========================
    # MAIN DETECTION LOGIC
    # =========================
    def detect(self, query, output):

        documents = self.fetch_web_data(query)

        # ⚠️ No web data → cannot verify
        if not documents:
            return {
                "hallucination": None,
                "confidence": 0.0,
                "evidence": "No web data",
                "web_available": False
            }

        # Use summarized response
        response_summary = self.summarize_response(output)

        # Clean texts
        response_summary = self.clean_text(response_summary)
        documents = [self.clean_text(doc) for doc in documents]

        # Generate embeddings
        response_embedding = self.model.encode([response_summary])
        doc_embeddings = self.model.encode(documents)

        # Compute similarity
        similarities = cosine_similarity(response_embedding, doc_embeddings)[0]
        max_score = max(similarities)

        # Keyword overlap check
        overlap_scores = [
            self.keyword_overlap(response_summary, doc) for doc in documents
        ]
        max_overlap = max(overlap_scores)

        # =========================
        # FINAL DECISION
        # =========================
        if max_score < self.threshold and max_overlap < 5:
            hallucination = True
        else:
            hallucination = False

        return {
            "hallucination": hallucination,
            "confidence": float(max_score),
            "evidence": documents[similarities.argmax()],
            "web_available": True
        }