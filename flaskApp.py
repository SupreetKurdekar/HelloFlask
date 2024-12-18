from flask import Flask
import os
import openai
from views import my_view


# app creation
app = Flask(__name__)
app.register_blueprint(my_view)

# page display
if __name__ == "__main__":
    app.run(debug=True)