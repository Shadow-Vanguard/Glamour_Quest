# app.py
from flask import Flask, request, render_template
import numpy as np
import cv2
from tensorflow.keras.models import load_model

app = Flask(__name__)
model = load_model('hairstyle_model.h5')

@app.route('/')
def virtual_try():
    return render_template('virtual_try.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file uploaded', 400
    file = request.files['file']
    if file.filename == '':
        return 'No file selected', 400

    # Process the uploaded image
    img = cv2.imdecode(np.fromstring(file.read(), np.uint8), cv2.IMREAD_COLOR)
    img = cv2.resize(img, (150, 150))
    img = img.astype('float32') / 255.0
    img = np.expand_dims(img, axis=0)

    # Predict hairstyles
    predictions = model.predict(img)
    # Get the top hairstyle predictions
    top_indices = np.argsort(predictions[0])[-3:][::-1]  # Top 3 predictions
    return render_template('results.html', predictions=top_indices)

if __name__ == '__main__':
    app.run(debug=True)