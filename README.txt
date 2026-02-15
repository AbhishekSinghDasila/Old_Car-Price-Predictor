# Car Price Predictor Web App 🚗

A beautiful, interactive Flask web application to predict car prices using your ML model.

## Project Structure
```
car-price-predictor/
│
├── app.py                      # Flask backend
├── templates/
│   └── index.html             # Frontend HTML/CSS/JS
├── car_price_model.pkl        # Your trained model (add this)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Add Your Model
- Place your trained model file as `car_price_model.pkl` in the same directory as `app.py`
- Make sure your model is saved using pickle

### 3. Run the Application
```bash
python app.py
```

### 4. Open in Browser
Navigate to: `http://localhost:5000`

## Features ✨

- **Beautiful UI**: Modern gradient design with smooth animations
- **Interactive Forms**: Dynamic model selection based on company
- **Real-time Prediction**: Instant price predictions with loading states
- **Responsive Design**: Works on desktop and mobile
- **Error Handling**: User-friendly error messages
- **Indian Currency Format**: Prices displayed in ₹ (Rupees)

## Important Notes 📝

### Before Running:
1. **Update the `predict()` function in `app.py`** to match your model's input features
2. Your model should accept these features (adjust as needed):
   - name (or company + model)
   - company
   - year
   - kms_driven
   - fuel_type

### Example Model Training Code:
```python
import pickle
from sklearn.linear_model import LinearRegression

# Train your model
model = LinearRegression()
model.fit(X_train, y_train)

# Save the model
pickle.dump(model, open('car_price_model.pkl', 'wb'))
```

## Customization Options 🎨

### Add More Companies/Models:
Edit the `COMPANIES` and `CAR_MODELS` dictionaries in `app.py`:

```python
COMPANIES = ['Maruti', 'Hyundai', 'Your_Company']

CAR_MODELS = {
    'Your_Company': ['Model1', 'Model2', 'Model3']
}
```

### Change Colors:
Edit the CSS gradient in `templates/index.html`:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

## Troubleshooting 🔧

**Model not loading?**
- Ensure `car_price_model.pkl` is in the same directory as `app.py`
- Check that the model was saved with Python's pickle module

**Prediction errors?**
- Verify your model's expected input format
- Update the `input_data` DataFrame in the `predict()` function

**Port already in use?**
- Change the port in `app.py`: `app.run(debug=True, port=5001)`

## For Interviews 💼

This project demonstrates:
- ✅ End-to-end ML deployment
- ✅ Flask REST API development
- ✅ Frontend-backend integration
- ✅ Error handling and validation
- ✅ Professional UI/UX design
- ✅ Production-ready code structure

## Next Steps 🚀

1. Deploy on Heroku/AWS/Azure
2. Add model performance metrics
3. Implement data visualization
4. Add user authentication
5. Store predictions in database

Good luck with your interviews! 🎯