import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Users, Trophy, RefreshCw, Check, X } from 'lucide-react';
import './App.css';

function App() {
  const [gameState, setGameState] = useState('welcome'); // welcome, playing, result
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [gameData, setGameData] = useState({});
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [progress, setProgress] = useState(0);

  const startNewGame = async () => {
    setLoading(true);
    try {
      const response = await axios.post('/api/start');
      setCurrentQuestion(response.data.question);
      setGameData({
        game_id: response.data.game_id,
        asked_questions: [],
        answers: {}
      });
      setProgress(0);
      setGameState('playing');
    } catch (error) {
      console.error('Error starting game:', error);
    } finally {
      setLoading(false);
    }
  };

  const answerQuestion = async (answer) => {
    setLoading(true);
    try {
      const response = await axios.post('/api/answer', {
        question_id: currentQuestion.id,
        answer: answer,
        game_state: gameData
      });

      if (response.data.type === 'result') {
        setResult(response.data);
        setGameState('result');
      } else {
        setCurrentQuestion(response.data.question);
        setGameData(response.data.game_state);
        setProgress(response.data.progress);
      }
    } catch (error) {
      console.error('Error answering question:', error);
    } finally {
      setLoading(false);
    }
  };

  const resetGame = () => {
    setGameState('welcome');
    setCurrentQuestion(null);
    setGameData({});
    setResult(null);
    setProgress(0);
  };

  const WelcomeScreen = () => (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card"
      style={{ maxWidth: '600px', margin: '0 auto' }}
    >
      <div style={{ textAlign: 'center' }}>
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.2 }}
          style={{ marginBottom: '30px' }}
        >
          <Brain size={80} color="#667eea" />
        </motion.div>
        
        <h1 style={{ fontSize: '48px', fontWeight: '700', marginBottom: '20px', color: '#333' }}>
          Akinator Game
        </h1>
        
        <p style={{ fontSize: '20px', color: '#666', marginBottom: '40px', lineHeight: '1.6' }}>
          Think of a famous person, and I'll try to guess who you're thinking of by asking you questions!
        </p>
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
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
        </motion.button>
      </div>
    </motion.div>
  );

  const QuestionScreen = () => (
    <motion.div
      initial={{ opacity: 0, x: 50 }}
      animate={{ opacity: 1, x: 0 }}
      className="card"
      style={{ maxWidth: '700px', margin: '0 auto' }}
    >
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
          {currentQuestion?.text}
        </h2>
        
        <div style={{ display: 'flex', gap: '20px', justifyContent: 'center', marginTop: '40px' }}>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn btn-yes"
            onClick={() => answerQuestion(true)}
            disabled={loading}
          >
            <Check size={20} />
            Yes
          </motion.button>
          
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="btn btn-no"
            onClick={() => answerQuestion(false)}
            disabled={loading}
          >
            <X size={20} />
            No
          </motion.button>
        </div>
        
        {loading && (
          <div className="loading">
            <div className="spinner" />
          </div>
        )}
      </div>
    </motion.div>
  );

  const ResultScreen = () => (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      className="card result-card"
      style={{ maxWidth: '600px', margin: '0 auto' }}
    >
      {result?.person ? (
        <>
          <motion.img
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.3 }}
            src={result.person.image}
            alt={result.person.name}
            className="result-image"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/200x200/667eea/ffffff?text=?';
            }}
          />
          
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="result-name"
          >
            {result.person.name}
          </motion.h2>
          
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="result-description"
          >
            {result.person.description}
          </motion.p>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="confidence"
          >
            Confidence: {Math.round(result.confidence * 100)}%
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            style={{ marginTop: '30px' }}
          >
            <p style={{ color: '#666', marginBottom: '20px' }}>
              Questions asked: {result.questions_asked}
            </p>
            
            <div style={{ display: 'flex', gap: '15px', justifyContent: 'center' }}>
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="btn btn-primary"
                onClick={resetGame}
              >
                <RefreshCw size={20} />
                Play Again
              </motion.button>
            </div>
          </motion.div>
        </>
      ) : (
        <>
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            style={{ textAlign: 'center' }}
          >
            <Brain size={80} color="#667eea" style={{ marginBottom: '20px' }} />
            <h2 style={{ fontSize: '28px', marginBottom: '15px', color: '#333' }}>
              I couldn't guess!
            </h2>
            <p style={{ color: '#666', marginBottom: '30px' }}>
              I couldn't determine who you were thinking of. Maybe try again with a different person?
            </p>
            
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="btn btn-primary"
              onClick={resetGame}
            >
              <RefreshCw size={20} />
              Try Again
            </motion.button>
          </motion.div>
        </>
      )}
    </motion.div>
  );

  return (
    <div className="container">
      <AnimatePresence mode="wait">
        {gameState === 'welcome' && <WelcomeScreen key="welcome" />}
        {gameState === 'playing' && <QuestionScreen key="playing" />}
        {gameState === 'result' && <ResultScreen key="result" />}
      </AnimatePresence>
    </div>
  );
}

export default App; 