# Akinator Game

A modern, interactive Akinator-like game built with React and Flask. Think of a famous person, and the AI will try to guess who you're thinking of by asking you questions!

## Features

- 🎮 **Interactive Gameplay**: Answer yes/no questions to help the AI guess your person
- 🎨 **Beautiful UI**: Modern, responsive design with smooth animations
- 📊 **Progress Tracking**: Visual progress bar showing game advancement
- 🖼️ **Person Database**: Includes famous people with images and descriptions
- 📱 **Mobile Responsive**: Works perfectly on desktop and mobile devices
- ⚡ **Fast Performance**: Optimized for smooth user experience
- 🤖 **Local LLM Integration**: Uses Ollama for intelligent question generation
- 🧠 **Smart AI**: Automatically selects the best local model for each task
- 🔒 **Privacy-First**: Runs completely locally - no cloud APIs required

## Technology Stack

### Backend
- **Python Flask**: RESTful API server
- **JSON Database**: Simple file-based storage for people and questions
- **CORS Support**: Cross-origin requests enabled
- **Local LLM Integration**: Ollama integration for intelligent question generation
- **Dynamic Model Selection**: Automatically chooses the best available local model

### Frontend
- **React 18**: Modern React with hooks
- **Framer Motion**: Smooth animations and transitions
- **Lucide React**: Beautiful icons
- **Axios**: HTTP client for API calls
- **CSS3**: Modern styling with gradients and animations

## Installation & Setup

### Prerequisites
- Node.js (v14 or higher)
- Python 3.7 or higher
- pip (Python package manager)
- **Ollama** (for local LLM support) - See [OLLAMA_SETUP.md](OLLAMA_SETUP.md) for installation guide

### Backend Setup

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Flask server**:
   ```bash
   python app.py
   ```
   
   The backend will start on `http://localhost:5000`

### Frontend Setup

1. **Install Node.js dependencies**:
   ```bash
   npm install
   ```

2. **Start the React development server**:
   ```bash
   npm start
   ```
   
   The frontend will start on `http://localhost:3000`

## How to Play

1. **Start the Game**: Click "Start Game" on the welcome screen
2. **Answer Questions**: Respond with "Yes" or "No" to each question
3. **Watch Progress**: The progress bar shows how close the AI is to guessing
4. **See Results**: The AI will show its best guess with confidence level
5. **Play Again**: Click "Play Again" to start a new game

## Database

The game includes a database of famous people with their traits:

### Sample People
- **Albert Einstein**: Physicist, historical figure, male, has beard
- **Marie Curie**: Scientist, historical figure, female, Nobel Prize winner
- **Leonardo da Vinci**: Artist, inventor, Renaissance figure
- **William Shakespeare**: Playwright, writer, historical figure
- **Marilyn Monroe**: Actress, Hollywood star, blonde
- **Elon Musk**: Entrepreneur, tech leader, current figure
- **Taylor Swift**: Singer, musician, current pop star
- **Barack Obama**: Politician, former president, current figure

### Questions
The AI asks strategic questions to narrow down the person:
- Is this person a scientist?
- Is this person from history?
- Is this person male?
- Is this person still alive?
- Is this person American?
- Does this person have a beard?
- And many more...

## API Endpoints

- `POST /api/start`: Start a new game
- `POST /api/answer`: Submit an answer and get next question/result
- `GET /api/people`: Get all people in database
- `GET /api/questions`: Get all available questions

## Customization

### Adding New People

Edit the `initialize_database()` function in `app.py` to add new people:

```python
{
    "id": 9,
    "name": "Your Person Name",
    "image": "https://example.com/image.jpg",
    "description": "Brief description of the person",
    "traits": {
        "is_scientist": False,
        "is_historical": False,
        "is_male": True,
        # ... add more traits
    }
}
```

### Adding New Questions

Add new questions to the database:

```python
{"id": 16, "text": "Is this person a sports athlete?", "trait": "is_athlete"}
```

## Development

### Project Structure
```
akinator/
├── app.py                 # Flask backend
├── requirements.txt       # Python dependencies
├── package.json          # Node.js dependencies
├── public/              # Static files
├── src/                 # React source code
│   ├── App.js          # Main React component
│   ├── App.css         # Component styles
│   ├── index.js        # React entry point
│   └── index.css       # Global styles
└── README.md           # This file
```

### Running in Development Mode

1. **Terminal 1** (Backend):
   ```bash
   python app.py
   ```

2. **Terminal 2** (Frontend):
   ```bash
   npm start
   ```

3. Open `http://localhost:3000` in your browser

## Future Enhancements

- [ ] **LLM Integration**: Connect to local or cloud LLMs for smarter question generation
- [ ] **User Accounts**: Save game history and statistics
- [ ] **More Categories**: Add animals, objects, fictional characters
- [ ] **Difficulty Levels**: Easy, medium, hard modes
- [ ] **Multiplayer**: Challenge friends to guess the same person
- [ ] **Voice Interface**: Speech recognition for hands-free play

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Credits

- Icons: [Lucide React](https://lucide.dev/)
- Animations: [Framer Motion](https://www.framer.com/motion/)
- Images: Wikimedia Commons (public domain)
- Font: Inter (Google Fonts) 