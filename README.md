# Shopping Trend Radar Agent

An AI-powered trend analysis system that monitors shopping trends across Amazon, social media platforms (YouTube, TikTok, Instagram, Meta, Pinterest) and e-commerce sites (Etsy, Walmart, eBay, Target) to surface trending products for merchants and consumers.

- Demo Site- https://samirasamrose.github.io/shopping-trend-radar/
- Source Code- https://github.com/SamiraSamrose/shopping-trend-radar
- Video Demo- https://youtu.be/vSW4gKRmQ54


## Features

### For Merchants
- **Product Sourcing & Selection**: Discover trending products before they peak
- **Inventory Forecasting**: AI-powered demand prediction
- **Competitive Analysis**: Track competition levels and market saturation
- **Ad Campaign Planning**: Optimize targeting based on trend data
- **Niche Discovery**: Identify emerging micro-trends

### For Consumers
- **Smart Shopping**: Find trending products and best deals
- **Price Comparison**: Compare prices across all platforms
- **Event-Based Recommendations**: Get gift ideas for upcoming events
- **Trend Alerts**: Custom notifications for products you care about
- **Social Proof**: See what's popular across platforms

## Architecture

### Core Technologies
- **AWS Bedrock Agent** - AI analysis using Claude 3 Sonnet
- **Amazon SageMaker** - ML predictions for trend trajectories
- **Nova SDK** - Multi-platform API connector
- **Amazon Q** - Policy and compliance checking
- **Strands SDK** - Sales data ingestion
- **AWS Lambda + S3** - Serverless processing and storage

### Platform Coverage
- 🛒 Amazon - Sales rank, reviews, ratings
- 📺 YouTube - Views, engagement, mentions
- 🎵 TikTok - Viral content, hashtags
- 📸 Instagram - Posts, saves, engagement
- 👥 Meta/Facebook - Shares, likes, comments
- 📌 Pinterest - Pins, saves, impressions
- 🎨 Etsy - Favorites, sales, views
- 🏬 Walmart - Sales rank, reviews
- 🔨 eBay - Bids, watchers, sales
- 🎯 Target - Ratings, reviews, stock

## Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+
- Redis 7+
- AWS Account with access to:
  - Bedrock
  - SageMaker
  - Lambda
  - S3
  - CloudWatch
- API Keys for platforms (YouTube, TikTok, Instagram, etc.)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/samirasamrose/shopping-trend-radar.git
cd shopping-trend-radar
```

### 2. Create Environment File
```bash
cp .env.example .env
```

Edit `.env` and fill in your API keys and credentials:
```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key

# Bedrock
BEDROCK_AGENT_ID=your_agent_id
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# External APIs
YOUTUBE_API_KEY=your_youtube_key
TIKTOK_CLIENT_KEY=your_tiktok_key
# ... (see .env.example for complete list)
```

### 3. Install Dependencies

#### Using Docker (Recommended)
```bash
docker-compose up -d
```

#### Manual Installation
```bash
# Backend
cd backend
pip install -r requirements.txt

# Database
createdb trendradar
```

### 4. Initialize Database
```bash
cd backend
alembic upgrade head
python scripts/seed_data.py
```

## Running the Application

### Using Docker Compose
```bash
docker-compose up
```

The application will be available at:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Home Dashboard: http://localhost:8000/

### Manual Run
```bash
# Terminal 1 - Start Redis
redis-server

# Terminal 2 - Start PostgreSQL
postgres -D /usr/local/var/postgres

# Terminal 3 - Start Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Usage Guide

### Merchant Dashboard

Navigate to http://localhost:8000/merchant

**Features:**
1. **High Opportunity Products** - Products with low competition and high trend potential
2. **Sourcing Recommendations** - Supplier suggestions with cost estimates
3. **Inventory Planning** - Demand forecasts and stock recommendations
4. **Ad Targeting** - Campaign suggestions based on trending data

**Example Workflow:**
```python
# Get trending products for merchants
curl http://localhost:8000/api/v1/trends/products?min_score=0.7&limit=20

# Get merchant insights for a product
curl http://localhost:8000/api/v1/products/merchant-insights/product_123
```

