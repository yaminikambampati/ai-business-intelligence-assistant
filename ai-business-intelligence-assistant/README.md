# AI Business Intelligence Assistant

A mini AI-powered business intelligence application that allows users to ask questions about sales data in natural language and receive answers calculated from actual database queries.

## Problem Statement

Business users need quick access to sales insights without writing SQL queries or navigating complex dashboards. This application provides a natural language interface to query sales transaction data and receive accurate, data-driven answers.

## Project Objectives

- Enable natural language queries about sales data
- Provide accurate answers from actual database records
- Support five core analytical questions
- Ensure security and data integrity
- Demonstrate clean Python development practices
- Showcase optional LLM integration
- Provide comprehensive testing and documentation

## Features

- **Natural Language Questions**: Ask questions in plain English
- **Five Core Analytics**:
  1. Total revenue calculation
  2. Highest-revenue product identification
  3. Monthly revenue trend analysis
  4. Highest-sales region identification
  5. Revenue comparison between months
- **CSV Data Import**: Load sales data from CSV files with validation
- **SQLite Database**: Reliable, embedded database storage
- **FastAPI Backend**: Modern, fast REST API
- **Streamlit Frontend**: Interactive web interface
- **Optional LLM Integration**: OpenAI-compatible API for flexible language understanding
- **Deterministic Fallback**: Works without LLM API key
- **SQL Security**: Parameterized queries with validation
- **Comprehensive Tests**: 60+ automated test cases
- **Complete Documentation**: Architecture, development report, and user guide

## Technology Stack

### Backend
- **Python 3.11+**: Core programming language
- **FastAPI**: Modern web framework for APIs
- **Uvicorn**: ASGI server
- **Pydantic**: Data validation
- **SQLAlchemy**: Database ORM (sqlite3 used directly)
- **SQLite**: Embedded database
- **Pandas**: Data processing
- **NumPy**: Numerical operations
- **OpenAI**: Optional LLM integration

### Frontend
- **Streamlit**: Python-based web UI framework
- **Plotly**: Interactive charts
- **Requests**: HTTP client

### Testing
- **pytest**: Testing framework
- **httpx**: Async HTTP client for testing

### Development
- **Git**: Version control
- **Python-dotenv**: Environment variable management

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
Business User
    ↓
Streamlit Frontend
    ↓
FastAPI Backend
    ↓
Question Parser (Deterministic + Optional LLM)
    ↓
Intent Validation
    ↓
Analytics Service
    ↓
Parameterized SQL
    ↓
SQLite Database
    ↓
Verified Results
    ↓
Structured Response
    ↓
Streamlit UI
```

For detailed architecture documentation, see [docs/architecture.md](docs/architecture.md).

## Directory Structure

```
ai-business-intelligence-assistant/
│
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── database.py          # Database connection and schema
│   ├── schemas.py           # Pydantic models
│   ├── data_loader.py       # CSV import logic
│   ├── analytics.py         # Business logic calculations
│   ├── question_parser.py   # Deterministic question parsing
│   ├── ai_service.py        # Optional LLM integration
│   ├── query_validator.py   # SQL security validation
│   └── config.py            # Configuration management
│
├── frontend/
│   └── app.py               # Streamlit UI
│
├── data/
│   ├── .gitkeep
│   └── sales.csv            # Your sales data (place here)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── test_analytics.py    # Analytics tests
│   ├── test_data_loader.py  # Data loading tests
│   ├── test_api.py          # API endpoint tests
│   ├── test_security.py     # Security tests
│   └── test_edge_cases.py   # Edge case tests
│
├── docs/
│   ├── architecture.md      # Architecture documentation
│   └── development_report.md # Development report
│
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── README.md                # This file
└── run.py                   # Convenience script (optional)
```

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git (for version control)
- A CSV file with sales transaction data

## Installation Instructions

### 1. Clone or Download the Project

```bash
# If using Git
git clone <repository-url>
cd ai-business-intelligence-assistant

