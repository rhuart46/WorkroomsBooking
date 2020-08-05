from flask import Flask

from api import api


# Create the application with its registered API:
app = Flask(__name__)
api.init_app(app)


# Launch the application when this file is run:
if __name__ == "__main__":
    app.run(debug=True)
