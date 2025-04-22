#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import venv
import shutil
from pathlib import Path
import socket

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        try:
            venv.create(venv_path, with_pip=True)
        except Exception as e:
            print(f"Error: Failed to create virtual environment: {e}")
            print("\nPlease ensure python3-venv is installed:")
            if platform.system() == "Darwin":  # macOS
                print("On macOS: brew install python@3.12")
            elif platform.system() == "Linux":
                print("On Ubuntu/Debian: sudo apt-get install python3-venv")
            sys.exit(1)
    return venv_path

def get_activate_script():
    """Get the appropriate activation script based on the OS."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    return "source venv/bin/activate"

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    try:
        # Upgrade pip first
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies: {e}")
        sys.exit(1)

def configure_port():
    """Configure the port based on the operating system and availability"""
    # Define the range of ports to try
    preferred_ports = [8000, 8080, 3000, 5000, 5001]
    
    print("Checking for available ports...")
    for port in preferred_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                print(f"Port {port} is available")
                return port
            except socket.error:
                print(f"Port {port} is in use, trying next port...")
                continue
    
    # If no preferred ports are available, try a range
    for port in range(8081, 8100):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('localhost', port))
                print(f"Found available port: {port}")
                return port
            except socket.error:
                continue
    
    print("Warning: Could not find any common ports, using 8000")
    return 8000  # Final fallback

def update_env_file():
    """Update or create .env file with configuration"""
    port = configure_port()
    env_content = f"""OPENAI_API_KEY=your-api-key-here
GPT_MODEL=gpt-3.5-turbo
PORT={port}
DEFAULT_PORT=8000
"""
    with open('.env', 'w') as f:
        f.write(env_content)
    print(f"Configuration file created with port {port}")

def create_reports_directory():
    """Create reports directory if it doesn't exist."""
    reports_path = Path("reports")
    if not reports_path.exists():
        print("Creating reports directory...")
        reports_path.mkdir()

def main():
    """Main installation function."""
    print("Starting CTO Signal Scanner installation...")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    venv_path = create_virtual_environment()
    
    # Get activation command
    activate_cmd = get_activate_script()
    
    # Create necessary files and directories
    update_env_file()
    create_reports_directory()
    
    # Install dependencies
    install_dependencies()
    
    print("\nInstallation complete! 🎉")
    print("\nTo start using the application:")
    print("1. Activate the virtual environment:")
    if platform.system() == "Windows":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\n2. Edit the .env file and add your OpenAI API key")
    print("\n3. Start the application:")
    print("   python run_web.py")
    print(f"\n4. Open your browser and go to: http://localhost:${{PORT}} (check .env file for port number)")
    print("\nFor more detailed instructions, please refer to the README.md file.")

if __name__ == "__main__":
    main() 