# Or download and extract the zip file
```

### 2. Create Virtual Environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies

**Windows PowerShell:**
```powershell
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example environment file:

**Windows PowerShell:**
```powershell
Copy-Item .env.example .env
```

**Linux/macOS:**
```bash
cp .env.example .env
```

Edit `.env` to add your OpenAI API key (optional):

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4o-mini
DATABASE_PATH=data/sales.db
```

**Note**: The application works without an LLM API key using deterministic parsing.

## CSV Placement Instructions

1. Place your sales CSV file in the `data/` directory
2. Name it `sales.csv` (or use a custom name and specify it when loading)
3. Ensure the CSV has the following columns (or configure column mapping):

**Required columns:**
- Transaction ID (e.g., Transaction_Id)
- Order Date (e.g., Order_date)
- Product Name (e.g., Product)
- Region (e.g., Region)

**Optional columns:**
- Category (e.g., Category)
- Sales Channel (e.g., Sales_channel)
- Quantity (e.g., Quantity)
- Unit Price (e.g., Unit_price)
- Discount Amount (e.g., Discount_amount)
- Status (e.g., Status)

**Date format:** DD-MM-YYYY (e.g., 15-01-2026)

## Database Initialization

The database is automatically initialized when you first load data. No manual initialization is required.

## CSV Import Instructions

### Import CSV Data

**Windows PowerShell:**
```powershell
python -m backend.data_loader --csv data/sales.csv
```

**Linux/macOS:**
```bash
python -m backend.data_loader --csv data/sales.csv
```

### Custom Date Format

If your CSV uses a different date format:

```bash
python -m backend.data_loader --csv data/sales.csv --date-format "%Y-%m-%d"
```

### Import Summary

The data loader will display:
- Total rows in CSV
- Valid rows
- Invalid rows
- Rows loaded into database
- Rows skipped (duplicates/errors)
- Rejection reasons

## Running the Application

### Start the Backend

**Windows PowerShell:**
```powershell
uvicorn backend.main:app --reload
```

**Linux/macOS:**
```bash
uvicorn backend.main:app --reload
```

The backend will start on `http://localhost:8000`

### Start the Frontend (New Terminal)

Open a new terminal window, activate the virtual environment, then:

**Windows PowerShell:**
```powershell
streamlit run frontend/app.py
```

**Linux/macOS:**
```bash
streamlit run frontend/app.py
```

The frontend will open in your browser at `http://localhost:8501`

## Running Automated Tests

**Windows PowerShell:**
```powershell
pytest -v
```

**Linux/macOS:**
```bash
pytest -v
```

### Run Specific Test Files

```bash
pytest tests/test_analytics.py -v
pytest tests/test_api.py -v
pytest tests/test_security.py -v
```

### Run with Coverage

```bash
pytest --cov=backend --cov=frontend -v
```

## API Endpoint Documentation

Once the backend is running, visit `http://localhost:8000/docs` for interactive API documentation (Swagger UI).

### Endpoints

#### 1. GET /health
Check application health and database status.

**Response:**
```json
{
  "status": "healthy",
  "database_available": true,
  "record_count": 51
}
```

#### 2. GET /metadata
Get dataset metadata.

**Response:**
```json
{
  "record_count": 51,
  "date_range": {
    "start": "2026-01-03",
    "end": "2026-06-28"
  },
  "products": ["Laptop Stand", "Wireless Mouse", ...],
  "regions": ["North", "South", "East", "West"],
  "import_status": "completed"
}
```

#### 3. POST /ask
Ask a natural language question.

**Request:**
```json
{
  "question": "What is the total revenue?"
}
```

**Response:**
```json
{
  "success": true,
  "question": "What is the total revenue?",
  "intent": "total_revenue",
  "answer": "The total revenue is 169650.00.",
  "data": {
    "total_revenue": 169650.0,
    "transaction_count": 51,
    "explanation": "..."
  },
  "explanation": "...",
  "limitations": [],
  "source": "database"
}
```

