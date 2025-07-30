import requests
import json
import os
import hashlib
from typing import Dict, List, Optional, Any

class LLMIntegration:
    def __init__(self):
        self.current_llm = 'none'
        self.available_llms = self._detect_available_llms()
        self._select_best_llm()
    
    def _detect_available_llms(self):
        """Detect available LLM services"""
        llms = {}
        
        # Check Ollama (local)
        try:
            response = requests.get('http://localhost:11434/api/tags', timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    llms['local_ollama'] = {
                        'models': [model['name'] for model in models],
                        'type': 'local',
                        'priority': 1
                    }
        except:
            pass
        
        # Check OpenAI
        if os.getenv('OPENAI_API_KEY'):
            llms['openai'] = {
                'models': ['gpt-4', 'gpt-3.5-turbo'],
                'type': 'cloud',
                'priority': 2
            }
        
        # Check Anthropic
        if os.getenv('ANTHROPIC_API_KEY'):
            llms['anthropic'] = {
                'models': ['claude-3-opus-20240229', 'claude-3-sonnet-20240229'],
                'type': 'cloud',
                'priority': 3
            }
        
        return llms
    
    def _select_best_llm(self):
        """Select the best available LLM"""
        if not self.available_llms:
            self.current_llm = 'none'
            return
        
        # Prefer local Ollama if available
        if 'local_ollama' in self.available_llms:
            self.current_llm = 'local_ollama'
        elif 'openai' in self.available_llms:
            self.current_llm = 'openai'
        elif 'anthropic' in self.available_llms:
            self.current_llm = 'anthropic'
        else:
            self.current_llm = 'none'
    
    def get_available_llms_info(self):
        """Get information about available LLMs"""
        return self.available_llms
    
    def generate_smart_question(self, answers: Dict, asked_questions: set) -> Optional[str]:
        """Generate the next smart question using LLM"""
        if self.current_llm == 'none':
            return None
        
        # Prepare context from previous answers
        context = self._prepare_question_context(answers, asked_questions)
        
        if self.current_llm == 'local_ollama':
            return self._generate_question_with_ollama(context)
        elif self.current_llm == 'openai':
            return self._generate_question_with_openai(context)
        elif self.current_llm == 'anthropic':
            return self._generate_question_with_anthropic(context)
        
        return None
    
    def identify_person(self, answers: Dict) -> Optional[Dict]:
        """Identify the person based on answers using LLM"""
        if self.current_llm == 'none':
            return None
        
        # Prepare context from answers
        context = self._prepare_identification_context(answers)
        
        if self.current_llm == 'local_ollama':
            return self._identify_person_with_ollama(context)
        elif self.current_llm == 'openai':
            return self._identify_person_with_openai(context)
        elif self.current_llm == 'anthropic':
            return self._identify_person_with_anthropic(context)
        
        return None
    
    def analyze_confidence_for_guess(self, answers: Dict) -> float:
        """Analyze if we should make a guess based on current answers"""
        if self.current_llm == 'none':
            return 0.5
        
        # Prepare context
        context = self._prepare_confidence_context(answers)
        
        if self.current_llm == 'local_ollama':
            return self._analyze_confidence_with_ollama(context)
        elif self.current_llm == 'openai':
            return self._analyze_confidence_with_openai(context)
        elif self.current_llm == 'anthropic':
            return self._analyze_confidence_with_anthropic(context)
        
        return 0.5
    
    def _prepare_question_context(self, answers: Dict, asked_questions: set) -> str:
        """Prepare context for question generation"""
        if not answers:
            return "No previous answers available. Generate a general question to start narrowing down the person."
        
        # Convert answers to readable format
        answer_texts = []
        for question_id, answer in answers.items():
            if answer is not None:  # Skip unsure/don't know answers
                answer_texts.append(f"Question {question_id}: {answer}")
        
        context = f"""
        Previous answers: {', '.join(answer_texts) if answer_texts else 'None'}
        
        Generate the next most informative yes/no question to narrow down the person.
        The question should be specific and help eliminate many possibilities.
        """
        return context
    
    def _prepare_identification_context(self, answers: Dict) -> str:
        """Prepare context for person identification"""
        if not answers:
            return "No answers available for identification."
        
        # Convert answers to readable format
        answer_texts = []
        for question_id, answer in answers.items():
            if answer is not None:  # Skip unsure/don't know answers
                answer_texts.append(f"Question {question_id}: {answer}")
        
        context = f"""
        Based on these answers: {', '.join(answer_texts)}
        
        Identify the most likely person. Return a JSON object with:
        - name: full name
        - description: brief description
        - image: URL to their image
        - confidence: confidence level (0-1)
        """
        return context
    
    def _prepare_confidence_context(self, answers: Dict) -> str:
        """Prepare context for confidence analysis"""
        if not answers:
            return "No answers available."
        
        answer_texts = []
        for question_id, answer in answers.items():
            if answer is not None:
                answer_texts.append(f"Question {question_id}: {answer}")
        
        context = f"""
        Based on these answers: {', '.join(answer_texts)}
        
        Should we make a guess now? Consider:
        1. How specific the answers are
        2. How many questions we've asked
        3. Whether we have enough information
        
        Return only a number between 0 and 1 representing confidence.
        """
        return context
    
    def _generate_question_with_ollama(self, context: str) -> Optional[str]:
        """Generate question using Ollama"""
        try:
            # Select best model for question generation
            model = self._select_best_ollama_model('question_generation')
            
            prompt = f"""You are playing Akinator. Generate ONE short yes/no question to narrow down the person.

{context}

RULES:
- Question must be short (max 10 words)
- Must be yes/no only
- No explanations or emojis
- Focus on distinctive traits

Return ONLY the question text."""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'num_predict': 50
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result.get('response', '').strip()
                if question and len(question) < 100:  # Sanity check
                    return question
            
        except Exception as e:
            print(f"Error generating question with Ollama: {e}")
        
        return None
    
    def _identify_person_with_ollama(self, context: str) -> Optional[Dict]:
        """Identify person using Ollama"""
        try:
            model = self._select_best_ollama_model('identification')
            
            prompt = f"""You are playing Akinator. Based on the answers, identify the person.

{context}

Return ONLY a valid JSON object with: name, description, image, confidence.
Example: {{"name": "Albert Einstein", "description": "Famous physicist", "image": "https://...", "confidence": 0.9}}"""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.3,
                        'top_p': 0.8,
                        'num_predict': 200
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # Try to parse JSON from response
                try:
                    # Find JSON in response
                    start = response_text.find('{')
                    end = response_text.rfind('}') + 1
                    if start != -1 and end > start:
                        json_str = response_text[start:end]
                        person_data = json.loads(json_str)
                        
                        # Validate required fields
                        if all(key in person_data for key in ['name', 'description', 'confidence']):
                            # Add default image if not provided
                            if 'image' not in person_data:
                                person_data['image'] = f"https://en.wikipedia.org/wiki/{person_data['name'].replace(' ', '_')}"
                            
                            return person_data
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            print(f"Error identifying person with Ollama: {e}")
        
        return None
    
    def _analyze_confidence_with_ollama(self, context: str) -> float:
        """Analyze confidence using Ollama"""
        try:
            model = self._select_best_ollama_model('analysis')
            
            prompt = f"""You are playing Akinator. Analyze if we should make a guess.

{context}

Return ONLY a number between 0 and 1 representing confidence."""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.2,
                        'top_p': 0.8,
                        'num_predict': 20
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                # Extract number from response
                try:
                    import re
                    numbers = re.findall(r'0\.\d+|\d+\.\d+|\d+', response_text)
                    if numbers:
                        confidence = float(numbers[0])
                        return max(0.0, min(1.0, confidence))  # Clamp between 0 and 1
                except:
                    pass
            
        except Exception as e:
            print(f"Error analyzing confidence with Ollama: {e}")
        
        return 0.5
    
    def _select_best_ollama_model(self, task: str) -> str:
        """Select the best Ollama model for a specific task"""
        if 'local_ollama' not in self.available_llms:
            return 'llama2'
        
        models = self.available_llms['local_ollama']['models']
        
        # Prefer more capable models for complex tasks
        if task in ['identification', 'analysis']:
            preferred_models = ['llama2:70b', 'llama2:13b', 'mistral:7b', 'codellama:13b', 'llama2']
        else:
            preferred_models = ['mistral:7b', 'llama2:13b', 'llama2:70b', 'codellama:13b', 'llama2']
        
        for preferred in preferred_models:
            if preferred in models:
                return preferred
        
        # Fallback to first available model
        return models[0] if models else 'llama2'
    
    def _generate_question_with_openai(self, context: str) -> Optional[str]:
        """Generate question using OpenAI"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are playing Akinator. Generate ONE short yes/no question to narrow down the person. Return ONLY the question text.'
                        },
                        {
                            'role': 'user',
                            'content': context
                        }
                    ],
                    'max_tokens': 50,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result['choices'][0]['message']['content'].strip()
                if question and len(question) < 100:
                    return question
            
        except Exception as e:
            print(f"Error generating question with OpenAI: {e}")
        
        return None
    
    def _identify_person_with_openai(self, context: str) -> Optional[Dict]:
        """Identify person using OpenAI"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are playing Akinator. Identify the person based on the answers. Return ONLY a valid JSON object with: name, description, image, confidence.'
                        },
                        {
                            'role': 'user',
                            'content': context
                        }
                    ],
                    'max_tokens': 200,
                    'temperature': 0.3
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content'].strip()
                
                try:
                    person_data = json.loads(response_text)
                    if all(key in person_data for key in ['name', 'description', 'confidence']):
                        if 'image' not in person_data:
                            person_data['image'] = f"https://en.wikipedia.org/wiki/{person_data['name'].replace(' ', '_')}"
                        return person_data
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            print(f"Error identifying person with OpenAI: {e}")
        
        return None
    
    def _analyze_confidence_with_openai(self, context: str) -> float:
        """Analyze confidence using OpenAI"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are playing Akinator. Analyze if we should make a guess. Return ONLY a number between 0 and 1 representing confidence.'
                        },
                        {
                            'role': 'user',
                            'content': context
                        }
                    ],
                    'max_tokens': 20,
                    'temperature': 0.2
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['choices'][0]['message']['content'].strip()
                
                try:
                    import re
                    numbers = re.findall(r'0\.\d+|\d+\.\d+|\d+', response_text)
                    if numbers:
                        confidence = float(numbers[0])
                        return max(0.0, min(1.0, confidence))
                except:
                    pass
            
        except Exception as e:
            print(f"Error analyzing confidence with OpenAI: {e}")
        
        return 0.5
    
    def _generate_question_with_anthropic(self, context: str) -> Optional[str]:
        """Generate question using Anthropic"""
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': os.getenv('ANTHROPIC_API_KEY'),
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 50,
                    'messages': [
                        {
                            'role': 'user',
                            'content': f'You are playing Akinator. Generate ONE short yes/no question to narrow down the person.\n\n{context}\n\nReturn ONLY the question text.'
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result['content'][0]['text'].strip()
                if question and len(question) < 100:
                    return question
            
        except Exception as e:
            print(f"Error generating question with Anthropic: {e}")
        
        return None
    
    def _identify_person_with_anthropic(self, context: str) -> Optional[Dict]:
        """Identify person using Anthropic"""
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': os.getenv('ANTHROPIC_API_KEY'),
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 200,
                    'messages': [
                        {
                            'role': 'user',
                            'content': f'You are playing Akinator. Identify the person based on the answers.\n\n{context}\n\nReturn ONLY a valid JSON object with: name, description, image, confidence.'
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['content'][0]['text'].strip()
                
                try:
                    person_data = json.loads(response_text)
                    if all(key in person_data for key in ['name', 'description', 'confidence']):
                        if 'image' not in person_data:
                            person_data['image'] = f"https://en.wikipedia.org/wiki/{person_data['name'].replace(' ', '_')}"
                        return person_data
                except json.JSONDecodeError:
                    pass
            
        except Exception as e:
            print(f"Error identifying person with Anthropic: {e}")
        
        return None
    
    def _analyze_confidence_with_anthropic(self, context: str) -> float:
        """Analyze confidence using Anthropic"""
        try:
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={
                    'x-api-key': os.getenv('ANTHROPIC_API_KEY'),
                    'Content-Type': 'application/json',
                    'anthropic-version': '2023-06-01'
                },
                json={
                    'model': 'claude-3-sonnet-20240229',
                    'max_tokens': 20,
                    'messages': [
                        {
                            'role': 'user',
                            'content': f'You are playing Akinator. Analyze if we should make a guess.\n\n{context}\n\nReturn ONLY a number between 0 and 1 representing confidence.'
                        }
                    ]
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result['content'][0]['text'].strip()
                
                try:
                    import re
                    numbers = re.findall(r'0\.\d+|\d+\.\d+|\d+', response_text)
                    if numbers:
                        confidence = float(numbers[0])
                        return max(0.0, min(1.0, confidence))
                except:
                    pass
            
        except Exception as e:
            print(f"Error analyzing confidence with Anthropic: {e}")
        
        return 0.5
    
    # Keep existing methods for backward compatibility
    def _prepare_context(self, people: List[Dict], question_answers: List[str], remaining_people: List[Dict]) -> str:
        """Prepare context for LLM question generation (legacy method)"""
        # Simplified context for backward compatibility
        context = f"""
        Akinator game. Ask ONE short yes/no question.

        PREVIOUS QUESTIONS:
        {chr(10).join(question_answers) if question_answers else 'No questions asked yet.'}

        RULES:
        - Max 10 words
        - Yes/no only
        - No explanations

        Return ONLY the question text.
        """
        return context
    
    def _generate_with_ollama(self, context: str) -> Optional[str]:
        """Generate with Ollama (legacy method)"""
        try:
            model = self._select_best_ollama_model('question_generation')
            
            enhanced_prompt = f"""Akinator game. Ask ONE short yes/no question.

