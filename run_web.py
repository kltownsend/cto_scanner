from cto_signal_scanner.web.app import app
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Get port from environment variable, default to 5001
    port = int(os.getenv('PORT', 5001))
    app.run(debug=True, port=port) 