#### 4. GET /analytics/total-revenue
Get total revenue.

#### 5. GET /analytics/top-product
Get highest-revenue product.

#### 6. GET /analytics/monthly-revenue
Get monthly revenue trend.

#### 7. GET /analytics/top-region
Get highest-sales region.

#### 8. GET /analytics/revenue-comparison
Compare revenue between months.

**Query Parameters:**
- `month1`: First month (1-12)
- `year1`: First year (e.g., 2026)
- `month2`: Second month (1-12)
- `year2`: Second year (e.g., 2026)

**Example:**
```
GET /analytics/revenue-comparison?month1=1&year1=2026&month2=2&year2=2026
```

## Supported Natural Language Questions

The application supports these core question types:

### 1. Total Revenue
- "What is the total revenue?"
- "Calculate total sales revenue."
- "What is our overall revenue?"
- "Show me the total sales."

### 2. Highest-Revenue Product
- "Which product generated the highest revenue?"
- "What product made the most money?"
- "Show the top product by revenue."
- "Which product has the highest sales?"

### 3. Monthly Revenue Trend
- "What is the monthly revenue trend?"
- "Show revenue month by month."
- "Display monthly sales data."
- "Revenue by month?"

### 4. Highest-Sales Region
- "Which region generated the highest sales?"
- "What region performed best?"
- "Show the top region by revenue."
- "Which region has the most sales?"

### 5. Revenue Comparison
- "How did revenue change between January 2026 and February 2026?"
- "Compare revenue in January 2026 and February 2026."
- "Revenue difference between 2026-01 and 2026-02."

## Sample Request and Response

### Request
```json
POST /ask
{
  "question": "Which product generated the highest revenue?"
}
```

### Response
```json
{
  "success": true,
  "question": "Which product generated the highest revenue?",
  "intent": "top_product",
  "answer": "The product 'Monitor' generated the highest revenue of 56500.00.",
  "data": {
    "product": "Monitor",
    "total_revenue": 56500.0,
    "all_products": [
      {"product": "Monitor", "total_revenue": 56500.0, "transaction_count": 4},
      {"product": "Office Chair", "total_revenue": 39000.0, "transaction_count": 5},
      ...
    ],
    "explanation": "Product 'Monitor' generated the highest revenue of 56500.00 from 4 transactions."
  },
  "explanation": "Product 'Monitor' generated the highest revenue of 56500.00 from 4 transactions.",
  "limitations": [],
  "source": "database"
}
```

## Database Schema and Query Explanation

### Table: sales_transactions

```sql
CREATE TABLE sales_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_id TEXT UNIQUE NOT NULL,
    transaction_date DATE NOT NULL,
    product TEXT NOT NULL,
    category TEXT,
    region TEXT NOT NULL,
    sales_channel TEXT,
    quantity INTEGER,
    unit_price REAL,
    discount_amount REAL DEFAULT 0,
    status TEXT,
    revenue REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### Revenue Calculation

Revenue is calculated as:
```
revenue = (quantity × unit_price) - discount_amount
```

### Indexes

- `idx_transaction_date` on `transaction_date`
- `idx_product` on `product`
- `idx_region` on `region`

### Query Examples

**Total Revenue:**
```sql
SELECT SUM(revenue) as total, COUNT(*) as count
FROM sales_transactions
WHERE revenue IS NOT NULL
```

**Top Product:**
```sql
SELECT product, SUM(revenue) as total_revenue, COUNT(*) as transaction_count
FROM sales_transactions
WHERE revenue IS NOT NULL
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 1
```

**Monthly Revenue:**
```sql
SELECT
    strftime('%Y-%m', transaction_date) as month,
    SUM(revenue) as total_revenue,
    COUNT(*) as transaction_count
