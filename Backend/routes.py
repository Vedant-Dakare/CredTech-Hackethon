from flask import Blueprint, jsonify, request
from models import Company, YahooFinanceAPI
import json
from datetime import datetime

api = Blueprint('api', __name__)

@api.route('/companies', methods=['GET'])
def get_companies():
    """Get all companies from database"""
    companies = Company.get_all()
    return jsonify(companies)

@api.route('/companies/<name>', methods=['GET'])
def get_company(name):
    """Get specific company details"""
    company = Company.get_by_name(name)
    if company:
        return jsonify(company)
    return jsonify({'error': 'Company not found'}), 404

@api.route('/companies', methods=['POST'])
def create_company():
    """Create a new company entry"""
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Name is required'}), 400
    
    Company.create(data)
    return jsonify({'message': 'Company created successfully'}), 201

@api.route('/yahoo/<symbol>/info', methods=['GET'])
def get_yahoo_info(symbol):
    """Get company info from Yahoo Finance"""
    info = YahooFinanceAPI.get_company_info(symbol)
    return jsonify(info)

@api.route('/yahoo/<symbol>/data', methods=['GET'])
def get_yahoo_data(symbol):
    """Get stock data from Yahoo Finance"""
    period = request.args.get('period', '1y')
    data = YahooFinanceAPI.get_stock_data(symbol, period)
    return jsonify(data)

@api.route('/companies/<name>/sync', methods=['POST'])
def sync_company_data(name):
    """Sync company data with Yahoo Finance"""
    company = Company.get_by_name(name)
    if not company:
        return jsonify({'error': 'Company not found'}), 404
    
    symbol = company.get('symbol')
    if not symbol:
        return jsonify({'error': 'No symbol provided for company'}), 400
    
    # Get fresh data from Yahoo
    yahoo_info = YahooFinanceAPI.get_company_info(symbol)
    yahoo_data = YahooFinanceAPI.get_stock_data(symbol)
    
    if 'error' in yahoo_info or 'error' in yahoo_data:
        return jsonify({'error': 'Failed to fetch data from Yahoo Finance'}), 500
    
    # Update company with fresh data
    update_data = {
        'market_cap': yahoo_info.get('market_cap', 0),
        'sector': yahoo_info.get('sector', 'Unknown'),
        'current_price': yahoo_data.get('current_price', 0),
        'pe_ratio': yahoo_data.get('pe_ratio', 0),
        'beta': yahoo_data.get('beta', 1),
        'historical_data': yahoo_data.get('historical_data', [])
    }
    
    Company.update(name, update_data)
    
    return jsonify({
        'message': 'Company data synced successfully',
        'data': update_data
    })

@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
