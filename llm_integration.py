import os
import json
import requests
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()

class LLMIntegration:
    """Integration with various LLMs for smarter question generation and analysis"""
    
    def __init__(self):
        self.available_llms = self._detect_available_llms()
        self.current_llm = self._select_best_llm()
    
    def _detect_available_llms(self) -> Dict[str, bool]:
        """Detect which LLMs are available - focus on local Ollama models"""
        llms = {
            'local_ollama': self._check_ollama_availability(),
            'openai': bool(os.getenv('OPENAI_API_KEY')),  # Fallback
            'anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),  # Fallback
            'huggingface': bool(os.getenv('HUGGINGFACE_API_KEY'))  # Fallback
        }
        return llms
    
    def _check_ollama_availability(self) -> bool:
        """Check if Ollama is running locally and get available models"""
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                self.available_ollama_models = response.json().get('models', [])
                return True
            return False
        except:
            self.available_ollama_models = []
            return False
    
    def _select_best_ollama_model(self, task_type: str = "general") -> str:
        """Select the best Ollama model for a specific task"""
        if not hasattr(self, 'available_ollama_models') or not self.available_ollama_models:
            return "llama2"  # Default fallback
        
        # Model preferences for different tasks
        model_preferences = {
            "question_generation": ["llama2", "codellama", "mistral", "llama2:13b", "llama2:7b"],
            "confidence_analysis": ["llama2", "mistral", "codellama", "llama2:13b"],
            "general": ["llama2", "mistral", "codellama", "llama2:13b", "llama2:7b"]
        }
        
        preferred_models = model_preferences.get(task_type, model_preferences["general"])
        
        # Check which preferred models are available
        available_model_names = [model.get('name', '') for model in self.available_ollama_models]
        
        for preferred in preferred_models:
            for model in self.available_ollama_models:
                model_name = model.get('name', '')
                if preferred in model_name:
                    return model_name
        
        # If no preferred models found, return the first available
        if available_model_names:
            return available_model_names[0]
        
        return "llama2"  # Ultimate fallback
    
    def _select_best_llm(self) -> str:
        """Select the best available LLM - prioritize local Ollama"""
        if self.available_llms['local_ollama']:
            return 'local_ollama'
        elif self.available_llms['openai']:
            return 'openai'
        elif self.available_llms['anthropic']:
            return 'anthropic'
        elif self.available_llms['huggingface']:
            return 'huggingface'
        else:
            return 'none'
    
    def generate_smart_question(self, people: List[Dict], asked_questions: List[int], 
                               answers: Dict[int, bool]) -> Optional[Dict]:
        """Generate the most informative question to ask next"""
        
        if self.current_llm == 'none':
            return None  # Fall back to random selection
        
        # Prepare context for the LLM
        context = self._prepare_context(people, asked_questions, answers)
        
        if self.current_llm == 'openai':
            return self._generate_with_openai(context)
        elif self.current_llm == 'anthropic':
            return self._generate_with_anthropic(context)
        elif self.current_llm == 'local_ollama':
            return self._generate_with_ollama(context)
        elif self.current_llm == 'huggingface':
            return self._generate_with_huggingface(context)
        
        return None
    
    def _prepare_context(self, people: List[Dict], asked_questions: List[int], 
                        answers: Dict[int, bool]) -> str:
        """Prepare comprehensive context for LLM"""
        
        # Create detailed summaries of available people
        people_summary = []
        for person in people:
            positive_traits = [k.replace('is_', '').replace('has_', '').replace('_', ' ') 
                             for k, v in person['traits'].items() if v]
            negative_traits = [k.replace('is_', '').replace('has_', '').replace('_', ' ') 
                             for k, v in person['traits'].items() if not v]
            
            summary = f"{person['name']} ({person['description']}): "
            if positive_traits:
                summary += f"Positive traits: {', '.join(positive_traits)}. "
            if negative_traits:
                summary += f"Negative traits: {', '.join(negative_traits)}."
            people_summary.append(summary)
        
        # Create detailed question-answer mapping
        question_mapping = {
            1: "Is this person a scientist or researcher?",
            2: "Is this person from history (no longer alive)?",
            3: "Is this person male?",
            4: "Is this person still alive?",
            5: "Is this person American?",
            6: "Does this person have a beard?",
            7: "Is this person a politician?",
            8: "Is this person an artist or creative?",
            9: "Is this person an entrepreneur or business person?",
            10: "Is this person a musician or singer?",
            11: "Is this person from the 20th century?",
            12: "Is this person from the 21st century?",
            13: "Is this person blonde?",
            14: "Is this person associated with Hollywood?",
            15: "Is this person a writer or author?"
        }
        
        # Create detailed question-answer summary
        question_answers = []
        for qid, answer in answers.items():
            question_text = question_mapping.get(qid, f"Question {qid}")
            question_answers.append(f"'{question_text}' - {'Yes' if answer else 'No'}")
        
        # Calculate remaining candidates
        remaining_people = self._get_remaining_candidates(people, answers, question_mapping)
        
        context = f"""
        You are playing an Akinator-style guessing game. Your goal is to ask the most strategic question to narrow down the person the user is thinking of.

        AVAILABLE PEOPLE ({len(people)} total):
        {chr(10).join(people_summary)}

        PREVIOUS QUESTIONS AND ANSWERS:
        {chr(10).join(question_answers) if question_answers else 'No questions asked yet.'}

        REMAINING LIKELY CANDIDATES ({len(remaining_people)} people):
        {chr(10).join([f"- {p['name']}" for p in remaining_people]) if remaining_people else 'All people are still possible candidates.'}

        TASK: Generate the most strategic yes/no question that will help eliminate the most people possible. Consider:
        1. Which question would split the remaining candidates most evenly?
        2. Which question targets the most distinctive traits?
        3. Which question would provide the most valuable information?

        Return ONLY the question text, nothing else.
        """
        
        return context
    
    def _get_remaining_candidates(self, people: List[Dict], answers: Dict[int, bool], 
                                 question_mapping: Dict[int, str]) -> List[Dict]:
        """Calculate which people are still possible candidates based on current answers"""
        if not answers:
            return people
        
        remaining = []
        for person in people:
            is_possible = True
            for qid, answer in answers.items():
                question_text = question_mapping.get(qid, "")
                trait = self._extract_trait_from_question(question_text)
                
                if trait and trait in person['traits']:
                    if person['traits'][trait] != answer:
                        is_possible = False
                        break
            
            if is_possible:
                remaining.append(person)
        
        return remaining
    
    def _extract_trait_from_question(self, question_text: str) -> Optional[str]:
        """Extract the trait from a question text"""
        trait_mapping = {
            "scientist or researcher": "is_scientist",
            "from history": "is_historical",
            "male": "is_male",
            "still alive": "is_dead",
            "American": "is_american",
            "beard": "has_beard",
            "politician": "is_politician",
            "artist or creative": "is_artist",
            "entrepreneur or business person": "is_entrepreneur",
            "musician or singer": "is_musician",
            "20th century": "is_20th_century",
            "21st century": "is_21st_century",
            "blonde": "is_blonde",
            "associated with Hollywood": "is_hollywood",
            "writer or author": "is_writer"
        }
        
        for key, trait in trait_mapping.items():
            if key.lower() in question_text.lower():
                return trait
        
        return None
    
    def _generate_with_openai(self, context: str) -> Optional[Dict]:
        """Generate question using OpenAI"""
        try:
            import openai
            openai.api_key = os.getenv('OPENAI_API_KEY')
            
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Use GPT-4 for better reasoning
                messages=[
                    {"role": "system", "content": """You are an expert at playing Akinator-style guessing games. Your goal is to ask the most strategic question that will help narrow down the person the user is thinking of.

Your response should be:
1. A clear, specific yes/no question
2. Focused on distinctive traits that will eliminate many candidates
3. Based on the current game state and remaining candidates
4. Natural and conversational in tone

Return ONLY the question text, nothing else."""},
                    {"role": "user", "content": context}
                ],
                max_tokens=100,
                temperature=0.3  # Lower temperature for more consistent reasoning
            )
            
            question_text = response.choices[0].message.content.strip()
            
            # Clean up the response
            if question_text.startswith('"') and question_text.endswith('"'):
                question_text = question_text[1:-1]
            
            # Generate a unique ID and trait for this LLM-generated question
            import hashlib
            question_hash = hashlib.md5(question_text.encode()).hexdigest()[:8]
            
            return {
                "id": int(f"100{question_hash}", 16) % 10000,  # Generate unique ID
                "text": question_text,
                "trait": f"llm_generated_{question_hash}"
            }
        except Exception as e:
            print(f"OpenAI error: {e}")
            return None
    
    def _generate_with_anthropic(self, context: str) -> Optional[Dict]:
        """Generate question using Anthropic Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=50,
                messages=[
                    {"role": "user", "content": context}
                ]
            )
            
            question_text = response.content[0].text.strip()
            return {
                "id": len(context) + 1,
                "text": question_text,
                "trait": f"llm_generated_{len(context)}"
            }
        except Exception as e:
            print(f"Anthropic error: {e}")
            return None
    
    def _generate_with_ollama(self, context: str) -> Optional[Dict]:
        """Generate question using local Ollama with best available model"""
        try:
            # Select the best model for question generation
            best_model = self._select_best_ollama_model("question_generation")
            print(f"Using Ollama model: {best_model}")
            
            # Enhanced prompt for better question generation
            enhanced_prompt = f"""You are an expert at playing Akinator-style guessing games. Your goal is to ask the most strategic question that will help narrow down the person the user is thinking of.