{context}

RULES:
- Max 10 words
- Yes/no only
- No explanations

Return ONLY the question text."""
            
            response = requests.post(
                'http://localhost:11434/api/generate',
                json={
                    'model': model,
                    'prompt': enhanced_prompt,
                    'stream': False,
                    'options': {
                        'temperature': 0.7,
                        'top_p': 0.9,
                        'num_predict': 50
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result.get('response', '').strip()
                if question and len(question) < 100:
                    return question
            
        except Exception as e:
            print(f"Error generating with Ollama: {e}")
        
        return None
    
    def _generate_with_openai(self, context: str) -> Optional[str]:
        """Generate with OpenAI (legacy method)"""
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {os.getenv("OPENAI_API_KEY")}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'gpt-4',
                    'messages': [
                        {
                            'role': 'system',
                            'content': 'You are playing Akinator. Generate ONE short yes/no question to narrow down the person. Return ONLY the question text.'
                        },
                        {
                            'role': 'user',
                            'content': context
                        }
                    ],
                    'max_tokens': 50,
                    'temperature': 0.7
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                question = result['choices'][0]['message']['content'].strip()
                if question and len(question) < 100:
                    return question
            
        except Exception as e:
            print(f"Error generating with OpenAI: {e}")
        
        return None
    
    def generate_smart_question(self, people: List[Dict], question_answers: List[str], remaining_people: List[Dict]) -> Optional[str]:
        """Generate smart question (legacy method)"""
        if self.current_llm == 'none':
            return None
        
        context = self._prepare_context(people, question_answers, remaining_people)
        
        if self.current_llm == 'local_ollama':
            return self._generate_with_ollama(context)
        elif self.current_llm == 'openai':
            return self._generate_with_openai(context)
        
        return None
    
    def analyze_confidence(self, person: Dict, answers: Dict) -> float:
        """Analyze confidence (legacy method)"""
        if self.current_llm == 'none':
            return 0.8
        
        # Simplified confidence analysis
        if len(answers) >= 5:
            return 0.9
        elif len(answers) >= 3:
            return 0.7
        else:
            return 0.5 