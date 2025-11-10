# Vector RAG demo

This is a demo of how to use Vector DB with LangChain.
Two projects are included:
1. aicompany - Ideal project for a Vector DB. It is a company policies and guidelines. Chatbot with context.
2. harry - Not a perfect project for a Vector DB. It is a Harry Potter chatbot. It is a bit more complex. The perfect project to show vector DB limitations.

## How to run:

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate && pip install --upgrade pip
source venv/bin/activate && pip install -r requirements.txt
```

2. Activate virtual environment:
```bash
source venv/bin/activate
```

3. Copy example environment variables and fill them:
```bash
cp .env.example .env
```