FROM sales_transactions
WHERE revenue IS NOT NULL
GROUP BY month
ORDER BY month ASC
```

## Data Validation and Invalid Record Handling

### Validation Rules

1. **Required Fields**: transaction_id, transaction_date, product, region must be present
2. **Date Format**: Must match specified format (default: DD-MM-YYYY)
3. **Numeric Fields**: quantity and unit_price must be valid numbers
4. **Negative Values**: Negative quantities and prices are rejected
5. **Duplicates**: Duplicate transaction IDs are skipped

### Handling Policy

- **Valid Records**: Inserted into database
- **Invalid Records**: Logged with reason and skipped
- **Missing Fields**: Record rejected with specific reason
- **Invalid Dates**: Record rejected with date format error
- **Negative Revenue**: Not automatically removed (may represent refunds)
- **Zero Quantity**: Allowed but may affect calculations
- **Returned Items**: Status field preserved, revenue still calculated

### Import Statistics

The data loader reports:
- Total rows in CSV
- Valid rows (pass validation)
- Invalid rows (fail validation)
- Loaded rows (successfully inserted)
- Skipped rows (duplicates or errors)
- Rejection reasons (first 10)

## AI Integration Design

### Architecture

The AI integration is designed as an optional enhancement:

1. **Primary**: Deterministic regex-based parser
2. **Fallback**: LLM-based interpretation when available
3. **Validation**: All LLM responses validated with Pydantic
4. **Structured Output**: LLM returns JSON conforming to schema

### Intent Schema

```python
{
  "intent": "total_revenue|top_product|monthly_revenue|top_region|revenue_comparison|unsupported",
  "parameters": {},
  "requires_clarification": false,
  "confidence": "high|medium|low",
  "message": null
}
```

### LLM Configuration

- **Provider**: OpenAI-compatible API
- **Model**: Configurable (default: gpt-4o-mini)
- **Temperature**: 0.0 (deterministic output)
- **Response Format**: JSON mode

### Safety

- LLM only interprets questions, doesn't calculate results
- Numerical answers always from database
- LLM never executes SQL
- Responses validated before use
- Fallback to deterministic parser on failure

### Configuration

Set in `.env`:
```env
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini
```

## SQL Security Design

### Prevention Measures

1. **Parameterized Queries**: All user input uses prepared statements
2. **Query Validation**: SQL validator checks queries before execution
3. **Allowed Operations**: Only SELECT statements permitted
4. **Forbidden Keywords**: INSERT, UPDATE, DELETE, DROP, etc. rejected
5. **Table Whitelist**: Only authorized tables can be queried
6. **Statement Limits**: Multiple statements rejected
7. **Comment Blocking**: SQL comments (--, /*) rejected
8. **Pattern Detection**: Suspicious patterns identified

### Validation Process

```python
def validate_query(query: str) -> Tuple[bool, str]:
    # 1. Check for forbidden keywords
    # 2. Check for multiple statements
    # 3. Check for SQL comments
    # 4. Verify SELECT only
    # 5. Verify allowed tables
    # 6. Check for suspicious patterns
    return is_valid, error_message
