# Intercom Data Security System

An AI-powered Data Security & DLP system for Intercom that protects sensitive information using machine learning.

## Features

- Real-time sensitive data detection using regex and ML
- Automatic data masking and redaction
- Data Loss Prevention (DLP) for external communications
- Machine Learning-based training for improved detection
- Admin dashboard for monitoring and management

## Tech Stack

- Backend: Python (FastAPI)
- Database: PostgreSQL
- ML Models: SpaCy, Transformers (BERT)
- APIs: Intercom Webhooks, OpenAI GPT-4

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
5. Initialize the database:
   ```bash
   python scripts/init_db.py
   ```
6. Run the application:
   ```bash
   uvicorn app.main:app --reload
   ```

## Environment Variables

Required environment variables:
- `INTERCOM_ACCESS_TOKEN`: Your Intercom API access token
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `JWT_SECRET`: Secret key for JWT authentication

## Project Structure

```
app/
├── api/            # API routes
├── core/           # Core functionality
├── models/         # Database models
├── schemas/        # Pydantic schemas
├── services/       # Business logic
├── utils/          # Utility functions
└── main.py         # Application entry point
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## License

MIT License 