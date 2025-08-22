from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv('MONGO_URI', 'mongodb://localhost:27017/'))
db = client['credit_intelligence']

# Clear existing data
db.companies.delete_many({})

# Seed with real Yahoo Finance symbols
companies = [
    {
        "name": "Apple Inc.",
        "symbol": "AAPL",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "market_cap": "$3.2T",
        "lastUpdated": datetime.utcnow(),
        "creditScore": 78,
        "creditTrend": [
            {"month": "Jan", "score": 72},
            {"month": "Feb", "score": 74},
            {"month": "Mar", "score": 71},
            {"month": "Apr", "score": 76},
            {"month": "May", "score": 78},
            {"month": "Jun", "score": 78}
        ],
        "sentiment": [
            {"category": "Payment History", "positive": 85, "negative": 15},
            {"category": "Financial Stability", "positive": 72, "negative": 28},
            {"category": "Market Position", "positive": 90, "negative": 10},
            {"category": "Debt Management", "positive": 68, "negative": 32}
        ],
        "scoreFactors": [
            {"text": "Excellent payment history with 99.2% on-time payments", "positive": True},
            {"text": "Strong revenue growth of 15% year-over-year", "positive": True},
            {"text": "Market volatility affecting tech sector confidence", "positive": False},
            {"text": "High cash reserves providing financial stability", "positive": True}
        ],
        "current_price": 0,
        "pe_ratio": 0,
        "beta": 1.0,
        "volume": 0
    },
    {
        "name": "Microsoft Corporation",
        "symbol": "MSFT",
        "sector": "Technology",
        "industry": "Software",
        "market_cap": "$2.8T",
        "lastUpdated": datetime.utcnow(),
        "creditScore": 85,
        "creditTrend": [
            {"month": "Jan", "score": 80},
            {"month": "Feb", "score": 82},
            {"month": "Mar", "score": 83},
            {"month": "Apr", "score": 84},
            {"month": "May", "score": 85},
            {"month": "Jun", "score": 85}
        ],
        "sentiment": [
            {"category": "Payment History", "positive": 92, "negative": 8},
            {"category": "Financial Stability", "positive": 88, "negative": 12},
            {"category": "Market Position", "positive": 95, "negative": 5},
            {"category": "Debt Management", "positive": 85, "negative": 15}
        ],
        "scoreFactors": [
            {"text": "Consistent revenue growth across all business segments", "positive": True},
            {"text": "Strong cloud revenue driving profitability", "positive": True},
            {"text": "Diversified revenue streams reducing risk", "positive": True},
            {"text": "Competitive pressure in cloud market", "positive": False}
        ],
        "current_price": 0,
        "pe_ratio": 0,
        "beta": 1.0,
        "volume": 0
    },
    {
        "name": "Tesla Inc.",
        "symbol": "TSLA",
        "sector": "Consumer Discretionary",
        "industry": "Electric Vehicles",
        "market_cap": "$800B",
        "lastUpdated": datetime.utcnow(),
        "creditScore": 65,
        "creditTrend": [
            {"month": "Jan", "score": 68},
            {"month": "Feb", "score": 65},
            {"month": "Mar", "score": 62},
            {"month": "Apr", "score": 64},
            {"month": "May", "score": 65},
            {"month": "Jun", "score": 65}
        ],
        "sentiment": [
            {"category": "Payment History", "positive": 75, "negative": 25},
            {"category": "Financial Stability", "positive": 60, "negative": 40},
            {"category": "Market Position", "positive": 85, "negative": 15},
            {"category": "Debt Management", "positive": 55, "negative": 45}
        ],
        "scoreFactors": [
            {"text": "Strong brand recognition and market leadership", "positive": True},
            {"text": "High volatility in stock price affecting stability", "positive": False},
            {"text": "Heavy investment in R&D impacting short-term profits", "positive": False},
            {"text": "Growing market share in EV sector", "positive": True}
        ],
        "current_price": 0,
        "pe_ratio": 0,
        "beta": 1.5,
        "volume": 0
    }
]

# Insert companies
result = db.companies.insert_many(companies)
print(f"Inserted {len(result.inserted_ids)} companies into database")

# Create indexes
db.companies.create_index("name", unique=True)
db.companies.create_index("symbol", unique=True)

print("Database initialization complete!")
