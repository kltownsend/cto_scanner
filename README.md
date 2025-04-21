# CTO Signal Scanner

A web application for scanning and analyzing CTO signals using AI-powered analysis.

## Features

- Web-based interface for easy access
- AI-powered signal analysis
- Report generation
- Cross-platform compatibility (Windows, macOS, Linux)

## Prerequisites

- Python 3.8 or higher
- OpenAI API key

## Installation

### Automatic Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/cto-scanner.git
   cd cto-scanner
   ```

2. Run the installation script:
   - On macOS/Linux:
     ```
     chmod +x install.sh
     ./install.sh
     ```
   - On Windows:
     ```
     python install.py
     ```

   The installation script will:
   - Check your Python version
   - Create a virtual environment
   - Install all required dependencies
   - Set up configuration files
   - Create necessary directories

### Manual Installation

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your OpenAI API key:
   ```
   OPENAI_API_KEY=your-api-key-here
   GPT_MODEL=gpt-3.5-turbo
   PORT=5000  # Use 5001 on macOS to avoid AirPlay conflicts
   ```

## Usage

1. Activate the virtual environment:
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
   - On Windows:
     ```
     venv\Scripts\activate
     ```

2. Start the application:
   ```
   python run_web.py
   ```

3. Open your browser and navigate to:
   - http://localhost:5000 (Windows/Linux)
   - http://localhost:5001 (macOS)

## Project Structure

```
cto_scanner/
├── cto_signal_scanner/     # Main package
│   ├── web/                # Web application
│   ├── analysis/           # Signal analysis modules
│   └── utils/              # Utility functions
├── reports/                # Generated reports
├── venv/                   # Virtual environment
├── .env                    # Environment variables
├── install.py              # Windows installation script
├── install.sh              # Unix installation script
├── requirements.txt        # Python dependencies
└── run_web.py             # Application entry point
```

## Configuration

The application can be configured through the `.env` file:

- `OPENAI_API_KEY`: Your OpenAI API key
- `GPT_MODEL`: The GPT model to use (default: gpt-3.5-turbo)
- `PORT`: The port to run the web server on (default: 5000, use 5001 on macOS)

## Troubleshooting

### Common Issues

1. **Python version error**: Ensure you have Python 3.8 or higher installed.
2. **Virtual environment creation fails**: Install python3-venv:
   - On macOS: `brew install python@3.12`
   - On Ubuntu/Debian: `sudo apt-get install python3-venv`
3. **Port conflicts**: If port 5000 is already in use, change the PORT in the .env file.
4. **Corrupted virtual environment**: If you see an error about the Python executable not being found in the virtual environment, the installation script will automatically remove the corrupted environment and create a new one. If it fails to do so, you can manually delete the 'venv' directory and run the installation script again.

### Installation Issues

If you encounter issues during installation:

1. **Check Python version**: Make sure you have Python 3.8 or higher installed.
2. **Verify python3-venv**: Ensure the python3-venv package is installed on your system.
3. **Clean installation**: If you're having persistent issues, try removing the 'venv' directory and the '.env' file, then run the installation script again.
4. **Manual installation**: If the automatic installation fails, follow the manual installation steps.

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
