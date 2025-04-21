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
if [ ! -d "venv" ]; then
    print_message "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        print_error "Failed to create virtual environment. Please ensure python3-venv is installed."
        print_message "On macOS, you can install it with: brew install python@3.12"
        print_message "On Ubuntu/Debian: sudo apt-get install python3-venv"
        exit 1
    fi
fi

# Activate virtual environment
print_message "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip in the virtual environment
print_message "Upgrading pip..."
python -m pip install --upgrade pip

# Install dependencies
print_message "Installing dependencies..."
python -m pip install -r requirements.txt

# Create necessary directories
print_message "Creating necessary directories..."
mkdir -p reports

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    print_message "Creating .env file..."
    echo "OPENAI_API_KEY=your-api-key-here" > .env
    echo "GPT_MODEL=gpt-3.5-turbo" >> .env
    print_message "Please edit .env file and add your OpenAI API key"
fi

print_success "Installation complete! 🎉"
echo ""
echo "To start using the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Edit the .env file and add your OpenAI API key"
echo "3. Start the application: python run_web.py"
echo "4. Open your browser and go to: http://localhost:5000"
echo ""
echo "For more detailed instructions, please refer to the README.md file." 