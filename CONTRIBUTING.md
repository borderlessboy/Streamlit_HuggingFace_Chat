# Contributing to HuggingFace Inference Chat

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

1. Fork the repository
2. Clone your fork:

```bash
git clone https://github.com/your-username/huggingface-inference-chat.git
```

3. Create a virtual environment and install dependencies:

```bash
python -m venv venv
source venv/bin/activate  # or `.\venv\Scripts\activate` on Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

## Development Process

1. Create a new branch:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes:

   - Follow the code style guidelines
   - Add tests for new features
   - Update documentation as needed

3. Run tests:

```bash
pytest tests/
```

4. Format and lint your code:

```bash
black .
ruff check .
```

5. Commit your changes:

```bash
git commit -m "Description of changes"
```

6. Push to your fork:

```bash
git push origin feature/your-feature-name
```

7. Create a Pull Request

## Code Style Guidelines

- Follow PEP 8
- Use type hints
- Write descriptive docstrings
- Keep functions focused and small
- Use meaningful variable names

## Testing

- Write unit tests for new features
- Ensure all tests pass before submitting PR
- Aim for high test coverage
- Include both positive and negative test cases

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Include code examples where helpful
- Keep documentation clear and concise

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the documentation
3. The PR must pass all CI checks
4. Get approval from at least one maintainer

## Questions?

Feel free to create an issue or contact the maintainers.
