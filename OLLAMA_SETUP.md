# Ollama Setup Guide for Akinator Game

## 🚀 **Local LLM Integration with Ollama**

This guide will help you set up Ollama to run local LLMs for the Akinator game, making it completely self-contained without requiring cloud APIs.

## 📋 **Prerequisites**

- Windows 10/11 (or macOS/Linux)
- At least 8GB RAM (16GB recommended)
- 10GB free disk space
- Internet connection for initial model downloads

## 🔧 **Installation Steps**

### 1. **Install Ollama**

**Windows:**
```bash
# Download from https://ollama.ai/download
# Or use winget:
winget install Ollama.Ollama
```

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. **Start Ollama Service**

```bash
# Start Ollama (it will run as a service)
ollama serve
```

### 3. **Download Recommended Models**

The Akinator game works best with these models. Download them based on your hardware:

**For 8GB RAM (Basic):**
```bash
ollama pull llama2:7b
ollama pull mistral:7b
```

**For 16GB+ RAM (Recommended):**
```bash
ollama pull llama2:13b
ollama pull codellama:7b
ollama pull mistral:7b
ollama pull llama2:7b
```

**For 32GB+ RAM (Best Performance):**
```bash
ollama pull llama2:70b
ollama pull codellama:13b
ollama pull mistral:7b
ollama pull llama2:13b
```

### 4. **Verify Installation**

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return something like:
# {
#   "models": [
#     {"name": "llama2:7b", "size": 3823, "modified_at": "2024-01-01T00:00:00Z"},
#     {"name": "mistral:7b", "size": 4107, "modified_at": "2024-01-01T00:00:00Z"}
#   ]
# }
```

## 🎮 **Using the Enhanced Akinator Game**

### **Features with Local LLMs:**

1. **Smart Question Generation**: The game will automatically select the best available model for generating strategic questions
2. **Confidence Analysis**: Uses local LLMs to analyze how confident the AI is in its guesses
3. **Dynamic Model Selection**: Automatically chooses the best model for each task:
   - **Question Generation**: Prefers `llama2`, `codellama`, `mistral`
   - **Confidence Analysis**: Prefers `llama2`, `mistral`, `codellama`

### **Model Preferences:**

The system will automatically select models in this order:

**Question Generation:**
1. `llama2` (best reasoning)
2. `codellama` (good for structured thinking)
3. `mistral` (fast and accurate)
4. `llama2:13b` (higher quality)
5. `llama2:7b` (faster)

**Confidence Analysis:**
1. `llama2` (best analysis)
2. `mistral` (fast analysis)
3. `codellama` (good reasoning)
4. `llama2:13b` (highest quality)

## 🔍 **Testing Your Setup**

### 1. **Check LLM Status**
```bash
curl http://localhost:5000/api/llm-status
```

Should show:
```json
{
  "available_llms": {
    "local_ollama": "Ollama (Local) - Models: llama2:7b, mistral:7b"
  },
  "current_llm": "local_ollama"
}
```

### 2. **Test Question Generation**
```bash
curl -X POST http://localhost:5000/api/start -H "Content-Type: application/json" -d "{}"
```

You should see LLM-generated questions instead of random ones!

### 3. **Monitor Model Usage**
Check the Flask server logs to see which models are being used:
```
Using Ollama model: llama2:7b
LLM generated question: Is this person associated with technology or innovation?
```

## 🛠️ **Troubleshooting**

### **Ollama Not Starting:**
```bash
# Check if Ollama is installed
ollama --version

# Start Ollama manually
ollama serve

# Check if port 11434 is open
netstat -an | findstr :11434
```

### **Models Not Downloading:**
```bash
# Check available models
ollama list

# Pull a specific model
ollama pull llama2:7b

# Check download progress
ollama ps
```

### **Memory Issues:**
- Close other applications
- Use smaller models (7b instead of 13b/70b)
- Increase virtual memory on Windows

### **Performance Optimization:**
```bash
# Set environment variables for better performance
set OLLAMA_HOST=0.0.0.0
set OLLAMA_ORIGINS=*

# Or on Linux/macOS:
export OLLAMA_HOST=0.0.0.0
export OLLAMA_ORIGINS=*
```

## 🎯 **Advanced Configuration**

### **Custom Model Selection:**
You can modify `llm_integration.py` to change model preferences:

```python
model_preferences = {
    "question_generation": ["your-preferred-model", "llama2", "mistral"],
    "confidence_analysis": ["your-preferred-model", "llama2", "mistral"],
    "general": ["your-preferred-model", "llama2", "mistral"]
}
```

### **Model Performance Comparison:**

| Model | Speed | Quality | Memory | Best For |
|-------|-------|---------|--------|----------|
| `llama2:7b` | Fast | Good | 4GB | General use |
| `llama2:13b` | Medium | Better | 8GB | Better reasoning |
| `mistral:7b` | Fast | Good | 4GB | Quick responses |
| `codellama:7b` | Fast | Good | 4GB | Structured thinking |
| `llama2:70b` | Slow | Best | 32GB | Highest quality |

## 🚀 **Start the Game**

Once Ollama is set up:

1. **Start Ollama:**
   ```bash
   ollama serve
   ```

2. **Start the Akinator Game:**
   ```bash
   python app.py
   ```

3. **Open in Browser:**
   ```
   http://localhost:3000
   ```

4. **Enjoy Local LLM-Powered Gaming!** 🎮

The game will now use your local LLMs for intelligent question generation and confidence analysis, making it completely self-contained and private! 