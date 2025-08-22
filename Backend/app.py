# app.py
from flask import Flask, jsonify, request
from pymongo import MongoClient
import yfinance as yf
from datetime import datetime
import datetime as dt
from flask_cors import CORS
import threading
import time
import random
import pandas as pd
import numpy as np # FIX: Import numpy for advanced array operations
from config import Config

# Initialize Flask app
app = Flask(__name__)
# Enable Cross-Origin Resource Sharing for the React app
CORS(app)

# MongoDB connection
client = MongoClient(Config.MONGO_URI)
db = client.credit_intelligence
companies_col = db.companies

# List of companies (stock tickers) to track
COMPANIES = [
    {"name": "Apple Inc.", "ticker": "AAPL"},
    {"name": "Microsoft Corp.", "ticker": "MSFT"},
    {"name": "Alphabet Inc.", "ticker": "GOOGL"},
    {"name": "Amazon.com Inc.", "ticker": "AMZN"},
    {"name": "NVIDIA Corp.", "ticker": "NVDA"},
]

def calculate_credit_score(close_price, ma50):
    """
    Calculates a simplified credit score based on stock price relative to its 50-day moving average.
    """
    # Avoid division by zero
    if ma50 == 0:
        return 70
        
    score = 70 + (close_price - ma50) / ma50 * 100
    return max(0, min(100, score)) # Clamp score between 0 and 100

def generate_sentiment_data(ticker_name):
    """
    Generates sentiment data based on the company's recent stock performance.
    """
    try:
        ticker = yf.Ticker(ticker_name)
        hist = ticker.history(period="30d")
        if hist.empty:
            return []

        # Calculate percentage change over the last 30 days
        start_price = hist['Close'].iloc[0]
        end_price = hist['Close'].iloc[-1]
        percent_change = ((end_price - start_price) / start_price) * 100

        # Adjust sentiment based on the stock's recent performance
        base_positive = 75 # Neutral baseline
        if percent_change > 5: # Strong upward trend
            base_positive = 90
        elif percent_change < -5: # Strong downward trend
            base_positive = 50
        elif percent_change > 0: # Slight upward trend
            base_positive = 80
        elif percent_change < 0: # Slight downward trend
            base_positive = 65

        categories = ["News", "Social Media", "Reports"]
        sentiment_data = []

        for category in categories:
            # Add some randomness to each category for a more natural feel
            positive_percent = min(100, max(0, base_positive + random.randint(-10, 10)))
            negative_percent = 100 - positive_percent
            sentiment_data.append({
                "category": category,
                "positive": positive_percent,
                "negative": negative_percent,
            })
            
        return sentiment_data
    except Exception as e:
        print(f"Error generating sentiment data for {ticker_name}: {e}")
        return []

def generate_credit_trend(ticker_name):
    """
    Generates a historical credit score trend based on actual historical stock data.
    """
    try:
        ticker = yf.Ticker(ticker_name)
        # Fetch 2 years of data to ensure enough history for the 50-day moving average for the last 8 months
        hist = ticker.history(period="2y")

        if hist.empty or len(hist) < 50:
            print(f"Insufficient historical data for {ticker_name}.")
            return []
        
        # FIX: Make the historical data timezone-naive to avoid the "tz-naive and tz-aware" error
        hist = hist.tz_localize(None)

        hist = hist.sort_index()

        # Calculate the 50-day moving average for the entire period
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        
        # NEW: Calculate the daily score for all dates
        hist['Score'] = hist.apply(lambda row: calculate_credit_score(row['Close'], row['MA50']), axis=1)

        # NEW: Apply a rolling mean to the score to create a smoother trend line
        hist['SmoothedScore'] = hist['Score'].rolling(window=30).mean()
        
        # NEW FIX: Resample the data on a monthly basis and get the last valid value for the month
        # This is a much more robust way to get a monthly trend line
        monthly_trend = hist['SmoothedScore'].resample('M').last().dropna()
        
        # We'll get the last 8 months from the resampled data
        trend_data = []
        for month, score in monthly_trend.tail(8).items():
            trend_data.append({
                "month": month.strftime("%b"),
                "score": score,
            })
            
        return trend_data
    except Exception as e:
        print(f"Error generating credit trend for {ticker_name}: {e}")
        return []

