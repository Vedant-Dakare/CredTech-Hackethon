from pymongo import MongoClient
from config import Config
import yfinance as yf
from datetime import datetime

client = MongoClient(Config.MONGO_URI)
db = client.get_default_database()

class Company:
    @staticmethod
    def get_all():
        return list(db.companies.find({}, {'_id': 0}))
    
    @staticmethod
    def get_by_name(name):
        return db.companies.find_one({'name': name}, {'_id': 0})
    
    @staticmethod
    def create(company_data):
        company_data['created_at'] = datetime.utcnow()
        company_data['updated_at'] = datetime.utcnow()
        return db.companies.insert_one(company_data)
    
    @staticmethod
    def update(name, update_data):
        update_data['updated_at'] = datetime.utcnow()
        return db.companies.update_one({'name': name}, {'$set': update_data})

class YahooFinanceAPI:
    @staticmethod
    def get_stock_data(symbol, period='1y'):
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            info = ticker.info
            
            return {
                'symbol': symbol,
                'current_price': info.get('currentPrice', 0),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1),
                'volume': info.get('volume', 0),
                'historical_data': [
                    {
                        'date': date.strftime('%Y-%m-%d'),
                        'close': float(row['Close']),
                        'volume': int(row['Volume'])
                    }
                    for date, row in hist.iterrows()
                ][-30:]
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_company_info(symbol):
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),
                'description': info.get('longBusinessSummary', ''),
                'employees': info.get('fullTimeEmployees', 0),
                'website': info.get('website', ''),
                'country': info.get('country', ''),
                'market_cap': info.get('marketCap', 0),
                'enterprise_value': info.get('enterpriseValue', 0),
                'revenue': info.get('totalRevenue', 0),
                'profit_margin': info.get('profitMargins', 0),
                'debt_to_equity': info.get('debtToEquity', 0),
                'current_ratio': info.get('currentRatio', 0),
                'return_on_equity': info.get('returnOnEquity', 0)
            }
        except Exception as e:
            return {'error': str(e)}
