"""
Flask Backend - Computer Vision Project
Menjalankan website Computer Vision untuk Tugas Akhir.
"""

from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    """Halaman utama website."""
    return render_template("index.html")


# --- Tambahkan route untuk Computer Vision processing di sini ---
# Contoh:
# @app.route("/api/process", methods=["POST"])
# def process_frame():
#     # Terima frame dari frontend, lakukan processing, kirim hasil
#     pass


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
