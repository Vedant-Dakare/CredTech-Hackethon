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
import numpy as np
import requests
import os
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

def format_number(n, is_currency=False):
    """Formats a number for display, as a percentage or in millions/billions."""
    if n is None:
        return "N/A"
    
    if is_currency:
        if abs(n) >= 1e12:
            return f"${n / 1e12:.2f}T"
        if abs(n) >= 1e9:
            return f"${n / 1e9:.2f}B"
        if abs(n) >= 1e6:
            return f"${n / 1e6:.2f}M"
        if abs(n) >= 1e3:
            return f"${n / 1e3:.2f}K"
        return f"${n:.2f}"
    
    if abs(n) >= 1e12:
        return f"{n / 1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"{n / 1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"{n / 1e6:.2f}M"
    if abs(n) >= 1e3:
        return f"{n / 1e3:.2f}K"
    return f"{n:.2f}"

def calculate_credit_score(close_price, ma50):
    """
    Calculates a simplified credit score based on stock price relative to its 50-day moving average.
    """
    # Avoid division by zero
    if ma50 == 0:
        return 70
        
    score = 70 + (close_price - ma50) / ma50 * 100
    return max(0, min(100, score)) # Clamp score between 0 and 100

def analyze_sentiment(text):
    """
    NEW: Performs a basic sentiment analysis on a text string
    by counting positive and negative keywords.
    Returns a score between -1 and 1.
    """
    positive_words = ["positive", "up", "growth", "gain", "strong", "bullish", "increase", "rise", "success", "boost", "soar", "rally"]
    negative_words = ["negative", "down", "loss", "decline", "weak", "bearish", "decrease", "drop", "fall", "struggle", "plunge", "volatile"]
    
    score = 0
    words = text.lower().split()
    for word in words:
        if word in positive_words:
            score += 1
        elif word in negative_words:
            score -= 1
            
    return score

def fetch_news_sentiment(ticker_name):
    """
    NEW: Fetches recent news from the News API and calculates a sentiment score.
    Returns a sentiment score (0-100) based on news headlines.
    """
    api_key = Config.NEWS_API_KEY
    if not api_key:
        print("News API key not found. Skipping news sentiment analysis.")
        return None
        
    url = "https://newsapi.org/v2/everything"
    params = {
        "q": ticker_name,
        "language": "en",
        "sortBy": "relevancy",
        "pageSize": 10, # Fetch the 10 most relevant articles
        "apiKey": api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status() # Raise an exception for bad status codes
        data = response.json()
        articles = data.get('articles', [])
        
        if not articles:
            print(f"No News API articles found for {ticker_name}.")
            return None
            
        total_sentiment_score = 0
        article_count = 0
        for article in articles:
            headline = article.get('title', '')
            # Use the basic sentiment analysis function
            sentiment_score = analyze_sentiment(headline)
            
            # Map the score to a 0-100 scale for consistency
            # score range from -10 to 10
            normalized_score = 50 + (sentiment_score / 10) * 50
            total_sentiment_score += normalized_score
            article_count += 1
            
        if article_count > 0:
            average_sentiment = total_sentiment_score / article_count
            return average_sentiment
        else:
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Error fetching News API news for {ticker_name}: {e}")
        return None

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
    Generates a historical credit score trend based on a weighted
    average of historical stock data and a simulated sentiment score.
    """
    try:
        ticker = yf.Ticker(ticker_name)
        hist = ticker.history(period="2y")
        if hist.empty or len(hist) < 50:
            print(f"Insufficient historical data for {ticker_name}.")
            return []
            
        hist = hist.tz_localize(None).sort_index()

        # Calculate the 50-day moving average for the entire period
        hist['MA50'] = hist['Close'].rolling(window=50).mean()

        # Calculate the base yfinance score
        hist['YFinanceScore'] = hist.apply(
            lambda row: calculate_credit_score(row['Close'], row['MA50']), axis=1)

        # NEW: Simulate a sentiment score based on price movement
        # Simple simulation: If price is above MA, sentiment is positive.
        # This creates a trend that mirrors the stock performance.
        hist['SimulatedSentiment'] = hist.apply(
            lambda row: 80 if row['Close'] > row['MA50'] else 60, axis=1)

        # NEW: Calculate the combined score for each day
        hist['CombinedScore'] = (hist['YFinanceScore'] * 0.7) + (hist['SimulatedSentiment'] * 0.3)

        # Smooth the combined score with a rolling mean
        hist['SmoothedScore'] = hist['CombinedScore'].rolling(window=30).mean()

        # Resample on a monthly basis and get the last valid value for the month
        monthly_trend = hist['SmoothedScore'].resample('M').last().dropna()

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
            ticker = yf.Ticker(ticker_name)
            info = ticker.info
            hist = ticker.history(period="2y")
            
            # Calculate credit score and other metrics based on stock data.
            if hist.empty or len(hist) < 50:
                print(f"Insufficient historical data for {company_name} to calculate 50-day moving average.")
                continue

            hist = hist.tz_localize(None)

            ma50 = hist['Close'].rolling(window=50).mean()
            current_close = hist['Close'].iloc[-1]
            yfinance_score = calculate_credit_score(current_close, ma50.iloc[-1])

            news_sentiment_score = fetch_news_sentiment(ticker_name)
            
            if news_sentiment_score is not None:
                final_score = (yfinance_score * 0.7) + (news_sentiment_score * 0.3)
            else:
                final_score = yfinance_score

            score_factors = []
            if current_close > ma50.iloc[-1]:
                score_factors.append({"text": "Recent stock price is trending above the 50-day moving average, a sign of positive momentum.", "positive": True})
            else:
                score_factors.append({"text": "Stock price is trading below the 50-day moving average, indicating a potential bearish trend.", "positive": False})

            if final_score >= 85:
                score_factors.append({"text": "Exceptional performance has led to a high credit intelligence score.", "positive": True})
            elif final_score >= 75:
                score_factors.append({"text": "Solid performance metrics contribute to a good overall score.", "positive": True})
            else:
                score_factors.append({"text": "Recent market volatility has negatively impacted the score.", "positive": False})
            
            if news_sentiment_score is not None:
                if news_sentiment_score > 70:
                    score_factors.append({"text": "Positive news sentiment from recent articles has boosted the score.", "positive": True})
                elif news_sentiment_score < 50:
                    score_factors.append({"text": "Negative news sentiment from recent articles has impacted the score.", "positive": False})
                else:
                    score_factors.append({"text": "Neutral news sentiment from recent articles contributed to the score.", "positive": True})

            sector = info.get('sector', 'N/A')
            score_factors.append({"text": f"The company's position in the {sector} sector provides stability.", "positive": True})

            revenue = info.get('totalRevenue')
            debt_to_equity = info.get('debtToEquity')
            profit_margin = info.get('profitMargins')
            return_on_equity = info.get('returnOnEquity')

            company_data = {
                "name": company_name,
                "ticker": ticker_name,
                "sector": sector,
                "marketCap": info.get('marketCap'),
                "lastUpdated": datetime.utcnow(),
                "score": final_score,
                "scoreFactors": score_factors,
                "sentiment": generate_sentiment_data(ticker_name),
                "creditTrend": generate_credit_trend(ticker_name),
                "metrics": {
                    "revenue": format_number(revenue, is_currency=True),
                    "debt_to_equity": f"{debt_to_equity:.2f}" if debt_to_equity is not None else "N/A",
                    "profit_margin": f"{profit_margin * 100:.2f}%" if profit_margin is not None else "N/A",
                    "return_on_equity": f"{return_on_equity * 100:.2f}%" if return_on_equity is not None else "N/A",
                }
            }

            companies_col.update_one(
                {"ticker": ticker_name},
                {"$set": company_data},
                upsert=True
            )
            print(f"Successfully updated data for {company_name}")
        
        except Exception as e:
            print(f"Error fetching data for {company_name}: {e}")

# Routes for the Flask API
@app.route('/api/companies', methods=['GET'])
def get_companies():
    companies_list = list(companies_col.find({}, {"_id": 0, "name": 1, "ticker": 1}))
    return jsonify(companies_list)

@app.route('/api/companies/<name>', methods=['GET'])
def get_company_details(name):
    company = companies_col.find_one({"name": name}, {"_id": 0})
    if company:
        if 'lastUpdated' in company and isinstance(company['lastUpdated'], datetime):
            company['lastUpdated'] = company['lastUpdated'].strftime("%B %d, %Y")
        return jsonify(company)
    return jsonify({"error": "Company not found"}), 404

# Run the initial data fetch and schedule future updates
if __name__ == '__main__':
    def start_scheduler():
        while True:
            fetch_and_store_data()
            time.sleep(60 * 60)
            
    scheduler_thread = threading.Thread(target=start_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()
    
    app.run(debug=True, use_reloader=False)