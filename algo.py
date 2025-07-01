import json
import logging
from typing import Dict, List, Optional, Union
from sentence_transformers import SentenceTransformer, util
import google.generativeai as genai
from datetime import datetime
import asyncio

# Configure standard logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Custom logger for finance-style logs
class FinanceLogger:
    def __init__(self):
        self.logger = logging.getLogger("FinanceLogger")

    def initialize(self):
        pass

    def log(self, event_type: str, message: str, context: Dict = None):
        log_entry = {
            "type": event_type,
            "message": message,
            "timestamp": datetime.now().isoformat(),
            **(context or {})
        }
        self.logger.info(f"[FinanceLog] {log_entry}")

    def info(self, message: str):
        self.logger.info(message)

    def error(self, message: str, error: Exception = None, context: Dict = None):
        log_entry = {
            "error": str(error) if error else "",
            "stack": str(error.__traceback__) if error else "",
            **(context or {})
        }
        self.log("error", message, log_entry)

finance_logger = FinanceLogger()

class FAQBot:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.initialize_gemini()
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.faq_data = self.load_faq_data()
        self.faq_questions = [item['question'] for item in self.faq_data]
        self.faq_embeddings = self.model.encode(self.faq_questions, convert_to_tensor=True)

    def initialize_gemini(self):
        try:
            genai.configure(api_key=self.api_key)
            models = genai.list_models()
            logger.info("Available models:")
            for model in models:
                logger.info(model.name)
        except Exception as e:
            finance_logger.error("Error initializing Gemini API", e)

    def load_faq_data(self) -> List[Dict]:
        try:
            with open('faq.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            finance_logger.error("Error loading FAQ data", e)
            return []

    def process_speech(self, text: str) -> Optional[str]:
        try:
            user_embedding = self.model.encode(text, convert_to_tensor=True)
            scores = util.cos_sim(user_embedding, self.faq_embeddings)[0]
            best_idx = int(scores.argmax())
            best_score = float(scores[best_idx])

            logger.info(f"Best score: {best_score}")
            logger.info(f"Best index: {best_idx}")
            logger.info(f"Best question: {self.faq_questions[best_idx]}")

            if best_score > 0.3:
                return self.faq_data[best_idx]['answer']
            return None
        except Exception as e:
            finance_logger.error("Error processing speech", e)
            return None

    def get_gemini_prompt(self, question: str, faq_data: List[Dict]) -> str:
        faq_text = json.dumps(faq_data, indent=2)
        current_date = datetime.now().strftime("%Y-%m-%d")
    
        prompt = f"""
    You are a helpful FAQ assistant that must respond with accurate information based on the provided FAQ data.
    If you don't know the answer, say you don't know rather than making up information.
    
    Current date: {current_date}
    FAQ Data: {faq_text}
    
    User question: "{question}"
    
    Please provide a detailed, human-like response to the user's question.
   
    
    If you can't find a relevant answer in the FAQ data, respond with:
    "I'm sorry, I couldn't find information about that in our database. Could you please rephrase your question or ask something else?"
    
    Important rules:
    1. Always be polite and professional
    2. If the answer exists in the FAQ data, use that information
    3. Don't make up answers - only use information from the FAQ data
    4. Keep responses concise but friendly
    """
        return prompt
    
    
    async def generate_response(self, question: str) -> str:
        logger.info(f"Processing question: {question}")

        fixed_answer = self.process_speech(question)
        logger.info(f"Fixed answer: {fixed_answer}")

        if fixed_answer:
            try:
                prompt = self.get_gemini_prompt(question, [{"question": question, "answer": fixed_answer}])
                gemini_model = genai.GenerativeModel('gemini-1.5-flash')
                response = await gemini_model.generate_content_async(prompt)
                logger.info(f"Gemini API response: {response.text}")
                return response.text
            except Exception as e:
                finance_logger.error("Error calling Gemini API (fixed match)", e)
                return fixed_answer

        try:
            prompt = self.get_gemini_prompt(question, self.faq_data)
            gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            response = await gemini_model.generate_content_async(prompt)
            logger.info(f"Gemini API response: {response.text}")
            return response.text
        except Exception as e:
            finance_logger.error("Error calling Gemini API (full FAQ)", e)
            return "I'm sorry, I couldn't find information about that in our database. Could you please rephrase your question or ask something else?"

# Example usage
async def main():
    bot = FAQBot(api_key="AIzaSyBYGcNPmwiakoc03KXGZkTXW-btfGt_itk")

    print("=== FAQ Bot (Semantic) ===")
    while True:
        try:
            user_input = input("\nYou: ")
            if user_input.lower() in ["exit", "quit"]:
                break

            response = await bot.generate_response(user_input)
            print("Bot:", response)
        except KeyboardInterrupt:
            break
        except Exception as e:
            finance_logger.error("Error in main loop", e)
            print("Bot: I'm sorry, I encountered an error. Please try again.")

if __name__ == "__main__":
    asyncio.run(main())