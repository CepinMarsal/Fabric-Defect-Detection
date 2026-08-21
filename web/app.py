"""
Flask Backend - Computer Vision Project
Menjalankan website Computer Vision untuk Tugas Akhir.
"""

import cv2
import numpy as np
import base64
from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    """Halaman utama website."""
    return render_template("index.html")


# Load YOLO model
from ultralytics import YOLO
import os

model_path = "c:/COMVIS/F/runs/exp7/weights/best.pt"
if os.path.exists(model_path):
    model = YOLO(model_path)
else:
    model = None
    print(f"Model not found at {model_path}")

# --- Tambahkan route untuk Computer Vision processing di sini ---
@app.route("/api/process", methods=["POST"])
def process_frame():
    try:
        from flask import request, jsonify
        data = request.json
        if not data or 'image' not in data:
            return jsonify({'error': 'No image provided'}), 400
        
        # Ambil base64 string, hilangkan prefix 'data:image/jpeg;base64,'
        img_data = data['image'].split(',')[1]
        
        # Decode base64 ke numpy array
        nparr = np.frombuffer(base64.b64decode(img_data), np.uint8)
        
        # Decode image
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # --- PROSES COMPUTER VISION DENGAN YOLO ---
        if model is not None:
            # Lakukan inferensi (verbose=False agar log tidak spam)
            results = model(frame, conf=0.25, verbose=False)
            
            # Buat kotak deteksi (plot) ke dalam gambar
            result_frame = results[0].plot()
        else:
            result_frame = frame
        
        # Encode kembali ke base64
        _, buffer = cv2.imencode('.jpg', result_frame)
        result_base64 = base64.b64encode(buffer).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image': 'data:image/jpeg;base64,' + result_base64
        })
    except Exception as e:
        print("Error processing frame:", str(e))
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
