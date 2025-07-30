import logging
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('akinator_game.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

class AkinatorGame:
    def __init__(self):
        self.asked_questions = set()
        self.answers = {}
        self.people_considered = []
        self.current_confidence = 0.0
        self.best_match = None
    
    def get_next_question(self):
        """Get the most informative question to ask next using LLM intelligence"""
        logger.info(f"Getting next question - asked_questions: {self.asked_questions}")
        logger.info(f"Current answers: {self.answers}")
        
        # Use LLM to generate the next best question
        if llm_integration.current_llm != 'none':
            question = llm_integration.generate_smart_question(self.answers, self.asked_questions)
            if question:
                logger.info(f"LLM generated question: {question}")
                return {"id": len(self.asked_questions) + 1, "text": question, "trait": "llm_generated"}
        
        # Fallback questions if LLM is not available
        fallback_questions = [
            "Is this person a scientist or researcher?",
            "Is this person from history (no longer alive)?",
            "Is this person male?",
            "Is this person still alive?",
            "Is this person American?",
            "Does this person have a beard?",
            "Is this person a politician?",
            "Is this person an artist or creative?",
            "Is this person an entrepreneur or business person?",
            "Is this person a musician or singer?",
            "Is this person from the 20th century?",
            "Is this person from the 21st century?",
            "Is this person blonde?",
            "Is this person associated with Hollywood?",
            "Is this person a writer or author?"
        ]
        
        available_questions = [q for i, q in enumerate(fallback_questions) if i not in self.asked_questions]
        if available_questions:
            selected_question = random.choice(available_questions)
            logger.info(f"Fallback question: {selected_question}")
            return {"id": len(self.asked_questions) + 1, "text": selected_question, "trait": "fallback"}
        
        return None
    
    def add_answer(self, question_id, answer):
        """Add an answer to the game state"""
        logger.info(f"Adding answer - Question ID: {question_id}, Answer: {answer}")
        self.asked_questions.add(question_id)
        
        # Handle special answer types
        if answer == 'unsure' or answer == 'dont_know':
            # For unsure/don't know, we'll skip this question in scoring
            self.answers[question_id] = None
            logger.info(f"Special answer '{answer}' - skipping in scoring")
        else:
            self.answers[question_id] = answer
            
        logger.info(f"Updated asked_questions: {self.asked_questions}")
        logger.info(f"Updated answers: {self.answers}")
    
    def get_best_match(self):
        """Use LLM to find the best match based on current answers"""
        if not self.answers or len([a for a in self.answers.values() if a is not None]) < 2:
            return None
        
        logger.info("=== Finding best match using LLM ===")
        
        if llm_integration.current_llm != 'none':
            # Use LLM to identify the person
            person_info = llm_integration.identify_person(self.answers)
            if person_info:
                logger.info(f"LLM identified: {person_info}")
                return person_info
        
        # Fallback: return None if LLM can't identify
        logger.info("LLM could not identify the person")
        return None
    
    def should_make_guess(self):
        """Determine if we should make a guess based on confidence and questions asked"""
        if len(self.asked_questions) < 3:
            return False
        
        if llm_integration.current_llm != 'none':
            # Use LLM to determine if we should guess
            confidence = llm_integration.analyze_confidence_for_guess(self.answers)
            logger.info(f"LLM confidence for guessing: {confidence}")
            return confidence > 0.7
        else:
            # Fallback: guess after 7 questions
            return len(self.asked_questions) >= 7

@app.route('/api/start', methods=['POST'])
def start_game():
    """Start a new game"""
    logger.info("=== Starting new game ===")
    game = AkinatorGame()
    question = game.get_next_question()
    
    logger.info(f"First question: {question}")
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
    answer = data.get('answer')  # True/False/unsure/dont_know
    game_state = data.get('game_state', {})
    
    logger.info(f"=== Answer received ===")
    logger.info(f"Question ID: {question_id}, Answer: {answer}")
    logger.info(f"Game state: {game_state}")
    
    # Reconstruct game state
    game = AkinatorGame()
    game.asked_questions = set(game_state.get('asked_questions', []))
    # Convert answer keys to integers to ensure consistent types
    answers = game_state.get('answers', {})
    game.answers = {int(k): v for k, v in answers.items()}
    
    logger.info(f"Reconstructed asked_questions: {game.asked_questions}")
    logger.info(f"Reconstructed answers: {game.answers}")
    
    # Add the new answer
    game.add_answer(question_id, answer)
    
    logger.info(f"After adding answer - asked_questions: {game.asked_questions}")
    logger.info(f"After adding answer - answers: {game.answers}")
    
    # Check if we should make a guess
    if game.should_make_guess():
        best_match = game.get_best_match()
        if best_match:
            confidence = llm_integration.analyze_confidence(best_match, game.answers) if llm_integration.current_llm != 'none' else 0.8
            return jsonify({
                "type": "result",
                "person": best_match,
                "confidence": confidence,
                "questions_asked": len(game.asked_questions)
            })
    
    # Get next question
    next_question = game.get_next_question()
    
    if next_question:
        progress = len(game.asked_questions) / 15 * 100  # Assume max 15 questions
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

@app.route('/api/llm-status', methods=['GET'])
def get_llm_status():
    """Get LLM availability status"""
    return jsonify({
        "available_llms": llm_integration.get_available_llms_info(),
        "current_llm": llm_integration.current_llm
    })

if __name__ == '__main__':
    app.run(debug=False, port=5000) 