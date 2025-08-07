from flask import Flask, render_template, request, redirect, make_response,flash,url_for,session,flash
from db_connection import get_connection
import pandas as pd
import joblib
import numpy as np
import mysql.connector
from xhtml2pdf import pisa
import io
import os
import cv2
from werkzeug.utils import secure_filename
import pickle
import requests
from datetime import datetime
import mysql.connector

app = Flask(__name__)

app.secret_key = 'shruti_super_secret_123'


PLANT_ID_API_KEY = "gcJXmr6Yt5t1Fy33BvL1uFVHMFbHiDHPXgi3x4LuEjKvMWqQ1A"
PLANT_ID_ENDPOINT = "https://plant.id/api/v3"

crop_model = joblib.load('models/crop_rec_model.joblib')
disease_model = joblib.load('models/plant_disease_model.pkl')

care_tips = {
    "rice": "🌾 Needs standing water, fertile soil, and protection from pests like stem borers.",
    "maize": "🌽 Grows best in warm weather. Ensure proper spacing and fertilize with nitrogen.",
    "chickpea": "🌱 Prefers dry climate. Use phosphorus-rich fertilizer and avoid water logging.",
    "banana": "🍌 Requires rich soil and regular watering. Add mulch and check for banana weevils.",
    "mango": "🥭 Needs sunlight and deep watering. Prune branches in summer for better growth.",
    "grapes": "🍇 Requires trellises, pruning, and dry conditions. Watch for powdery mildew.",
    "apple": "🍎 Grows in cold climates. Needs regular pruning and pest protection.",
    "orange": "🍊 Needs full sun. Water deeply and regularly. Use mulch to retain moisture.",
    "tomato": "🍅 Loves sunlight. Use support stakes and protect from aphids and hornworms.",
    "coffee": "☕ Grows in shade. Requires rich soil, frequent watering, and pest control.",
    # Add more crops as needed
}
class_names = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___healthy",
    "Potato___Late_blight",
    "Tomato__Target_Spot",
    "Tomato__Tomato_mosaic_virus",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_healthy",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite"
]

care_tips_disease = {
    "Pepper__bell___Bacterial_spot": "🧪 Apply copper-based fungicide and rotate crops.",
    "Pepper__bell___healthy": "✅ No issues detected. Keep observing.",
    "Potato___Early_blight": "🍂 Remove affected foliage and use protective sprays.",
    "Potato___healthy": "👍 Healthy! Maintain regular watering and inspection.",
    "Potato___Late_blight": "🌧️ Avoid wet leaves, use fungicides before rain.",
    "Tomato__Target_Spot": "🌿 Remove infected leaves and apply chlorothalonil.",
    "Tomato__Tomato_mosaic_virus": "🧼 Sanitize tools, avoid tobacco near plants.",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "🕵️ Control whiteflies and remove infected plants.",
    "Tomato_Bacterial_spot": "🛡️ Use copper sprays and avoid overhead watering.",
    "Tomato_Early_blight": "🍃 Prune lower leaves and rotate crops.",
    "Tomato_healthy": "👌 GreenByte approves! Keep monitoring.",
    "Tomato_Late_blight": "☔ Improve drainage and use protective fungicides.",
    "Tomato_Leaf_Mold": "🌬️ Ventilate greenhouse and reduce humidity.",
    "Tomato_Septoria_leaf_spot": "🧽 Remove debris and apply appropriate fungicide.",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "🔍 Use miticides or neem oil, monitor infestations."
}

