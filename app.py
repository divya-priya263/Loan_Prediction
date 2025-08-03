from flask import Flask, render_template, request, redirect, url_for, flash
import pickle
import numpy as np
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Load the model and scaler
with open('model.pkl', 'rb') as f:
    classifier = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

# Define a model for storing predictions
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    gender = db.Column(db.String(10))
    married = db.Column(db.String(10))
    dependents = db.Column(db.Integer)
    education = db.Column(db.String(10))
    self_employed = db.Column(db.String(10))
    applicant_income = db.Column(db.Float)
    coapplicant_income = db.Column(db.Float)
    loan_amount = db.Column(db.Float)
    loan_amount_term = db.Column(db.Float)
    credit_history = db.Column(db.Float)
    property_area = db.Column(db.String(20))
    status = db.Column(db.String(10))

# Create the database
with app.app_context():
    db.create_all()

@app.route('/')
def project():
    return render_template('project.html')

@app.route('/a', methods=['GET', 'POST'])
def a():
    if request.method == 'POST':
        try:
            # Collect form data
            Gender = request.form['gender'].lower()
            Gender = 1 if Gender == 'male' else 0

            Married = request.form['married'].lower()
            Married = 1 if Married == 'married' else 0

            Dependents = request.form['dependents']
            Dependents = 4 if Dependents == '3+' else int(Dependents)

            Education = request.form['education'].lower()
            Education = 1 if Education == 'graduate' else 0

            Self_Employed = request.form['self_employed'].lower()
            Self_Employed = 1 if Self_Employed == 'yes' else 0

            ApplicantIncome = float(request.form['applicant_income'])
            CoapplicantIncome = float(request.form['coapplicant_income'])
            LoanAmount = float(request.form['loan_amount'])
            Loan_Amount_Term = float(request.form['loan_amount_term'])
            Credit_History = float(request.form['credit_history'])

            Property_Area = request.form['property_area'].lower()
            Property_Area = 0 if Property_Area == 'rural' else 1 if Property_Area == 'semiurban' else 2

            # Create numpy array for input data
            input_data = np.array([[Gender, Married, Dependents, Education, Self_Employed, 
                                    ApplicantIncome, CoapplicantIncome, LoanAmount, Loan_Amount_Term, 
                                    Credit_History, Property_Area]])

            # Optional: Scale input data if scaler is used
            input_data_scaled = scaler.transform(input_data)

            # Predict loan status
            prediction = classifier.predict(input_data_scaled)
            print(f"Input Data: {input_data_scaled}, Prediction: {prediction}")

            prediction_text = 'You are eligible for loan' if prediction[0] == 1 else 'You are not eligible for loan'

            # Store the data in the database
            new_prediction = Prediction(
                gender=request.form['gender'],
                married=request.form['married'],
                dependents=Dependents,
                education=request.form['education'],
                self_employed=request.form['self_employed'],
                applicant_income=ApplicantIncome,
                coapplicant_income=CoapplicantIncome,
                loan_amount=LoanAmount,
                loan_amount_term=Loan_Amount_Term,
                credit_history=Credit_History,
                property_area=request.form['property_area'],
                status=prediction_text
            )
            db.session.add(new_prediction)
            db.session.commit()

            return render_template('a.html', prediction_text=prediction_text)
        except Exception as e:
            flash(f"An error occurred: {e}")
            return redirect(url_for('a'))

    return render_template('a.html')

@app.route('/lgs', methods=['GET', 'POST'])
def lgs():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Add your logic to validate the username and password here
        valid_username = 'testuser'
        valid_password = 'testpassword'

        if username == 'validuser' and password == 'validpassword':  # Example validation
            return redirect(url_for('project'))
        else:
            error = 'Successfully Created Accound Redirectering to home page'
            return render_template('project.html', error=error)
    return render_template('lgs.html')

@app.route('/business')
def business():
    return render_template('business.html')

@app.route('/personal')
def personal():
    return render_template('personal.html')

@app.route('/homeloan')
def homeloan():
    return render_template('homeloan.html')

@app.route('/car')
def car():
    return render_template('car.html')

@app.route('/s', methods=['GET', 'POST'])
def s():
    
    return render_template('s.html')

@app.route('/predictions')
def view_predictions():
    predictions = Prediction.query.all()
    return render_template('predictions.html', predictions=predictions)

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Change to any unused port