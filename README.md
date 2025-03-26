# Intercom Data Security System

An AI-powered Data Security & DLP system for Intercom that protects sensitive information using machine learning.

## Features

- Real-time sensitive data detection using regex and ML
- Automatic data masking and redaction
- Data Loss Prevention (DLP) for external communications
- Machine Learning-based training for improved detection
- Admin dashboard for monitoring and management
- Secure vault for storing sensitive data
- Role-based access control (Admin, Reviewer, Viewer)

## Tech Stack

- Backend: Python (FastAPI)
- Database: SQLite (development) / PostgreSQL (production)
- ML Models: SpaCy, Transformers (BERT)
- APIs: Intercom Webhooks, OpenAI GPT-4
- Authentication: JWT with OAuth2

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/intercom-security.git
   cd intercom-security
   ```

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
- `DATABASE_URL`: Database connection string (default: SQLite)
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `JWT_SECRET`: Secret key for JWT authentication
- `MODEL_CONFIDENCE_THRESHOLD`: Confidence threshold for ML model (default: 0.85)
- `MAX_TOKENS`: Maximum tokens for OpenAI API (default: 1000)
- `BLOCK_EXTERNAL_MESSAGES`: Whether to block messages with sensitive data (default: true)
- `NOTIFY_ADMIN_ON_BLOCK`: Whether to notify admin on blocked messages (default: true)

## Project Structure

```
app/
├── api/            # API routes
│   ├── api_v1/     # API version 1
│   │   └── endpoints/  # API endpoints
│   └── deps.py     # Dependencies
├── core/           # Core functionality
│   ├── config.py   # Configuration
│   └── database.py # Database setup
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

## Development

### Running Tests
```bash
pytest
```

### Code Style
The project follows PEP 8 guidelines. You can check your code style using:
```bash
flake8
```

### Database Migrations
When making changes to models, update the database:
```bash
python scripts/init_db.py
```

## Security Considerations

- All sensitive data is encrypted at rest
- API keys and secrets are stored in environment variables
- JWT tokens are used for authentication
- Role-based access control is implemented
- Sensitive data is automatically masked in messages
- External messages with sensitive data can be blocked

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License 