```

### Test Coverage

Security tests verify:
- Valid SELECT queries accepted
- DELETE queries rejected
- DROP queries rejected
- UPDATE queries rejected
- INSERT queries rejected
- Multiple statements rejected
- SQL comments rejected
- Unauthorized tables rejected

## Error Handling Strategy

### API Error Handling

- **400 Bad Request**: Invalid input, empty question
- **503 Service Unavailable**: Database not available
- **500 Internal Server Error**: Unexpected errors
- **Generic Handler**: Catches all exceptions, returns safe error message

### Frontend Error Handling

- Connection errors displayed to user
- Backend unavailability warning
- Invalid input validation
- Loading states during processing
- Clear error messages

### Database Error Handling

- Transactions rolled back on error
- Connection context managers ensure cleanup
- Specific error messages logged
- Graceful degradation

### CSV Import Error Handling

- Invalid rows logged and skipped
- Detailed rejection reasons
- Import summary always displayed
- Partial imports allowed

## Known Limitations

1. **Question Understanding**: Limited to predefined patterns without LLM
2. **Date Format**: Only DD-MM-YYYY supported by default
3. **Currency**: No currency conversion or formatting
4. **Scale**: SQLite may not scale to millions of records
5. **Concurrency**: Synchronous request processing
6. **Authentication**: No user authentication
7. **Caching**: No query result caching
8. **Deployment**: Not containerized or production-ready

See [docs/development_report.md](docs/development_report.md) for complete limitations.

## Troubleshooting

### Backend Won't Start

**Problem**: Port 8000 already in use
**Solution**: Use a different port:
```bash
uvicorn backend.main:app --port 8001
```

### Database Not Available

**Problem**: "Database not available or empty" error
**Solution**: Load CSV data first:
```bash
python -m backend.data_loader --csv data/sales.csv
```

### CSV Import Fails

**Problem**: "Missing required columns" error
**Solution**: Check CSV has required columns:
- Transaction_Id
- Order_date
- Product
- Region

### Date Parsing Errors

**Problem**: "Invalid date format" errors
**Solution**: Specify your date format:
```bash
python -m backend.data_loader --csv data/sales.csv --date-format "%Y-%m-%d"
```

### LLM Not Working

**Problem**: AI service not available
**Solution**: Add API key to `.env` or use deterministic parsing (works without API key)

### Tests Failing

**Problem**: pytest errors
**Solution**: Ensure dependencies installed:
```bash
pip install -r requirements.txt
```

### Frontend Can't Connect

**Problem**: Connection error in Streamlit
**Solution**: Ensure backend is running on http://localhost:8000

## Future Improvements

- Enhanced natural language understanding
- More analytical questions
- Authentication and authorization
- Docker containerization
- PostgreSQL migration
- Caching layer
- CI/CD pipeline
- AWS cloud deployment
- Performance optimization
- More comprehensive tests

## Interview Preparation

### Key Concepts Explained

#### 1. What is Generative AI?
Generative AI refers to artificial intelligence systems that can create new content (text, images, code, etc.) rather than just analyzing or classifying existing data. Examples include GPT for text, DALL-E for images, and Copilot for code.

#### 2. What is an LLM?
Large Language Models (LLMs) are neural networks trained on vast amounts of text data. They understand and generate human-like text by predicting the next word in a sequence. Examples: GPT-4, Claude, Llama.

#### 3. What is an AI Agent?
An AI agent is a system that perceives its environment, makes decisions, and takes actions to achieve goals. In this application, the "agent" is the workflow that receives questions, interprets them, validates parameters, executes analytics, and returns results.

#### 4. What is Agentic AI?
Agentic AI refers to AI systems that can autonomously plan and execute multi-step tasks to achieve objectives. This application demonstrates a bounded, controlled agent workflow rather than full autonomous agency.

#### 5. How Does This Application's Workflow Work?
1. User asks question in Streamlit UI
2. Frontend sends HTTP request to FastAPI
3. Question parser determines intent (deterministic or LLM)
4. Intent and parameters are validated
5. Analytics service executes calculation
6. Parameterized SQL queries database
7. Results formatted into structured response
8. API returns JSON to frontend
9. Frontend displays answer with supporting data

#### 6. What is RAG?
Retrieval-Augmented Generation (RAG) is a technique that combines retrieval of relevant documents with generative AI to produce more accurate, context-aware responses. This application does NOT implement RAG.

#### 7. What is Vectorless RAG?
"Vectorless RAG" is sometimes used to describe systems that retrieve structured data (like database records) rather than vector embeddings of documents. This application retrieves from a database but does not use vector search or embeddings.

#### 8. What is LangChain?
LangChain is a framework for building applications with LLMs. It provides tools for prompt management, memory, agents, and data retrieval. This application does not use LangChain but is designed modularly to allow future integration.

#### 9. What is Google ADK?
Google AI Development Kit (ADK) is Google's framework for building AI applications. This application does not use Google ADK.

#### 10. What is Dify?
Dify is an open-source LLM application development platform. This application does not use Dify.

#### 11. Why SQLite?
SQLite was chosen because:
- No server setup required
- Single-file database for easy portability
- Sufficient for development and small datasets
- Built-in Python support
- Reliable ACID transactions
- Easy to backup and migrate

#### 12. Why FastAPI?
FastAPI was chosen because:
- Modern, fast Python web framework
- Automatic OpenAPI documentation
- Pydantic integration for validation
- Type hints improve code quality
- Async support for future scalability
- Easy testing with TestClient

#### 13. Why Pandas?
Pandas was chosen because:
- Industry-standard for data processing
- Powerful CSV handling
- Built-in data validation
- Easy data transformation
- Familiar to data engineers
- Efficient for in-memory operations

#### 14. How is Natural Language Converted to Analytics Operations?
The application uses two approaches:
1. **Deterministic**: Regex patterns match common question phrases
2. **LLM (optional)**: OpenAI API interprets varied phrasing
Both return structured intent and parameters that map to specific analytics functions.

#### 15. Why are Database Queries More Reliable than LLM Calculations?
LLMs can hallucinate or make calculation errors. Database queries:
- Use actual data from records
- Provide deterministic, reproducible results
- Can be verified and audited
- Don't suffer from training data cutoffs
- Handle edge cases consistently

#### 16. How are SQL Injection and Destructive Queries Prevented?
- Parameterized queries prevent injection
- SQL validator rejects destructive keywords
- Only SELECT statements allowed
- Table whitelist enforced
- Multiple statements rejected
- SQL comments blocked
- All queries validated before execution

#### 17. What Do Automated Tests Verify?
- Correctness of analytics calculations
- API endpoint behavior
- Data validation logic
- SQL security measures
- Edge case handling
- Error scenarios
- Integration between components

#### 18. How Could This Be Deployed to AWS?
- **API**: FastAPI on AWS Lambda with API Gateway
- **Database**: Amazon RDS (PostgreSQL)
- **Storage**: Amazon S3 for CSV files
- **AI**: Amazon Bedrock for LLM
- **Auth**: Amazon Cognito
- **Monitoring**: CloudWatch

#### 19. What Are the Limitations?
- No authentication or authorization
- Limited question variations without LLM
- SQLite may not scale to large datasets
- No caching or performance optimization
- Not containerized for production
- Limited UI customization

#### 20. How Could This Be Extended into a More Advanced Agentic System?
- Add tool-calling capabilities
- Implement multi-step reasoning
- Support compound questions
- Add context awareness
- Implement follow-up questions
- Use agent frameworks (LangChain, AutoGen)
- Add memory for conversation history
- Enable autonomous task planning

## Git Submission Instructions

### Initialize Git Repository

**Windows PowerShell:**
```powershell
git init
```

**Linux/macOS:**
```bash
git init
```

### Add Files

**Windows PowerShell:**
```powershell
git add .
```

**Linux/macOS:**
```bash
git add .
```

### Commit Changes

**Windows PowerShell:**
```powershell
git commit -m "Build AI Business Intelligence Assistant"
```

**Linux/macOS:**
```bash
git commit -m "Build AI Business Intelligence Assistant"
```

### Create GitHub Repository

1. Go to https://github.com/new
2. Create a new repository (don't initialize with README)
3. Copy the repository URL

### Push to GitHub

**Windows PowerShell:**
```powershell
git remote add origin <your-repository-url>
git branch -M main
git push -u origin main
```

**Linux/macOS:**
```bash
git remote add origin <your-repository-url>
git branch -M main
git push -u origin main
```

## License

This project is created for a Graduate Engineer Trainee assessment.

## Contact

For questions or support, please refer to the development team or project documentation.