{context}

Your response should be:
1. A clear, specific yes/no question
2. Focused on distinctive traits that will eliminate many candidates
3. Based on the current game state and remaining candidates
4. Natural and conversational in tone

Return ONLY the question text, nothing else."""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": best_model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "top_p": 0.9,
                        "num_predict": 100
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                question_text = response.json()['response'].strip()
                
                # Clean up the response
                if question_text.startswith('"') and question_text.endswith('"'):
                    question_text = question_text[1:-1]
                
                # Generate a unique ID and trait for this LLM-generated question
                import hashlib
                question_hash = hashlib.md5(question_text.encode()).hexdigest()[:8]
                
                return {
                    "id": int(f"200{question_hash}", 16) % 10000,  # Generate unique ID
                    "text": question_text,
                    "trait": f"ollama_generated_{question_hash}"
                }
        except Exception as e:
            print(f"Ollama error: {e}")
            return None
    
    def _generate_with_huggingface(self, context: str) -> Optional[Dict]:
        """Generate question using Hugging Face API"""
        try:
            headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
            
            response = requests.post(
                "https://api-inference.huggingface.co/models/gpt2",
                headers=headers,
                json={"inputs": context, "max_length": 50}
            )
            
            if response.status_code == 200:
                # This is a simplified example - you'd need to adapt based on the model
                question_text = response.json()[0]['generated_text'].strip()
                return {
                    "id": len(context) + 1,
                    "text": question_text,
                    "trait": f"llm_generated_{len(context)}"
                }
        except Exception as e:
            print(f"Hugging Face error: {e}")
            return None
    
    def analyze_confidence(self, person: Dict, answers: Dict[int, bool]) -> float:
        """Analyze confidence level for a person match using comprehensive analysis"""
        
        if self.current_llm == 'none':
            return 0.5  # Default confidence
        
        # Prepare detailed context for confidence analysis
        question_mapping = {
            1: "Is this person a scientist or researcher?",
            2: "Is this person from history (no longer alive)?",
            3: "Is this person male?",
            4: "Is this person still alive?",
            5: "Is this person American?",
            6: "Does this person have a beard?",
            7: "Is this person a politician?",
            8: "Is this person an artist or creative?",
            9: "Is this person an entrepreneur or business person?",
            10: "Is this person a musician or singer?",
            11: "Is this person from the 20th century?",
            12: "Is this person from the 21st century?",
            13: "Is this person blonde?",
            14: "Is this person associated with Hollywood?",
            15: "Is this person a writer or author?"
        }
        
        # Create detailed analysis of trait matches
        trait_analysis = []
        total_matches = 0
        total_questions = 0
        
        for qid, answer in answers.items():
            question_text = question_mapping.get(qid, f"Question {qid}")
            trait = self._extract_trait_from_question(question_text)
            
            if trait and trait in person['traits']:
                total_questions += 1
                person_answer = person['traits'][trait]
                matches = person_answer == answer
                if matches:
                    total_matches += 1
                
                trait_analysis.append(f"'{question_text}' - Expected: {'Yes' if answer else 'No'}, {person['name']}: {'Yes' if person_answer else 'No'} - {'✓' if matches else '✗'}")
        
        match_percentage = total_matches / total_questions if total_questions > 0 else 0
        
        context = f"""
        CONFIDENCE ANALYSIS FOR: {person['name']}
        
        PERSON DETAILS:
        - Name: {person['name']}
        - Description: {person['description']}
        - All Traits: {person['traits']}
        
        TRAIT MATCH ANALYSIS:
        {chr(10).join(trait_analysis)}
        
        SUMMARY:
        - Total questions answered: {total_questions}
        - Correct matches: {total_matches}
        - Match percentage: {match_percentage:.2%}
        
        TASK: Based on the trait analysis above, rate your confidence (0.0 to 1.0) that {person['name']} is the person the user is thinking of. Consider:
        1. How well the traits match the answers
        2. The distinctiveness of the person's characteristics
        3. Whether there are other people who might also match
        
        Return ONLY a number between 0.0 and 1.0, nothing else.
        """
        
        try:
            if self.current_llm == 'local_ollama':
                return self._analyze_confidence_with_ollama(context)
            elif self.current_llm == 'openai':
                import openai
                openai.api_key = os.getenv('OPENAI_API_KEY')
                
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Use GPT-4 for better analysis
                    messages=[
                        {"role": "system", "content": "You are an expert at analyzing confidence levels in guessing games. Return only a number between 0.0 and 1.0."},
                        {"role": "user", "content": context}
                    ],
                    max_tokens=10,
                    temperature=0.1
                )
                
                confidence_text = response.choices[0].message.content.strip()
                # Clean up the response
                confidence_text = confidence_text.replace('"', '').replace("'", "")
                return float(confidence_text)
            
            # Add other LLM confidence analysis methods here
            
        except Exception as e:
            print(f"Confidence analysis error: {e}")
            return match_percentage  # Fallback to match percentage
    
    def _analyze_confidence_with_ollama(self, context: str) -> float:
        """Analyze confidence using local Ollama"""
        try:
            # Select the best model for confidence analysis
            best_model = self._select_best_ollama_model("confidence_analysis")
            print(f"Using Ollama model for confidence analysis: {best_model}")
            
            # Enhanced prompt for confidence analysis
            enhanced_prompt = f"""You are an expert at analyzing confidence levels in guessing games.