# Database connection
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='root',
    database='greenbyte'
)
cursor = conn.cursor(dictionary=True)

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor.execute('SELECT * FROM users WHERE username = %s AND password = %s', (username, password))
        user = cursor.fetchone()

        if user:
            session['user'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials', 'danger')

    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        try:
            cursor.execute(
                'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
                (username, email, password)
            )
            conn.commit()
            flash('Signup successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except:
            flash('Username or email already exists', 'warning')

    return render_template('signup.html')

@app.route('/index')
def index():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('login'))

# ✅ Crop care tips dictionary
care_tips_crop = {
    "rice": "🌾 Needs standing water, fertile soil, and protection from pests like stem borers.",
    "maize": "🌽 Grows best in warm weather. Ensure proper spacing and fertilize with nitrogen.",
    "chickpea": "🌱 Prefers dry climate. Use phosphorus-rich fertilizer and avoid water logging.",
    "banana": "🍌 Requires rich soil and regular watering. Add mulch and check for banana weevils.",
    "mango": "🥭 Needs sunlight and deep watering. Prune branches in summer for better growth.",
    "grapes": "🍇 Requires trellises, pruning, and dry conditions. Watch for powdery mildew.",
    "apple": "🍎 Grows in cold climates. Needs regular pruning and pest protection.",
    "orange": "🍊 Needs full sun. Water deeply and regularly. Use mulch to retain moisture.",
    "tomato": "🍅 Loves sunlight. Use support stakes and protect from aphids and hornworms.",
    "coffee": "☕ Grows in shade. Requires rich soil, frequent watering, and pest control."
}

# 🧠 Recommendation route
@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        N = float(request.form['N'])
        P = float(request.form['P'])
        K = float(request.form['K'])
        temperature = float(request.form['temperature'])
        humidity = float(request.form['humidity'])
        ph = float(request.form['ph'])
        rainfall = float(request.form['rainfall'])

        input_data = np.array([[N, P, K, temperature, humidity, ph, rainfall]])
        prediction = crop_model.predict(input_data)[0]

        # 🌿 Match crop prediction to care tips
        tips = care_tips_crop.get(prediction.lower(), "🪴 No care tips found for this plant.")

        return render_template('recommendations.html', plant=prediction, tips=tips)
    
    return render_template('recommend_form.html')


@app.route('/tracker')
def tracker():
    return redirect('/view_tracker')


@app.route('/add_tracker', methods=['GET', 'POST'])
def add_tracker():
    if request.method == 'POST':
        plant_name = request.form['plant_name']
        date_planted = request.form['date_planted']
        height_cm = request.form.get('height_cm', 0)
        status = request.form['status']
        notes = request.form['notes']

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO growth_tracker (plant_name, date_planted, height_cm, status, notes)
            VALUES (%s, %s, %s, %s, %s)
        """, (plant_name, date_planted, height_cm, status, notes))
        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/view_tracker')
    return render_template('add_tracker.html')


@app.route('/view_tracker')
def view_tracker():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM growth_tracker")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('view_tracker.html', rows=rows)

@app.route('/download_pdf')
def download_pdf():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM growth_tracker")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    rendered = render_template('pdf_template.html', rows=rows)

    pdf = io.BytesIO()
    pisa.CreatePDF(io.StringIO(rendered), dest=pdf)

    response = make_response(pdf.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=plant_growth_report.pdf'
    return response
@app.route('/plant-diary', methods=['GET', 'POST'])
def plant_diary():
    if request.method == 'POST':
        image = request.files['image']
        note = request.form['note']

        if image:
            filename = secure_filename(image.filename)
            filepath = os.path.join('static/uploads/diary_images', filename)
            image.save(filepath)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO plant_diary (image_path, note) VALUES (%s, %s)", (filepath, note))
            conn.commit()
            cursor.close()
            conn.close()
            flash("Diary entry added successfully!", "success")
            return redirect('/plant-diary')

    # Display existing entries
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM plant_diary ORDER BY created_at DESC")
    entries = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('plant_diary.html', entries=entries)

plant_care_tips = {
    'rose': {
        'water': 'Water every 2 days.',
        'sunlight': 'Needs 6 hours of sunlight.',
        'fertilizer': 'Use rose-specific fertilizer once a week.'
    },
    'tulsi': {
        'water': 'Water daily in summer, alternate days in winter.',
        'sunlight': 'Needs direct sunlight.',
        'fertilizer': 'Use organic compost monthly.'
    },
    'money plant': {
        'water': 'Water once the soil is dry.',
        'sunlight': 'Indirect sunlight is best.',
        'fertilizer': 'Use liquid fertilizer once a month.'
    },
    'default': {
        'water': 'Water as needed.',
        'sunlight': 'Provide enough natural light.',
        'fertilizer': 'Use all-purpose plant food occasionally.'
    }
}

@app.route('/care_tips', methods=['GET', 'POST'])
def care_tips():
    plant = None
    message = None
    if request.method == 'POST':
        plant_name = request.form['plant_name'].strip().lower()
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM plants WHERE LOWER(plant_name) = %s", (plant_name,))
        plant = cursor.fetchone()
        cursor.close()
        conn.close()

        if not plant:
            message = "No plant found or missing plant name."

    return render_template('care_tips.html', plant=plant, message=message)


# Load the trained model
# Load trained model and vectorizer
model = joblib.load('models/companion_model.joblib')
vectorizer = joblib.load('models/companion_vectorizer.joblib')

@app.route('/companion', methods=['GET', 'POST'])
def companion():
    if request.method == 'POST':
        source = request.form['source'].lower().strip()
        target = request.form['target'].lower().strip()
        source_type = request.form['type'].lower().strip()

        # Build input string for prediction
        input_text = f"{source} {target} {source_type}"
        input_vec = vectorizer.transform([input_text])

        # Predict relationship
        relation = model.predict(input_vec)[0]

        return render_template('companion_result.html',
                               source=source,
                               target=target,
                               relation=relation)
    return render_template('companion_form.html')




def extract_features(image):
    image = cv2.resize(image, (100, 100))
    hist = cv2.calcHist([image], [0, 1, 2], None, [8, 8, 8],
                        [0, 256, 0, 256, 0, 256])
    return hist.flatten()

@app.route('/predict_disease', methods=['GET', 'POST'])
def predict_disease():
    if request.method == 'POST':
        file = request.files['image']
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join('static/uploads', filename)
            file.save(filepath)

            img = cv2.imread(filepath)
            features = extract_features(img)
            prediction = disease_model.predict([features])[0]
            tip = care_tips_disease.get(prediction, "No care tip available.")

            return render_template('predict_disease.html',
                                   prediction=prediction,
                                   tip=tip,
                                   image_path=filepath)

    return render_template('predict_disease.html')

# 🌾 Rule-Based Crop Suggestion Function
def suggest_crop(temp, humidity, ph, rainfall):
    if temperature > 30 and humidity < 50 and rainfall < 100:
        return "Millet"
    elif temperature < 20 and humidity > 70 and rainfall > 200:
        return "Rice"
    elif 20 <= temperature <= 30 and 50 <= humidity <= 70 and 100 <= rainfall <= 200:
        return "Maize"
    elif ph < 6.0:
        return "Potato"
    elif ph > 7.5:
        return "Barley"
    else:
        return "Wheat"

# 🌦️ Weather API Caller
def get_weather(city, api_key):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        res = requests.get(url)
        res.raise_for_status()  # Raise error for non-200 responses
        data = res.json()

        temperature = data['main']['temperature']
        humidity = data['main']['humidity']
        rainfall = data.get('rain', {}).get('1h', 0) or 0.0  # Handle missing rain data gracefully

        return temperature, humidity, rainfall
    except requests.RequestException as err:
        raise Exception(f"API request failed: {err}")
    except KeyError:
        raise Exception("Unexpected response format from weather API")

# 🌱 Flask Route to Handle Weather-Based Crop Recommendation
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    if request.method == 'POST':
        city = request.form.get('city')
        api_key = 'f633ac265a52b6516bdadde80ed6daf6'  # Replace with your key

        try:
            temperature, humidity, rainfall = get_weather(city, api_key)
            ph = 6.5  # Default value

            # Try rule-based crop suggestion
            crop = suggest_crop(temperature, humidity, ph, rainfall)

            if crop in [None, "Conditions unclear — consider ML model"]:
                # ML fallback
                input_features = [[temperature, humidity, ph, rainfall]]
                predicted_label = crop_model(input_features)
                crop = label_encoder.inverse_transform(predicted_label)[0]

            return render_template('weather_result.html', crop=crop, city=city)

        except Exception as e:
            return render_template('weather_result.html', crop=None, error=str(e), city=city)

    return render_template('weather_form.html')


    return render_template('weather_form.html')



if __name__ == '__main__':
    app.run(debug=True)
