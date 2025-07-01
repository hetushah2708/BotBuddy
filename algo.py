# algo.py
import json
from sentence_transformers import SentenceTransformer, util

# Load model once
model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast & accurate

# Load FAQ
with open('faq.json', 'r', encoding='utf-8') as f:
    faq_data = json.load(f)

faq_questions = [item['question'] for item in faq_data]
faq_embeddings = model.encode(faq_questions, convert_to_tensor=True)

def process_speech(text):
    user_embedding = model.encode(text, convert_to_tensor=True)

    # Compute cosine similarity
    scores = util.cos_sim(user_embedding, faq_embeddings)[0]

    best_idx = int(scores.argmax())
    best_score = float(scores[best_idx])

    if best_score > 0.4:  # Confidence threshold (adjustable)
        return faq_data[best_idx]['answer']
    else:
        return "I'm sorry, I didn't quite catch that. Could you please rephrase your question?"

# Test CLI
if __name__ == "__main__":
    print("=== FAQ Bot (Semantic) ===")
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break
            response = process_speech(user_input)
            print("Bot:", response)
        except KeyboardInterrupt:
            break