### Consumer Dashboard

Navigate to http://localhost:8000/consumer

**Features:**
1. **Hot Products** - Currently trending items across all platforms
2. **Event Recommendations** - Gift ideas for upcoming holidays
3. **Price Comparisons** - Best deals across platforms
4. **Custom Alerts** - Notifications for products matching your criteria

**Example Workflow:**
```python
# Compare product prices
curl "http://localhost:8000/api/v1/products/compare/wireless%20earbuds"

# Get event recommendations
curl http://localhost:8000/api/v1/products/events?days_ahead=30

# Create alert
curl -X POST http://localhost:8000/api/v1/alerts/ \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "keywords": ["smartphone", "gaming"],
    "categories": ["Electronics"],
    "min_trend_score": 0.7
  }'
```

### Interactive Demo

Navigate to http://localhost:8000/demo

**Features:**
1. **System Architecture Tour** - Explore all AWS tools and SDKs
2. **Live Pipeline Demo** - Watch data flow through the entire system
3. **Platform Monitoring** - Test individual platform APIs
4. **Use Case Scenarios** - Pre-built scenarios for merchants and consumers
5. **API Testing Console** - Interactive API endpoint testing

## 🔧 API Documentation

### Core Endpoints

#### Trends
```bash
# Get trending products
GET /api/v1/trends/products?categories=Electronics&min_score=0.7&limit=50

# Get product details
GET /api/v1/trends/products/{product_id}

# Get trend prediction
GET /api/v1/trends/predictions/{product_id}

# Generate trend report
GET /api/v1/trends/report?user_type=merchant&categories=Electronics

# Get trending categories
GET /api/v1/trends/categories
```

#### Products
```bash
# Compare prices
GET /api/v1/products/compare/{product_name}?platforms=amazon,walmart

# Get event recommendations
GET /api/v1/products/events?days_ahead=30

# Get merchant insights
GET /api/v1/products/merchant-insights/{product_id}

# Get consumer insights
GET /api/v1/products/consumer-insights/{product_id}

# Check compliance
GET /api/v1/products/compliance-check?product_name=Widget&category=Electronics
```

#### Alerts
```bash
# Create alert
POST /api/v1/alerts/
{
  "user_id": "user123",
  "keywords": ["laptop", "gaming"],
  "categories": ["Electronics"],
  "min_trend_score": 0.7,
  "platforms": ["amazon", "tiktok"]
}

# Get user alerts
GET /api/v1/alerts/user/{user_id}

# Update alert
PUT /api/v1/alerts/{alert_id}

# Delete alert
DELETE /api/v1/alerts/{alert_id}

# Check alert
GET /api/v1/alerts/{alert_id}/check
```

## Testing

### Run Unit Tests
```bash
cd backend
pytest tests/ -v
```

### Run Integration Tests
```bash
pytest tests/test_integration.py -v
```

### Test Individual Services
```bash
# Test Bedrock Agent
python -m tests.test_bedrock_agent

# Test SageMaker
python -m tests.test_sagemaker

# Test API endpoints
pytest tests/test_api.py -v
```

## AWS Lambda Functions

### Deploy Lambda Functions
```bash
cd backend/lambda_functions

# Package dashboard generator
zip -r dashboard_generator.zip dashboard_generator.py

# Deploy to AWS
aws lambda create-function \
  --function-name trend-radar-dashboard-generator \
  --runtime python3.11 \
  --handler dashboard_generator.lambda_handler \
  --zip-file fileb://dashboard_generator.zip \
  --role arn:aws:iam::YOUR_ACCOUNT:role/lambda-execution-role
```

### Configure EventBridge Triggers
```bash
# Schedule dashboard generation every hour
aws events put-rule \
  --name trend-radar-hourly-dashboard \
  --schedule-expression "rate(1 hour)"

aws events put-targets \
  --rule trend-radar-hourly-dashboard \
  --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:trend-radar-dashboard-generator"
```

