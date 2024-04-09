from flask import Flask, request, jsonify
import mysql.connector
import joblib
from flask_cors import CORS
#from sklearn.externals import joblib


app = Flask(__name__)
CORS(app) # Add this line to enable CORS for your Flask app


# Load the trained ML model
with open('stroke.pkl', 'rb') as model_file:
    model = joblib.load(model_file)
    #model = joblib.load('stroke.pkl')

@app.route('/')
def landing_page():
    return 'Backend is running'

@app.route('/predict_stroke', methods=['POST'])
def predict_stroke():

    # Get data from request
    data = request.json

    features = [
        1 if data['gender'] == 'Female' else 0,
        1 if data['gender'] == 'Male' else 0,
        1 if data['gender'] == 'Other' else 0,
        1 if data['smoking_status'] == 'formerly smoked' else 0,
        1 if data['smoking_status'] == 'never smoked' else 0,
        1 if data['smoking_status'] == 'smokes' else 0,
        1 if data['smoking_status'] == 'Unknown' else 0,
        1 if data['work_type'] == 'children' else 0,
        1 if data['work_type'] == 'Govt_job' else 0,
        1 if data['work_type'] == 'Never_worked' else 0,
        1 if data['work_type'] == 'Private' else 0,
        1 if data['work_type'] == 'Self-employed' else 0,
        data['age'],
        1 if data['hypertension'] else 0,
        1 if data['heart_disease'] else 0,
        1 if data['ever_married'] == 'Yes' else 0,
        1 if data['Residence_type'] == 'Urban' else 0,
        data['avg_glucose_level'],
        data['bmi']
    ]

    # Make prediction using the ML model
    prediction = model.predict([features])[0]
    
    return jsonify({'stroke_prediction': bool(prediction)})

if __name__ == '__main__':
    app.run(debug=True)


