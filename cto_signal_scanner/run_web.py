from cto_signal_scanner.web.app import app, PORT
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    print(f"Starting server on port {PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=True) 