## Database Schema

### Products Table
```sql
CREATE TABLE products (
    id VARCHAR(255) PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    category VARCHAR(100),
    description TEXT,
    price DECIMAL(10, 2),
    trend_score DECIMAL(3, 2),
    viral_velocity DECIMAL(3, 2),
    status VARCHAR(50),
    platforms TEXT[],
    first_seen TIMESTAMP,
    last_updated TIMESTAMP
);
```

### Alerts Table
```sql
CREATE TABLE alerts (
    id VARCHAR(255) PRIMARY KEY,
    user_id VARCHAR(255) NOT NULL,
    product_id VARCHAR(255),
    keywords TEXT[],
    categories TEXT[],
    min_trend_score DECIMAL(3, 2),
    platforms TEXT[],
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP
);
```

## Monitoring & Metrics

### CloudWatch Metrics

The system automatically sends metrics to CloudWatch:

- `APILatency` - API response times
- `APICallCount` - Total API calls
- `ProductsAnalyzed` - Number of products analyzed
- `PlatformFetchSuccess` - Platform API success rate
- `TrendAnalysisTime` - Trend analysis processing time

### View Metrics
```bash
aws cloudwatch get-metric-statistics \
  --namespace TrendRadar \
  --metric-name APILatency \
  --start-time 2025-10-17T00:00:00Z \
  --end-time 2025-10-17T23:59:59Z \
  --period 3600 \
  --statistics Average
```

## Security

### Environment Variables

Never commit `.env` file. Use AWS Secrets Manager in production:
```python
import boto3

secrets = boto3.client('secretsmanager')
response = secrets.get_secret_value(SecretId='trend-radar/api-keys')
```

### API Rate Limiting

Rate limits are enforced per endpoint:
- 60 requests/minute for trend endpoints
- 30 requests/minute for prediction endpoints
- 100 requests/minute for query endpoints

### Authentication

For production, implement JWT authentication:
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def verify_token(credentials = Depends(security)):
    # Verify JWT token
    pass
```

## Deployment

### Deploy to AWS ECS
```bash
# Build Docker image
docker build -t shopping-trend-radar:latest .

# Tag for ECR
docker tag shopping-trend-radar:latest YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shopping-trend-radar:latest

# Push to ECR
docker push YOUR_ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/shopping-trend-radar:latest

# Deploy to ECS
aws ecs update-service \
  --cluster trend-radar-cluster \
  --service trend-radar-service \
  --force-new-deployment
```

### Infrastructure as Code (Terraform)
```bash
cd infrastructure/terraform

# Initialize
terraform init

# Plan
terraform plan

# Apply
terraform apply
```

## Configuration

### Custom Event Calendar

Edit `backend/app/config.py` to add custom events:
```python
CALENDAR_EVENTS = {
    "12-25": {
        "name": "Christmas",
        "categories": ["Gifts", "Decorations", "Toys"]
    },
    # Add your custom events
}
```

### Platform Weights

Adjust platform importance in trend calculations:
```python
SUPPORTED_PLATFORMS = {
    "amazon": {"weight": 0.25},
    "tiktok": {"weight": 0.20},
    # Adjust weights as needed
}
```

## Troubleshooting

### Common Issues

**1. Database Connection Error**
```bash
# Check PostgreSQL is running
pg_isready

# Reset database
dropdb trendradar
createdb trendradar
alembic upgrade head
```

**2. Redis Connection Error**
```bash
# Check Redis is running
redis-cli ping

# Restart Redis
redis-server --daemonize yes
```

**3. AWS Credentials Error**
```bash
# Configure AWS CLI
aws configure

# Test credentials
aws sts get-caller-identity
```

**4. API Key Issues**
```bash
# Verify all keys are set
python -c "from app.config import get_settings; s = get_settings(); print(s.dict())"
```

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Amazon SageMaker Guide](https://docs.aws.amazon.com/sagemaker/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [YouTube Data API](https://developers.google.com/youtube/v3)
- [TikTok API](https://developers.tiktok.com/)
