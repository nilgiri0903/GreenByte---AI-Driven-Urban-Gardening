
📘 GreenByte – AI-Powered Gardening Assistant 🌱

GreenByte is an intelligent gardening assistant that leverages AI and machine learning to help users with smart crop planning, disease detection, and growth tracking. It is designed to promote efficient farming practices, especially for small-scale and home-based gardeners.

🧩 Features

🌾 Crop Recommendation

Suggests the most suitable crops to grow based on soil, weather, and environmental conditions.

🌿 Crop Relationship Detection

Uses graph-based analysis to understand compatibility and interdependence between crops (e.g., companion planting).

🌱 Plant Disease Detection

Upload an image of a plant, and the system detects diseases using a trained deep learning model.

📈 Growth Tracker Log

Tracks the development and health of plants over time using logs and visual indicators.


🛠️ Tech Stack

Frontend: HTML, CSS, JavaScript

Backend: Python (Flask)

AI/ML:

Plant Disease Detection Model (Trained on image datasets)

Crop Recommendation using rule-based or ML logic

Crop Relationship Detection using NetworkX (graph theory)

Database: MySQL


📁 Project Structure
```bash
GreenByte/
│
├── static/                  # CSS, JS, images
├── templates/               # HTML templates
├── datasets/                # Data files for ML models
├── models/                  # Pretrained models
├── test_images/             # Test images for disease prediction
├── app.py                   # Main Flask app
├── db_connection.py         # Database connection
├── train_model.py           # Model training script
├── predict_disease.py       # Prediction logic
└── README.md                # Project overview
```

🚀 How to Run the Project
1. Clone the repository
```bash
git clone https://github.com/yourusername/GreenByte.git
cd GreenByte
```
2.Install dependencies
```bash
Install the required Dependencies
```

3. Run the Application
```bash
python app.py
```
4.Access it in your browser
```bash
Go to http://127.0.0.1:5000/
```


