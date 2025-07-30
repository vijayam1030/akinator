from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import random
from datetime import datetime
import requests
from dotenv import load_dotenv
from llm_integration import LLMIntegration

load_dotenv()

app = Flask(__name__)
CORS(app)

# Initialize LLM integration
llm_integration = LLMIntegration()

# Load the database
def load_database():
    try:
        with open('database.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"people": [], "questions": []}

def save_database(data):
    with open('database.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Initialize database with sample data
def initialize_database():
    db = load_database()
    if not db["people"]:
        db["people"] = [
            {
                "id": 1,
                "name": "Albert Einstein",
                "image": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Einstein_1921_by_F_Schmutzer_-_restoration.jpg",
                "description": "Famous physicist who developed the theory of relativity",
                "traits": {
                    "is_scientist": True,
                    "is_historical": True,
                    "is_male": True,
                    "is_dead": True,
                    "is_american": False,
                    "is_german": True,
                    "has_beard": True,
                    "is_physicist": True,
                    "won_nobel_prize": True,
                    "is_20th_century": True
                }
            },
            {
                "id": 2,
                "name": "Marie Curie",
                "image": "https://upload.wikimedia.org/wikipedia/commons/c/c8/Marie_Curie_c1920.jpg",
                "description": "Pioneering physicist and chemist who conducted research on radioactivity",
                "traits": {
                    "is_scientist": True,
                    "is_historical": True,
                    "is_male": False,
                    "is_dead": True,
                    "is_american": False,
                    "is_polish": True,
                    "has_beard": False,
                    "is_physicist": True,
                    "won_nobel_prize": True,
                    "is_20th_century": True
                }
            },
            {
                "id": 3,
                "name": "Leonardo da Vinci",
                "image": "https://upload.wikimedia.org/wikipedia/commons/c/c3/Leonardo_da_Vinci_-_presumed_self-portrait_-_WGA12798.jpg",
                "description": "Italian polymath of the Renaissance who was a painter, sculptor, architect, and scientist",
                "traits": {
                    "is_scientist": True,
                    "is_historical": True,
                    "is_male": True,
                    "is_dead": True,
                    "is_american": False,
                    "is_italian": True,
                    "has_beard": True,
                    "is_artist": True,
                    "is_inventor": True,
                    "is_renaissance": True
                }
            },
            {
                "id": 4,
                "name": "William Shakespeare",
                "image": "https://upload.wikimedia.org/wikipedia/commons/a/a2/Shakespeare.jpg",
                "description": "English playwright and poet, widely regarded as the greatest writer in the English language",
                "traits": {
                    "is_scientist": False,
                    "is_historical": True,
                    "is_male": True,
                    "is_dead": True,
                    "is_american": False,
                    "is_english": True,
                    "has_beard": False,
                    "is_writer": True,
                    "is_playwright": True,
                    "is_16th_century": True
                }
            },
            {
                "id": 5,
                "name": "Marilyn Monroe",
                "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Marilyn_Monroe_in_The_Seven_Year_Itch_trailer.jpg/800px-Marilyn_Monroe_in_The_Seven_Year_Itch_trailer.jpg",
                "description": "American actress, model, and singer who became a major sex symbol",
                "traits": {
                    "is_scientist": False,
                    "is_historical": True,
                    "is_male": False,
                    "is_dead": True,
                    "is_american": True,
                    "is_actress": True,
                    "has_beard": False,
                    "is_20th_century": True,
                    "is_blonde": True,
                    "is_hollywood": True
                }
            },
            {
                "id": 6,
                "name": "Elon Musk",
                "image": "https://upload.wikimedia.org/wikipedia/commons/9/99/Elon_Musk_Colorado_2022_%28cropped%29.jpg",
                "description": "Business magnate and investor who founded or co-founded several companies including Tesla and SpaceX",
                "traits": {
                    "is_scientist": False,
                    "is_historical": False,
                    "is_male": True,
                    "is_dead": False,
                    "is_american": True,
                    "is_businessman": True,
                    "has_beard": False,
                    "is_entrepreneur": True,
                    "is_tech": True,
                    "is_21st_century": True
                }
            },
            {
                "id": 7,
                "name": "Taylor Swift",
                "image": "https://upload.wikimedia.org/wikipedia/commons/f/fc/Taylor_Swift_2_-_2019_by_Glenn_Francis_%28cropped%29.jpg",
                "description": "American singer-songwriter whose narrative songwriting has received critical praise",
                "traits": {
                    "is_scientist": False,
                    "is_historical": False,
                    "is_male": False,
                    "is_dead": False,
                    "is_american": True,
                    "is_singer": True,
                    "has_beard": False,
                    "is_musician": True,
                    "is_pop": True,
                    "is_21st_century": True
                }
            },
            {
                "id": 8,
                "name": "Barack Obama",
                "image": "https://upload.wikimedia.org/wikipedia/commons/8/8d/President_Barack_Obama.jpg",
                "description": "American politician who served as the 44th president of the United States",
                "traits": {
                    "is_scientist": False,
                    "is_historical": False,
                    "is_male": True,
                    "is_dead": False,
                    "is_american": True,
                    "is_politician": True,
                    "has_beard": False,
                    "is_president": True,
                    "is_democrat": True,
                    "is_21st_century": True
                }
            }
        ]
    
    if not db["questions"]:
        db["questions"] = [
            {"id": 1, "text": "Is this person a scientist or researcher?", "trait": "is_scientist"},
            {"id": 2, "text": "Is this person from history (no longer alive)?", "trait": "is_historical"},
            {"id": 3, "text": "Is this person male?", "trait": "is_male"},
            {"id": 4, "text": "Is this person still alive?", "trait": "is_dead"},
            {"id": 5, "text": "Is this person American?", "trait": "is_american"},
            {"id": 6, "text": "Does this person have a beard?", "trait": "has_beard"},
            {"id": 7, "text": "Is this person a politician?", "trait": "is_politician"},
            {"id": 8, "text": "Is this person an artist or creative?", "trait": "is_artist"},
            {"id": 9, "text": "Is this person an entrepreneur or business person?", "trait": "is_entrepreneur"},
            {"id": 10, "text": "Is this person a musician or singer?", "trait": "is_musician"},
            {"id": 11, "text": "Is this person from the 20th century?", "trait": "is_20th_century"},
            {"id": 12, "text": "Is this person from the 21st century?", "trait": "is_21st_century"},
            {"id": 13, "text": "Is this person blonde?", "trait": "is_blonde"},
            {"id": 14, "text": "Is this person associated with Hollywood?", "trait": "is_hollywood"},
            {"id": 15, "text": "Is this person a writer or author?", "trait": "is_writer"}
        ]
    
    save_database(db)
    return db

# Initialize the database
database = initialize_database()

class AkinatorGame:
    def __init__(self):
        self.people = database["people"]
        self.questions = database["questions"]
        self.asked_questions = set()
        self.answers = {}
    
    def get_next_question(self):
        """Get the most informative question to ask next using LLM intelligence"""
        available_questions = [q for q in self.questions if q["id"] not in self.asked_questions]
        
        if not available_questions:
            return None
        
        # Always try to use LLM for smart question generation
        if llm_integration.current_llm != 'none':
            smart_question = llm_integration.generate_smart_question(
                self.people, 
                list(self.asked_questions), 
                self.answers
            )
            if smart_question:
                print(f"LLM generated question: {smart_question['text']}")
                return smart_question
        
        # If LLM is not available or failed, use intelligent fallback
        return self._get_best_fallback_question(available_questions)
    
    def _get_best_fallback_question(self, available_questions):
        """Get the best question from available ones using simple heuristics"""
        if not available_questions:
            return None
        
        # Score questions based on how well they split the remaining candidates
        question_scores = []
        
        for question in available_questions:
            trait = question["trait"]
            yes_count = 0
            no_count = 0
            
            for person in self.people:
                if trait in person["traits"]:
                    if person["traits"][trait]:
                        yes_count += 1
                    else:
                        no_count += 1
            
            # Prefer questions that split candidates more evenly
            total = yes_count + no_count
            if total > 0:
                balance = 1 - abs(yes_count - no_count) / total
                question_scores.append((question, balance))
        
        if question_scores:
            # Sort by balance score (higher is better)
            question_scores.sort(key=lambda x: x[1], reverse=True)
            return question_scores[0][0]
        
        return random.choice(available_questions)
    
    def add_answer(self, question_id, answer):
        """Add an answer to the game state"""
        self.asked_questions.add(question_id)
        self.answers[question_id] = answer
    
    def get_best_match(self):
        """Find the person that best matches the current answers"""
        if not self.answers:
            return None
        
        best_match = None
        best_score = 0
        
        for person in self.people:
            score = 0
            total_questions = 0
            
            for question_id, answer in self.answers.items():
                question = next(q for q in self.questions if q["id"] == question_id)
                trait = question["trait"]
                
                if trait in person["traits"]:
                    total_questions += 1
                    if person["traits"][trait] == answer:
                        score += 1
            
            if total_questions > 0:
                match_percentage = score / total_questions
                if match_percentage > best_score:
                    best_score = match_percentage
                    best_match = person
        
        if best_match and best_score > 0.5:
            # Use LLM for confidence analysis if available
            if llm_integration.current_llm != 'none':
                confidence = llm_integration.analyze_confidence(best_match, self.answers)
                best_match['llm_confidence'] = confidence
            return best_match
        return None

@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game"""
    game = AkinatorGame()
    question = game.get_next_question()
    
    # Ensure the question has the text field
    if question and 'text' not in question:
        # Find the question in the database
        db_question = next((q for q in game.questions if q["id"] == question["id"]), None)
        if db_question:
            question = db_question
    
    return jsonify({
        "game_id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "question": question,
        "progress": 0
    })

@app.route('/api/answer', methods=['POST'])
def answer_question():
    """Submit an answer and get the next question or result"""
    data = request.json
    question_id = data.get('question_id')
    answer = data.get('answer')  # True/False
    game_state = data.get('game_state', {})
    
    # Reconstruct game state
    game = AkinatorGame()
    game.asked_questions = set(game_state.get('asked_questions', []))
    # Convert answer keys to integers to ensure consistent types
    answers = game_state.get('answers', {})
    game.answers = {int(k): v for k, v in answers.items()}
    
    # Add the new answer
    game.add_answer(question_id, answer)
    
    # Check if we have enough information to make a guess
    if len(game.asked_questions) >= 5:
        best_match = game.get_best_match()
        if best_match:
            return jsonify({
                "type": "result",
                "person": best_match,
                "confidence": 0.8,
                "questions_asked": len(game.asked_questions)
            })
    
    # Get next question
    next_question = game.get_next_question()
    
    # Ensure the question has the text field
    if next_question and 'text' not in next_question:
        # Find the question in the database
        db_question = next((q for q in game.questions if q["id"] == next_question["id"]), None)
        if db_question:
            next_question = db_question
    
    if next_question:
        progress = len(game.asked_questions) / len(game.questions) * 100
        return jsonify({
            "type": "question",
            "question": next_question,
            "progress": progress,
            "game_state": {
                "asked_questions": list(game.asked_questions),
                "answers": {str(k): v for k, v in game.answers.items()}
            }
        })
    else:
        # No more questions, make best guess
        best_match = game.get_best_match()
        return jsonify({
            "type": "result",
            "person": best_match,
            "confidence": 0.6 if best_match else 0.0,
            "questions_asked": len(game.asked_questions)
        })

@app.route('/api/people', methods=['GET'])
def get_people():
    """Get all people in the database"""
    return jsonify({"people": database["people"]})

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Get all questions"""
    return jsonify({"questions": database["questions"]})

@app.route('/api/llm-status', methods=['GET'])
def get_llm_status():
    """Get LLM availability status"""
    return jsonify({
        "available_llms": llm_integration.get_available_llms_info(),
        "current_llm": llm_integration.current_llm
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000) 