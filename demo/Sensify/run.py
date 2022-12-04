import os
from app import create_app

app = create_app()

production = os.environ.get("PRODUCTION", False)

if __name__ == '__main__':
    # app.run()
    if production:
        app.run(debug=True)
    else:
        app.run(host='0.0.0.0', port=8002, debug=True)
