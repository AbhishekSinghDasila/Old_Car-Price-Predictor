from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import numpy as np
import json

app = Flask(__name__)

# Load the trained model
try:
    model = pickle.load(open('car_price_model.pkl', 'rb'))
    print("✅ Model loaded successfully!")
    
    # Extract valid categories from the model
    ct = model.named_steps['columntransformer']
    ohe = ct.named_transformers_['onehotencoder']
    
    valid_names = list(ohe.categories_[0])
    valid_companies = list(ohe.categories_[1])
    valid_fuels = list(ohe.categories_[2])
    
    # Create company to models mapping
    CAR_MODELS = {}
    for name in valid_names:
        parts = name.split(' ', 1)
        if len(parts) >= 2:
            company = parts[0]
            model_name = parts[1]
            if company not in CAR_MODELS:
                CAR_MODELS[company] = []
            if model_name not in CAR_MODELS[company]:
                CAR_MODELS[company].append(model_name)
    
    COMPANIES = sorted(list(CAR_MODELS.keys()))
    FUEL_TYPES = sorted(valid_fuels)
    
    # Create smart fuel recommendations based on car type
    # EVs, Luxury cars, Budget cars typically have specific fuel types
    FUEL_RECOMMENDATIONS = {
        'default': ['Petrol', 'Diesel', 'CNG'],  # Most common
        'luxury': ['Petrol', 'Diesel'],  # Luxury brands
        'ev_capable': ['Petrol', 'Diesel', 'Electric'],  # Modern brands with EV options
        'budget': ['Petrol', 'CNG'],  # Budget segment
    }
    
    # Map companies to fuel categories
    COMPANY_FUEL_CATEGORY = {
        'Tata': 'ev_capable',
        'MG': 'ev_capable', 
        'Kia': 'ev_capable',
        'Hyundai': 'ev_capable',
        'Mahindra': 'ev_capable',
        'Audi': 'luxury',
        'BMW': 'luxury',
        'Mercedes': 'luxury',
        'Jaguar': 'luxury',
        'Volvo': 'luxury',
        'Maruti': 'default',
        'Honda': 'default',
        'Toyota': 'default',
    }
    
    print(f"✅ Loaded {len(COMPANIES)} companies with {len(valid_names)} car models")
    
except Exception as e:
    print(f"❌ Error loading model: {e}")
    model = None
    COMPANIES = []
    CAR_MODELS = {}
    FUEL_TYPES = ['Petrol', 'Diesel', 'CNG', 'Electric']
    FUEL_RECOMMENDATIONS = {'default': FUEL_TYPES}
    COMPANY_FUEL_CATEGORY = {}

@app.route('/')
def home():
    return render_template('index.html', 
                         companies=COMPANIES, 
                         fuel_types=FUEL_TYPES,
                         car_models=CAR_MODELS)

@app.route('/get_models/<company>')
def get_models(company):
    """API endpoint to get car models for a selected company"""
    models = CAR_MODELS.get(company, [])
    return jsonify(models)

@app.route('/get_fuel_types/<company>')
def get_fuel_types(company):
    """API endpoint to get recommended fuel types for a company"""
    category = COMPANY_FUEL_CATEGORY.get(company, 'default')
    fuels = FUEL_RECOMMENDATIONS.get(category, FUEL_TYPES)
    return jsonify(fuels)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get form data
        data = request.json
        
        company = data.get('company')
        model_name = data.get('model')
        year = int(data.get('year'))
        kms_driven = int(data.get('kms_driven'))
        fuel_type = data.get('fuel_type')
        
        # Create car name exactly as model expects (Company + space + Model)
        car_name = f"{company} {model_name}"
        
        if model is None:
            return jsonify({
                'success': False,
                'error': 'Model not loaded. Please add car_price_model.pkl file.'
            })
        
        # Prepare input exactly as model was trained
        input_data = pd.DataFrame({
            'name': [car_name],
            'company': [company],
            'year': [year],
            'kms_driven': [kms_driven],
            'fuel_type': [fuel_type]
        })
        
        # Try prediction - if it fails due to unknown category, provide helpful error
        try:
            prediction = model.predict(input_data)[0]
        except ValueError as ve:
            # This means the combination doesn't exist in training data
            if "unknown categor" in str(ve).lower():
                return jsonify({
                    'success': False,
                    'error': f'This combination ({car_name} with {fuel_type}) was not in the training data. Please try a different fuel type for this model.'
                })
            else:
                raise ve
        
        # ===== FIX: Intelligent Price Adjustment =====
        # The model has issues with year/kms coefficients
        # Apply realistic depreciation and mileage adjustments
        
        current_year = 2026
        car_age = current_year - year
        
        # Base prediction from model
        base_price = prediction
        
        # Depreciation: 8% per year (realistic for cars)
        depreciation_factor = (1 - 0.08) ** car_age
        
        # Mileage adjustment: -0.5% per 10,000 kms (realistic)
        km_factor = 1 - (kms_driven / 10000) * 0.005
        km_factor = max(km_factor, 0.5)  # Don't reduce more than 50%
        
        # Apply adjustments
        adjusted_price = base_price * depreciation_factor * km_factor
        
        # Ensure minimum price (cars rarely sell below 50k)
        adjusted_price = max(adjusted_price, 50000)
        
        # Format price in Indian rupees (lakhs)
        price_in_lakhs = adjusted_price / 100000
        
        if price_in_lakhs >= 1:
            price_formatted = f"₹ {price_in_lakhs:.2f} Lakhs"
        else:
            price_formatted = f"₹ {adjusted_price:,.0f}"
        
        return jsonify({
            'success': True,
            'predicted_price': price_formatted,
            'price_value': float(adjusted_price),
            'price_lakhs': float(price_in_lakhs),
            'car_details': {
                'name': car_name,
                'year': year,
                'age': f"{car_age} years old",
                'kms': f"{kms_driven:,} km",
                'fuel': fuel_type
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Prediction error: {str(e)}'
        })

if __name__ == '__main__':
    app.run(debug=True, port=5000)