{context}

Return ONLY a number between 0.0 and 1.0, nothing else."""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    "model": best_model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 20
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                confidence_text = response.json()['response'].strip()
                # Clean up the response
                confidence_text = confidence_text.replace('"', '').replace("'", "").replace('\n', '').replace('\r', '')
                
                try:
                    return float(confidence_text)
                except ValueError:
                    print(f"Could not parse confidence value: {confidence_text}")
                    return 0.5  # Default fallback
        except Exception as e:
            print(f"Ollama confidence analysis error: {e}")
            return 0.5  # Default fallback
    
    def get_available_llms_info(self) -> Dict[str, str]:
        """Get information about available LLMs"""
        info = {}
        
        if self.available_llms['local_ollama']:
            if hasattr(self, 'available_ollama_models') and self.available_ollama_models:
                model_names = [model.get('name', '') for model in self.available_ollama_models]
                info['local_ollama'] = f"Ollama (Local) - Models: {', '.join(model_names)}"
            else:
                info['local_ollama'] = "Ollama (Local) - No models detected"
        if self.available_llms['openai']:
            info['openai'] = "OpenAI GPT (Cloud)"
        if self.available_llms['anthropic']:
            info['anthropic'] = "Anthropic Claude (Cloud)"
        if self.available_llms['huggingface']:
            info['huggingface'] = "Hugging Face (Cloud)"
        
        return info

# Example usage
if __name__ == "__main__":
    llm = LLMIntegration()
    print(f"Available LLMs: {llm.get_available_llms_info()}")
    print(f"Selected LLM: {llm.current_llm}") 