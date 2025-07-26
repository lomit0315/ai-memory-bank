# 🦙 Complete Ollama Setup Guide for AI Memory Bank

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Installing Ollama](#installing-ollama)  
3. [Installing Models](#installing-models)
4. [Using with AI Memory Bank](#using-with-ai-memory-bank)
5. [Advanced Configuration](#advanced-configuration)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)

---

## 🚀 Quick Start

### Step 1: Install Ollama
```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh

# Windows
# Download from https://ollama.com/download/windows
```

### Step 2: Start Ollama Service
```bash
ollama serve
```

### Step 3: Install a Model
```bash
# Install a fast, lightweight model
ollama pull llama2

# Or install a more powerful model
ollama pull codellama
```

### Step 4: Start Your AI Memory Bank
```bash
cd /path/to/your/ai-memory-bank
python start_frontend.py
```

### Step 5: Configure in Web Interface
1. Open http://localhost:8000
2. Go to **"AI Model Configuration"** section
3. Click **"Local Models"** tab
4. Select your installed model from dropdown
5. Ask questions in the **"AI Question Answering"** section!

---

## 🔧 Installing Ollama

### macOS
```bash
# Method 1: Using curl (recommended)
curl -fsSL https://ollama.com/install.sh | sh

# Method 2: Using Homebrew
brew install ollama
```

### Linux
```bash
# Ubuntu/Debian
curl -fsSL https://ollama.com/install.sh | sh

# Manual installation
curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/local/bin/ollama
chmod +x /usr/local/bin/ollama
```

### Windows
1. Download from https://ollama.com/download/windows
2. Run the installer
3. Ollama will start automatically

### Verify Installation
```bash
ollama --version
# Should show: ollama version 0.x.x
```

---

## 🤖 Installing Models

### Recommended Models for Different Use Cases

#### 🏃‍♂️ Fast & Lightweight (Good for laptops)
```bash
# Llama 2 7B - Great balance of speed and quality
ollama pull llama2

# Orca Mini - Very fast, good for quick tasks
ollama pull orca-mini

# Phi-2 - Microsoft's compact model
ollama pull phi
```

#### 🧠 High Quality (Requires more RAM)
```bash
# Llama 2 13B - Better quality, needs 16GB+ RAM
ollama pull llama2:13b

# Code Llama - Excellent for programming tasks
ollama pull codellama

# Mistral - High quality general purpose
ollama pull mistral
```

#### 🌏 Chinese Language Support
```bash
# Qwen - Alibaba's Chinese model
ollama pull qwen

# Chinese Llama 2
ollama pull llama2-chinese
```

### Check Available Models
```bash
# See all available models online
ollama list

# See models you've installed
ollama ps
```

### Model Management
```bash
# Remove a model
ollama rm llama2

# Update a model
ollama pull llama2

# Show model information
ollama show llama2
```

---

## 🎯 Using with AI Memory Bank

### 1. Start Ollama Service
```bash
# In terminal 1 - Keep this running
ollama serve
```

### 2. Start AI Memory Bank
```bash
# In terminal 2
cd /path/to/your/ai-memory-bank
python start_frontend.py
```

### 3. Web Interface Configuration

#### Configure Local Models
1. Open http://localhost:8000
2. Navigate to **"AI Model Configuration"**
3. Click **"Local Models"** tab
4. **Model Selection**: Choose from installed models
5. **Temperature**: Adjust creativity (0.1 = focused, 0.9 = creative)
6. **Max Tokens**: Set response length (1024-4096)

#### Status Indicators
- **🟢 Green dot**: Ollama is connected and working
- **🔴 Red dot**: Ollama is not running or not accessible

### 4. Asking Questions

#### Basic Usage
1. Go to **"AI Question Answering"** section
2. Type your question in the large text area
3. Make sure **"Enable AI Enhancement"** is checked
4. Make sure **"Use Local Model"** is checked
5. Click **"Ask AI"**

#### Example Questions
```
What are the main concepts in my machine learning documents?

Summarize the key findings from my research papers about neural networks.

How can I improve my Python coding skills based on these tutorials?

What programming patterns do my code examples demonstrate?
```

---

## ⚙️ Advanced Configuration

### Custom Ollama Configuration

#### Change Ollama Host/Port
```bash
# Set environment variables
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*

# Then start Ollama
ollama serve
```

#### Modify AI Memory Bank Config
Edit `config.py`:
```python
# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"  # Change if needed
OLLAMA_MODEL = "llama2"  # Your preferred default model
OLLAMA_TIMEOUT = 60
OLLAMA_MAX_TOKENS = 2048
OLLAMA_TEMPERATURE = 0.7

# Add your installed models
AVAILABLE_OLLAMA_MODELS = [
    "llama2",
    "llama2:13b", 
    "codellama",
    "mistral",
    "qwen",
    # Add your models here
]
```

### Performance Optimization

#### For Better Performance
```bash
# Increase model context (if you have enough RAM)
ollama run llama2 --context-length 4096

# Use GPU acceleration (if available)
# Ollama automatically detects and uses GPU
```

#### Memory Management
- **8GB RAM**: Use `llama2`, `orca-mini`, `phi`
- **16GB RAM**: Use `llama2:13b`, `codellama`
- **32GB+ RAM**: Use `llama2:70b` or larger models

---

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 1. "Ollama not available" Error
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it
ollama serve

# Check the process
ps aux | grep ollama
```

#### 2. Model Not Found
```bash
# List installed models
ollama list

# Install the model if missing
ollama pull llama2
```

#### 3. Slow Responses
- **Solution**: Use a smaller model like `orca-mini`
- **Check**: Ensure enough RAM is available
- **Close**: Other heavy applications

#### 4. Connection Refused
```bash
# Check if port 11434 is in use
lsof -i :11434

# Kill conflicting processes
sudo kill -9 <PID>

# Restart Ollama
ollama serve
```

#### 5. Out of Memory
- **Use smaller model**: Switch from `llama2:13b` to `llama2`
- **Reduce context**: Lower max tokens in AI Memory Bank
- **Close applications**: Free up RAM

### Debug Mode
```bash
# Run with debug output
OLLAMA_DEBUG=1 ollama serve

# Check logs
tail -f ~/.ollama/logs/server.log
```

---

## 📊 Best Practices

### Model Selection Guide

#### For Research & Academic Work
- **Best**: `llama2:13b` or `mistral`
- **Backup**: `llama2`
- **Why**: Better reasoning and accuracy

#### For Code Analysis
- **Best**: `codellama`
- **Backup**: `llama2`
- **Why**: Trained specifically on code

#### For Quick Questions
- **Best**: `orca-mini` or `phi`
- **Why**: Fast responses, good for simple queries

#### For Chinese Content
- **Best**: `qwen`
- **Backup**: `llama2-chinese`
- **Why**: Native Chinese language support

### Performance Tips

#### Optimize Your Questions
✅ **Good**: "What are the main themes in my machine learning papers?"
❌ **Bad**: "Tell me everything about AI"

✅ **Good**: "Summarize the key functions in my Python scripts"
❌ **Bad**: "What's in these files?"

#### Temperature Settings
- **0.1-0.3**: Factual, focused answers
- **0.4-0.7**: Balanced creativity and accuracy
- **0.8-1.0**: Creative, varied responses

#### Token Management
- **Short answers**: 512-1024 tokens
- **Detailed analysis**: 1024-2048 tokens
- **Comprehensive summaries**: 2048-4096 tokens

### Security & Privacy

#### Local Processing Benefits
- ✅ **Complete Privacy**: Data never leaves your machine
- ✅ **No Internet Required**: Works offline
- ✅ **No API Costs**: Free to use
- ✅ **Full Control**: Choose your own models

#### Data Protection
- Documents are processed locally
- No data sent to external servers
- Full control over your information

---

## 🎯 Real-World Examples

### Example 1: Research Paper Analysis
```
Setup:
1. Upload your research papers (PDF)
2. Use model: llama2:13b
3. Temperature: 0.3 (for accuracy)

Question: "What are the main methodologies discussed in my machine learning research papers?"

Expected Output: Detailed analysis of research methods with source citations
```

### Example 2: Code Review
```
Setup:
1. Upload your Python/JS files
2. Use model: codellama
3. Temperature: 0.2 (for precision)

Question: "What design patterns are used in my code and how can I improve them?"

Expected Output: Code analysis with improvement suggestions
```

### Example 3: Document Summarization
```
Setup:
1. Upload multiple documents
2. Use model: mistral
3. Temperature: 0.5 (balanced)

Question: "Create a comprehensive summary of all my project documentation"

Expected Output: Well-structured summary with key points
```

---

## 🆘 Getting Help

### Resources
- **Ollama Documentation**: https://ollama.com/docs
- **Model Library**: https://ollama.com/library
- **GitHub Issues**: https://github.com/ollama/ollama/issues

### Community
- **Discord**: https://discord.gg/ollama
- **Reddit**: r/ollama
- **Stack Overflow**: Tag `ollama`

### AI Memory Bank Support
If you have issues specific to AI Memory Bank + Ollama integration:
1. Check the status indicator in the web interface
2. Look at browser console for errors (F12)
3. Check terminal output for error messages
4. Ensure both services are running

---

## 🎉 Success!

Once everything is working, you should see:
- ✅ Green status dot in "Local Models" tab
- ✅ Available models in the dropdown
- ✅ Fast, intelligent responses to your questions
- ✅ Proper source citations from your documents

**Congratulations! You now have a powerful, private AI assistant running entirely on your local machine!** 🚀

---

*Last updated: December 2024* 