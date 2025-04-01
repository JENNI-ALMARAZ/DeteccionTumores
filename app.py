from flask import Flask, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import cv2 as cv
import base64
from displayTumor import DisplayTumor
from predictTumor import predictTumor  # Tu función de predicción

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return redirect(request.url)
    
    file = request.files['file']
    
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Convertir la imagen original a base64
        with open(file_path, "rb") as img_file:
            original_img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

        # Cargar la imagen y procesarla
        image = cv.imread(file_path, 1)
        display_tumor = DisplayTumor()
        display_tumor.readImage(image)
        
        # Procesar la imagen para detección de tumor
        display_tumor.displayTumor()

        # Predecir el tumor usando la función predictTumor
        res = predictTumor(image)
        result = "Tumor Detectado" if res > 0.5 else "No hay tumor"
        
        # Obtener la imagen procesada en base64
        img_base64 = display_tumor.get_base64_image()

        return render_template('result.html', result=result, 
                               img_data=img_base64, 
                               original_img_data=original_img_base64)

    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
