# 🤗 HuggingFace Inference Chat

A Streamlit-based chat interface powered by HuggingFace models with advanced features.

## 📸 Screenshots & Demo

![HuggingFace Inference Chat](assets/demo/screenshot.png)

### Features Showcase:

1. **Interactive Chat Interface**

   - Real-time streaming responses
   - Code syntax highlighting
   - File upload support
   - Token usage tracking

2. **Model Settings**

   - Adjustable temperature
   - Top-p sampling
   - Response length control
   - Repetition penalty

3. **Advanced Features**
   - Redis-based caching
   - Conversation memory
   - File analysis
   - Modern UI

## Features

- 🤗 Advanced language models from HuggingFace
- 🔄 Real-time streaming responses
- 💻 Code syntax highlighting and formatting
- 📁 File upload and analysis
- 💬 Persistent conversation history
- 📦 Redis-based caching with fallback
- 🎨 Modern, responsive UI
- 📊 Token usage tracking

## Installation Guide

### Prerequisites

- Python 3.10 or higher
- Redis server (optional, falls back to in-memory cache)
- HuggingFace API token ([Get one here](https://huggingface.co/settings/tokens))

### Windows

```bash
# Clone repository
git clone https://github.com/borderlessboy/huggingface-inference-chat.git
cd huggingface-inference-chat

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
copy .env.example .env
# Edit .env with your HuggingFace API token
```

### macOS/Linux

```bash
# Clone repository
git clone https://github.com/borderlessboy/huggingface-inference-chat.git
cd huggingface-inference-chat

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your HuggingFace API token

# Optional: Install Redis (macOS with Homebrew)
brew install redis
brew services start redis

# Optional: Install Redis (Ubuntu/Debian)
sudo apt update
sudo apt install redis-server
sudo systemctl start redis
```

### Docker Installation

```bash
# Build the image
docker build -t huggingface-chat .

# Run the container
docker run -p 8501:8501 --env-file .env huggingface-chat
```

## API Documentation

### HuggingFace API Client

The `HuggingFaceAPI` class provides the main interface for interacting with HuggingFace's inference API:

```python
from api.huggingface import HuggingFaceAPI

# Initialize client
hf_api = HuggingFaceAPI(model_name="Qwen/Qwen2.5-Coder-32B-Instruct", api_token="your_token")

# Generate response (streaming)
for chunk in hf_api.generate_stream("Your prompt here"):
    print(chunk, end="")

# Generate response (non-streaming)
response = hf_api.generate("Your prompt here")
```

### Key Parameters

- `temperature` (0.0-1.0): Controls randomness in responses
- `top_p` (0.0-1.0): Controls diversity via nucleus sampling
- `max_tokens` (int): Maximum length of generated response
- `repetition_penalty` (1.0-2.0): Prevents repetitive text

### Caching System

The application supports two caching backends:

1. Redis (recommended for production)
2. In-memory cache (fallback option)

```python
# Redis configuration
REDIS_CONFIG = {
    "host": "localhost",
    "port": 6379,
    "db": 0,
}
```

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch:

```bash
git checkout -b feature/your-feature-name
```

3. Make your changes and commit:

```bash
git commit -m "Add your feature description"
```

4. Push to your fork:

```bash
git push origin feature/your-feature-name
```

5. Create a Pull Request

### Contribution Guidelines

1. **Code Style**

   - Follow PEP 8 guidelines
   - Use type hints
   - Add docstrings for functions and classes
   - Use meaningful variable names

2. **Testing**

   - Add tests for new features
   - Ensure all tests pass before submitting PR
   - Update documentation if needed

3. **Commit Messages**

   - Use clear, descriptive commit messages
   - Reference issues if applicable

4. **Pull Requests**
   - Describe changes in detail
   - Include screenshots for UI changes
   - Update README if needed

### Code of Conduct

- Be respectful and inclusive
- Follow the project's coding standards
- Help others and provide constructive feedback
- Report bugs and issues

## Usage

1. Start the application:

```bash
streamlit run src/main.py
```

2. Open your browser and navigate to `http://localhost:8501`

3. Start chatting with the assistant!

## Development

### Cleaning Cache Files

To remove all cache and temporary files from the project:

```bash
python scripts/cleanup.py
```

This will remove:

- Python cache files (`__pycache__`, `.pyc`, etc.)
- IDE cache directories (`.idea`, `.vscode`)
- Test cache (`.pytest_cache`, `.coverage`)
- Project cache (`.streamlit`, `redis-data`)
- Temporary files (`.swp`, `.swo`, `.DS_Store`)
