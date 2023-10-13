from app import create_app
from logger import init_logging
from flask_cors import CORS


if __name__ == '__main__':
    init_logging()
    app = create_app()
    CORS(app, resources=r"/*")
    app.run(port=6006, debug=False)
