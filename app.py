from flask import Flask, request, jsonify
import mysql.connector
from joblib import load
from flask_cors import CORS

app = Flask(__name__)
CORS(app)# Add this line to enable CORS for your Flask app

# Connect to MySQL database
db = mysql.connector.connect(
    host="us-cluster-east-01.k8s.cleardb.net",
    port="3306",
    user="b2a95cc800eb0c",
    password="ab9a770b",
    database="heroku_dabded5d9a5f04a"
)

""" # Connect to MySQL database
db = mysql.connector.connect(
    host="127.0.0.1",
    port="3306",
    user="root",
    password="admin",
    database="ehospital"
) """

# Load the trained ML model
with open('stroke.pkl', 'rb') as model_file:
    model = load(model_file)

@app.route('/')
def landing_page():
    return 'Backend is running'

@app.route('/insert_patient', methods=['POST'])
def insert_patient():
    # Get data from request
    data = request.json
    
    # Extract values from data
    id = data.get('id')
    gender = data.get('gender')
    age = data.get('age')
    hypertension = data.get('hypertension')
    heart_disease = data.get('heart_disease')
    ever_married = data.get('ever_married')
    work_type = data.get('work_type')
    Residence_type = data.get('Residence_type')
    avg_glucose_level = data.get('avg_glucose_level')
    bmi = data.get('bmi')
    smoking_status = data.get('smoking_status')
    stroke = data.get('stroke')
    
    # Insert data into MySQL table
    cursor = db.cursor()
    query = "INSERT INTO patient (id, gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status, stroke) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    values = (id, gender, age, hypertension, heart_disease, ever_married, work_type, Residence_type, avg_glucose_level, bmi, smoking_status, stroke)
    cursor.execute(query, values)
    db.commit()
    
    # Close cursor and return response
    cursor.close()
    return jsonify({'message': 'Patient data inserted successfully'}), 201

@app.route('/predict_stroke', methods=['POST'])
def predict_stroke():
    # Get data from request
    data = request.json
    
    # Extract values from data
    id = data.get('id')
    
    # Retrieve patient information from the database
    cursor = db.cursor()
    query = "SELECT * FROM patient WHERE id = %s"
    cursor.execute(query, (id,))
    patient_data = cursor.fetchone()
    cursor.close()
    
    if not patient_data:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Prepare input features for prediction
    features = [
        1 if patient_data[1] == 'Female' else 0, #gender
        1 if patient_data[1] == 'Male' else 0, #gender
        1 if patient_data[1] == 'Other' else 0, #gender
        1 if patient_data[10] == 'formerly smoked' else 0,  # smoking_status_formerly_smoked
        1 if patient_data[10] == 'never smoked' else 0,  # smoking_status_never_smoked
        1 if patient_data[10] == 'smokes' else 0,  # smoking_status_smokes
        1 if patient_data[10] == 'Unknown' else 0,  # smoking_status_Unknown
        1 if patient_data[6] == 'children' else 0,  # work_type_children
        1 if patient_data[6] == 'Govt_job' else 0,  # work_type_Govt_job
        1 if patient_data[6] == 'Never_worked' else 0,  # work_type_Never_worked
        1 if patient_data[6] == 'Private' else 0,  # work_type_Private
        1 if patient_data[6] == 'Self-employed' else 0,  # work_type_Self-employed
        patient_data[2],  # age
        1 if patient_data[3] else 0,  # hypertension
        1 if patient_data[4] else 0,  # heart_disease
        1 if patient_data[5] == 'Yes' else 0,  # ever_married
        1 if patient_data[7] == 'Urban' else 0,  # Residence_type_Urban
        patient_data[8],  # avg_glucose_level
        patient_data[9]  # bmi 
        ]
    
    # Make prediction using the ML model
    prediction = model.predict([features])[0]
    
    return jsonify({'stroke_prediction': bool(prediction)})

if __name__ == '__main__':
    app.run(debug=True)