def fetch_and_store_data():
    """
    Fetches stock data from yfinance and stores it in MongoDB.
    This function will be called periodically by the scheduler.
    """
    print("Starting scheduled data update...")
    for company_info in COMPANIES:
        ticker_name = company_info["ticker"]
        company_name = company_info["name"]
        
        try:
            # Fetch company info and historical data
            # We use 2y of data to ensure enough history for the trend chart.
            ticker = yf.Ticker(ticker_name)
            info = ticker.info
            hist = ticker.history(period="2y")

            # Calculate credit score and other metrics based on stock data.
            if hist.empty or len(hist) < 50:
                print(f"Insufficient historical data for {company_name} to calculate 50-day moving average.")
                continue

            # FIX: Also make sure the data here is tz-naive for consistency
            hist = hist.tz_localize(None)
            
            ma50 = hist['Close'].rolling(window=50).mean()
            current_close = hist['Close'].iloc[-1]
            score = calculate_credit_score(current_close, ma50.iloc[-1])
            
            # Generate dynamic score factors based on the current score and stock performance
            score_factors = []
            if current_close > ma50.iloc[-1]:
                score_factors.append({"text": "Recent stock price is trending above the 50-day moving average, a sign of positive momentum.", "positive": True})
            else:
                score_factors.append({"text": "Stock price is trading below the 50-day moving average, indicating a potential bearish trend.", "positive": False})
            
            if score >= 85:
                score_factors.append({"text": "Exceptional performance has led to a high credit intelligence score.", "positive": True})
            elif score >= 75:
                score_factors.append({"text": "Solid performance metrics contribute to a good overall score.", "positive": True})
            else:
                score_factors.append({"text": "Recent market volatility has negatively impacted the score.", "positive": False})
                
            # Add a generic factor based on the company's sector
            sector = info.get('sector', 'N/A')
            score_factors.append({"text": f"The company's position in the {sector} sector provides stability.", "positive": True})
            
            # Generate dynamic sentiment and credit trend data
            sentiment_data = generate_sentiment_data(ticker_name)
            credit_trend_data = generate_credit_trend(ticker_name)
            
            # Prepare the data document for MongoDB
            company_data = {
                "name": company_name,
                "ticker": ticker_name,
                "score": score,
                "marketCap": info.get('marketCap', 0),
                "sector": sector,
                "lastUpdated": datetime.utcnow(),
                "sentiment": sentiment_data,
                "creditTrend": credit_trend_data,
                "scoreFactors": score_factors,
            }
            
            # Update or insert the company data in the database
            companies_col.update_one(
                {"ticker": ticker_name},
                {"$set": company_data},
                upsert=True
            )
            print(f"Data for {company_name} updated successfully.")
            
        except Exception as e:
            print(f"Error fetching data for {company_name}: {e}")

# API Endpoints
@app.route("/api/companies", methods=["GET"])
def get_companies():
    """Returns a list of all companies in the database."""
    companies = list(companies_col.find({}, {"name": 1, "_id": 0}))
    return jsonify(companies)

@app.route("/api/companies/<name>", methods=["GET"])
def get_company(name):
    """Returns detailed data for a specific company."""
    company = companies_col.find_one({"name": name}, {"_id": 0})
    if company:
        # Convert datetime object to string for JSON serialization
        company['lastUpdated'] = company['lastUpdated'].strftime("%Y-%m-%d %H:%M:%S UTC")
        return jsonify(company)
    return jsonify({"error": "Company not found"}), 404

# A manual endpoint to trigger the data update for testing purposes
@app.route("/api/update_data", methods=["POST"])
def update_data():
    """Manually triggers the data fetching and storage process."""
    fetch_and_store_data()
    return jsonify({"message": "Data update triggered successfully."}), 200

def scheduled_update():
    """
    A function to run the data update periodically.
    """
    while True:
        fetch_and_store_data()
        # Update every 60 minutes (3600 seconds)
        time.sleep(3600)

if __name__ == "__main__":
    # Start the scheduled data update in a separate thread
    # The daemon=True ensures the thread exits when the main program exits
    update_thread = threading.Thread(target=scheduled_update, daemon=True)
    update_thread.start()
    
    # Run the Flask app
    app.run(debug=True, use_reloader=False)

