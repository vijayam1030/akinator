import React, { useState } from 'react';
import axios from 'axios';
import { Brain, RefreshCw, Check, X, HelpCircle, Minus } from 'lucide-react';
import './App.css';

function App() {
  console.log('App component rendering...');
  
  const [gameState, setGameState] = useState('welcome');
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [gameData, setGameData] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);

  console.log('Current gameState:', gameState);
  console.log('Current loading:', loading);
  console.log('Current error:', error);

  const startNewGame = async () => {
    console.log('Starting new game...');
    setLoading(true);
    setError(null);
    
    try {
      console.log('Making API call to /api/start...');
      const response = await axios.post('/api/start');
      console.log('API response:', response.data);
      
      setCurrentQuestion(response.data.question);
      setGameData({
        game_id: response.data.game_id,
        asked_questions: [],
        answers: {}
      });
      setProgress(0);
      setGameState('playing');
      console.log('Game started successfully');
    } catch (error) {
      console.error('Error starting game:', error);
      setError('Failed to start game: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestion = async (answer) => {
    console.log('Answering question:', answer);
    setLoading(true);
    setError(null);
    
    try {
      console.log('Making API call to /api/answer...');
      const response = await axios.post('/api/answer', {
        question_id: currentQuestion.id,
        answer: answer,
        game_state: gameData
      });
      console.log('API response:', response.data);

      if (response.data.type === 'result') {
        setResult(response.data);
        setGameState('result');
        console.log('Game ended with result');
      } else {
        setCurrentQuestion(response.data.question);
        setGameData(response.data.game_state);
        setProgress(response.data.progress);
        console.log('Question answered, continuing...');
      }
    } catch (error) {
      console.error('Error answering question:', error);
      setError('Failed to answer question: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const resetGame = () => {
    console.log('Resetting game...');
    setGameState('welcome');
    setCurrentQuestion(null);
    setGameData({});
    setResult(null);
    setProgress(0);
    setError(null);
  };

  const WelcomeScreen = () => {
    console.log('Rendering WelcomeScreen');
    return (
      <div className="card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ marginBottom: '30px' }}>
            <Brain size={80} color="#667eea" />
          </div>
          
          <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '20px', color: '#333' }}>
            Akinator Game
          </h1>
          
          <p style={{ fontSize: '20px', color: '#666', marginBottom: '40px', lineHeight: '1.6' }}>
            Think of a famous person, and I'll try to guess who you're thinking of by asking you questions!
          </p>
          
          {error && (
            <div style={{ 
              background: '#ffebee', 
              color: '#c62828', 
              padding: '10px', 
              borderRadius: '8px', 
              marginBottom: '20px' 
            }}>
              Error: {error}
            </div>
          )}
          
          <button
            className="btn btn-primary"
            onClick={startNewGame}
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw size={20} className="spinner" />
                Starting...
              </>
            ) : (
              <>
                <Brain size={20} />
                Start Game
              </>
            )}
          </button>
        </div>
      </div>
    );
  };

  const QuestionScreen = () => {
    console.log('Rendering QuestionScreen, currentQuestion:', currentQuestion);
    return (
      <div className="card" style={{ maxWidth: '700px', margin: '0 auto' }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{ marginBottom: '30px' }}>
            <Brain size={60} color="#667eea" />
          </div>
          
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress}%` }}
            />
          </div>
          
          <p style={{ fontSize: '14px', color: '#666', marginBottom: '20px' }}>
            Progress: {Math.round(progress)}%
          </p>
          
          <h2 className="question-text">
            {currentQuestion?.text || 'Loading question...'}
          </h2>
          
          {error && (
            <div style={{ 
              background: '#ffebee', 
              color: '#c62828', 
              padding: '10px', 
              borderRadius: '8px', 
              marginBottom: '20px' 
            }}>
              Error: {error}
            </div>
          )}
          
          <div style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '40px', flexWrap: 'wrap' }}>
            <button
              className="btn btn-yes"
              onClick={() => answerQuestion(true)}
              disabled={loading}
            >
              <Check size={20} />
              Yes
            </button>
            
            <button
              className="btn btn-no"
              onClick={() => answerQuestion(false)}
              disabled={loading}
            >
              <X size={20} />
              No
            </button>
            
            <button
              className="btn btn-unsure"
              onClick={() => answerQuestion('unsure')}
              disabled={loading}
            >
              <HelpCircle size={20} />
              Not Sure
            </button>
            
            <button
              className="btn btn-dont-know"
              onClick={() => answerQuestion('dont_know')}
              disabled={loading}
            >
              <Minus size={20} />
              Don't Know
            </button>
          </div>
          
          {loading && (
            <div className="loading">
              <div className="spinner" />
            </div>
          )}
        </div>
      </div>
    );
  };

  const ResultScreen = () => {
    console.log('Rendering ResultScreen, result:', result);
    return (
      <div className="card result-card" style={{ maxWidth: '600px', margin: '0 auto' }}>
        {result?.person ? (
          <>
            <img
              src={result.person.image}
              alt={result.person.name}
              className="result-image"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/200x200/667eea/ffffff?text=?';
              }}
            />
            
            <h2 className="result-name">
              {result.person.name}
            </h2>
            
            <p className="result-description">
              {result.person.description}
            </p>
            
            <div className="confidence">
              Confidence: {Math.round(result.confidence * 100)}%
            </div>
            
            <div style={{ marginTop: '30px' }}>
              <p style={{ color: '#666', marginBottom: '20px' }}>
                Questions asked: {result.questions_asked}
              </p>
              
              <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
                <button
                  className="btn btn-primary"
                  onClick={resetGame}
                >
                  <RefreshCw size={20} />
                  Play Again
                </button>
              </div>
            </div>
          </>
        ) : (
          <>
            <div style={{ textAlign: 'center' }}>
              <Brain size={80} color="#667eea" style={{ marginBottom: '20px' }} />
              <h2 style={{ fontSize: '28px', marginBottom: '15px', color: '#333' }}>
                I couldn't guess!
              </h2>
              <p style={{ color: '#666', marginBottom: '30px' }}>
                I couldn't determine who you were thinking of. Maybe try again with a different person?
              </p>
              
              <button
                className="btn btn-primary"
                onClick={resetGame}
              >
                <RefreshCw size={20} />
                Try Again
              </button>
            </div>
          </>
        )}
      </div>
    );
  };

  console.log('About to render main component, gameState:', gameState);
  
  return (
    <div className="container">
      <div style={{ 
        position: 'fixed', 
        top: '10px', 
        right: '10px', 
        background: 'rgba(0,0,0,0.8)', 
        color: 'white', 
        padding: '10px', 
        borderRadius: '5px', 
        fontSize: '12px',
        zIndex: 1000
      }}>
        Debug: {gameState} | Loading: {loading.toString()} | Error: {error ? 'Yes' : 'No'}
      </div>
      
      {gameState === 'welcome' && <WelcomeScreen />}
      {gameState === 'playing' && <QuestionScreen />}
      {gameState === 'result' && <ResultScreen />}
    </div>
  );
}

export default App; 