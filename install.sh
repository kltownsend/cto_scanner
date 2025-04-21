#!/bin/bash

# Print colorful messages
print_message() {
    echo -e "\033[1;34m==>\033[0m $1"
}

print_error() {
    echo -e "\033[1;31mError:\033[0m $1"
}

print_success() {
    echo -e "\033[1;32mSuccess:\033[0m $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
print_message "Installation directory: $SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    print_error "Python 3.8 or higher is required. Found version $python_version"
    exit 1
fi

print_message "Starting installation..."

# Create virtual environment if it doesn't exist
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    print_message "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/venv"
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment. Please ensure python3-venv is installed."
        print_message "On macOS, you can install it with: brew install python@3.12"
        print_message "On Ubuntu/Debian: sudo apt-get install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

# Upgrade pip in the virtual environment
print_message "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
print_message "Installing dependencies..."
python -m pip install -r "$SCRIPT_DIR/requirements.txt"

# Create necessary directories
print_message "Creating necessary directories..."
mkdir -p "$SCRIPT_DIR/reports"

# Create .env file if it doesn't exist
if [ ! -f "$SCRIPT_DIR/.env" ]; then
    print_message "Creating .env file..."
    echo "OPENAI_API_KEY=your-api-key-here" > "$SCRIPT_DIR/.env"
    echo "GPT_MODEL=gpt-3.5-turbo" >> "$SCRIPT_DIR/.env"
    
    # Set port based on OS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "PORT=5001" >> "$SCRIPT_DIR/.env"
        print_message "Using port 5001 for macOS to avoid AirPlay conflicts"
    else
        echo "PORT=5000" >> "$SCRIPT_DIR/.env"
    fi
    
    print_message "Please edit .env file and add your OpenAI API key"
fi

print_success "Installation complete! 🎉"
echo ""
echo "To start using the application:"
echo "1. Navigate to the installation directory: cd $SCRIPT_DIR"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Edit the .env file and add your OpenAI API key"
echo "4. Start the application: python run_web.py"
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "5. Open your browser and go to: http://localhost:5001"
else
    echo "5. Open your browser and go to: http://localhost:5000"
fi
echo ""
echo "For more detailed instructions, please refer to the README.md file." 