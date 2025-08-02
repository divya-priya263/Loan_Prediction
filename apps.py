from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy

import pickle
import re
import os
import matplotlib.pyplot as plt
from werkzeug.utils import secure_filename
import numpy as np
import sqlite3
from io import BytesIO
import base64

app = Flask(__name__)
app.secret_key = 'your_unique_secret_key'

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///predictions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Initialize Bcrypt


# Load the model and scaler
with open('model.pkl', 'rb') as f:
    classifier = pickle.load(f)

with open('scaler.pkl', 'rb') as f:
    scaler = pickle.load(f)

def init_db():
    with sqlite3.connect("volunteer.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS volunteers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL
        )''')
        conn.commit()

init_db()

@app.route('/', methods=['GET', 'POST'])
def donate():
    if request.method == 'POST':
        # Get form data
        name = request.form.get('myname1')
        email = request.form.get('myemail')
        phone = request.form.get('myphone')
        address = request.form.get('myadd')
        category = request.form.get('myfood')
        quantity = request.form.get('quantity')
        food_date = request.form.get('fooddate')
        note = request.form.get('note')

        # Save the donation data to the database
        with sqlite3.connect("donations.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS donations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                name TEXT NOT NULL,
                                email TEXT NOT NULL,
                                phone TEXT NOT NULL,
                                address TEXT NOT NULL,
                                category TEXT NOT NULL,
                                quantity INTEGER NOT NULL,
                                food_date TEXT NOT NULL,
                                note TEXT
                            )''')
            cursor.execute("INSERT INTO donations (name, email, phone, address, category, quantity, food_date, note) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (name, email, phone, address, category, quantity, food_date, note))
            conn.commit()

        # Show a flash message after submission
        flash(f'Thank you {name} for your donation of {quantity} kg in the {category} category!')

        # Redirect to the donations page to show the updated list
        return redirect(url_for('donations'))  # Ensure redirect is returning a valid response

    return render_template('donate.html')  # Ensure rendering the form when it's a GET request


@app.route('/donations')
def donations():
    # Connect to the database and fetch donations
    with sqlite3.connect("donations.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM donations")
        donations = cursor.fetchall()

    # Pass the donations data to the template
    return render_template('donate.html', donations=donations)

def init_graph_db():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        # Check if the table exists
        cursor.execute('''CREATE TABLE IF NOT EXISTS food_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_food_wasted REAL,
            food_donated REAL,
            waste_per_meal REAL,
            wastage_reduction_goal REAL,
            total_meals_served REAL,
            food_recycled REAL,
            date TEXT NOT NULL
        )''')
        conn.commit()
        
        # Check if the date column exists, if not, add it
        cursor.execute("PRAGMA table_info(food_data);")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'date' not in columns:
            cursor.execute("ALTER TABLE food_data ADD COLUMN date TEXT NOT NULL")
            conn.commit()

def setup_database():
    conn = sqlite3.connect("data.db")
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total_food_wasted REAL NOT NULL,
            food_donated REAL NOT NULL,
            waste_per_meal REAL NOT NULL,
            wastage_reduction_goal REAL NOT NULL,
            total_meals_served REAL NOT NULL,
            food_recycled REAL NOT NULL,
            date TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    latest_graph_url = None
    comparison_graph_url = None

    if request.method == 'POST':
        # Retrieve form data
        total_food_wasted = float(request.form['total_food_wasted'])
        food_donated = float(request.form['food_donated'])
        waste_per_meal = float(request.form['waste_per_meal'])
        wastage_reduction_goal = float(request.form['wastage_reduction_goal'])
        total_meals_served = int(request.form['total_meals_served'])
        food_recycled = float(request.form['food_recycled'])
        date = request.form['date']

        # Save data to SQLite database
        with sqlite3.connect("data.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS food_data (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                total_food_wasted REAL,
                                food_donated REAL,
                                waste_per_meal REAL,
                                wastage_reduction_goal REAL,
                                total_meals_served INTEGER,
                                food_recycled REAL,
                                date TEXT)''')
            cursor.execute('''INSERT INTO food_data (
                                total_food_wasted,
                                food_donated,
                                waste_per_meal,
                                wastage_reduction_goal,
                                total_meals_served,
                                food_recycled,
                                date)
                                VALUES (?, ?, ?, ?, ?, ?, ?)''', 
                                (total_food_wasted, food_donated, waste_per_meal,
                                wastage_reduction_goal, total_meals_served,
                                food_recycled, date))
            conn.commit()

        # Generate the latest graph
        labels = ['Total Food Wasted', 'Food Donated', 'Waste per Meal', 'Reduction Goal', 'Meals Served', 'Food Recycled']
        values = [total_food_wasted, food_donated, waste_per_meal, wastage_reduction_goal, total_meals_served, food_recycled]
        
        plt.figure(figsize=(10, 6))
        plt.bar(labels, values, color=['red', 'green', 'blue', 'purple', 'orange', 'teal'])
        plt.title(f'Food Data for {date}')
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        latest_graph_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

        # Generate a comparison graph (dummy data for previous week)
        previous_week_values = [total_food_wasted * 0.9, food_donated * 0.95, waste_per_meal * 1.1, 
                                wastage_reduction_goal * 0.9, total_meals_served * 0.85, food_recycled * 1.2]
        
        plt.figure(figsize=(10, 6))
        x = range(len(labels))
        plt.bar(x, values, width=0.4, label='This Week', align='center')
        plt.bar([p + 0.4 for p in x], previous_week_values, width=0.4, label='Last Week', align='center')
        plt.xticks([p + 0.2 for p in x], labels)
        plt.title('Comparison with Previous Week')
        plt.legend()
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        comparison_graph_url = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        plt.close()

    return render_template(
        'admin_dashboard.html',
        latest_graph_url=f"data:image/png;base64,{latest_graph_url}" if latest_graph_url else None,
        comparison_graph_url=f"data:image/png;base64,{comparison_graph_url}" if comparison_graph_url else None
    )



# Route to handle volunteer details submission
@app.route('/volunteer_details', methods=['GET', 'POST'])
def volunteer_details():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        address = request.form.get('address')
        
        if name and email and phone and address:  # Ensure all fields are filled
            try:
                # Insert data into the database
                with sqlite3.connect("volunteer.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("INSERT INTO volunteers (name, email, phone, address) VALUES (?, ?, ?, ?)", 
                                   (name, email, phone, address))
                    conn.commit()

                flash('Volunteer details submitted successfully.')
                return redirect(url_for('volunteers'))  # Redirect to volunteers list
            except Exception as e:
                flash(f"An error occurred: {str(e)}")
                return redirect(url_for('volunteer_details'))
        else:
            flash('All fields are required!')
            return redirect(url_for('volunteer_details'))

    return render_template('volunteer_details.html')

@app.route('/volunteers')
def volunteers():
    with sqlite3.connect("volunteer.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM volunteers")
        volunteers = cursor.fetchall()
    return render_template('volunteers.html', volunteers=volunteers)

# Additional routes
@app.route('/index')
def index():
    return render_template('index.html')



@app.route('/login')
def login():
    return render_template('login.html')
    
@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/mandet')
def mandet():
    return render_template('mandet.html')

@app.route('/locations')
def locations():
    return render_template('locations.html')

@app.route('/register')
def register():
    return render_template('register.html')




if __name__ == '__main__':
    app.run(debug=True, port=5001)
