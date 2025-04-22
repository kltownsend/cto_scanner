#!/bin/bash

# Color output functions
print_message() {
    echo -e "\033[1;34m$1\033[0m"
}

print_success() {
    echo -e "\033[1;32m$1\033[0m"
}

print_error() {
    echo -e "\033[1;31m$1\033[0m"
}

# Check Python version
check_python_version() {
    if command -v python3 >/dev/null 2>&1; then
        python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if (( $(echo "$python_version >= 3.8" | bc -l) )); then
            print_success "Python $python_version found ✓"
            return 0
        fi
    fi
    print_error "Error: Python 3.8 or higher is required"
    return 1
}

# Find available port
find_available_port() {
    # Try preferred ports first
    local preferred_ports=(5001 5000 8000 8080 3000)
    
    print_message "Checking for available ports..."
    for port in "${preferred_ports[@]}"; do
        if ! lsof -i ":$port" > /dev/null 2>&1; then
            echo "$port"
            return 0
        fi
        print_message "Port $port is in use, trying next port..."
    done
    
    # Try range of ports if preferred ones are not available
    for port in {8081..8100}; do
        if ! lsof -i ":$port" > /dev/null 2>&1; then
            echo "$port"
            return 0
        fi
    done
    
    echo "5001"  # fallback port
}

# Create or update .env file
create_env_file() {
    print_message "Detecting available port..."
    PORT=$(find_available_port)
    print_message "Using port $PORT"
    
    cat > .env << EOF
OPENAI_API_KEY=your-api-key-here
GPT_MODEL=gpt-3.5-turbo
PORT=$PORT
EOF
    print_success "Configuration file created with port $PORT"
}

# Main installation process
main() {
    print_message "Starting CTO Signal Scanner installation..."

    # Check Python version
    check_python_version || exit 1

    # Create virtual environment
    print_message "Creating virtual environment..."
    python3 -m venv venv

    # Activate virtual environment
    print_message "Activating virtual environment..."
    source venv/bin/activate

    # Install dependencies
    print_message "Installing dependencies..."
    pip install -r requirements.txt

    # Create configuration
    create_env_file

    # Create reports directory
    print_message "Creating reports directory..."
    mkdir -p reports

    print_success "\nInstallation complete! 🎉"
    echo -e "\nTo start using the application:"
    echo "1. Activate the virtual environment:"
    echo "   source venv/bin/activate"
    echo -e "\n2. Edit the .env file and add your OpenAI API key"
    echo -e "\n3. Start the application:"
    echo "   python run_web.py"
    echo -e "\n4. Open your browser and go to: http://localhost:\${PORT} (check .env file for port number)"
    echo -e "\nFor more detailed instructions, please refer to the README.md file."
}

main 