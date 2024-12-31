from flask import Flask
import os

from views import my_view


# app creation
app = Flask(__name__)
app.register_blueprint(my_view)

# Constants
UPLOAD_FOLDER = './PDFDatabase'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# page display
if __name__ == "__main__":
    app.run(debug=True)