#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

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
        venv.create(venv_path, with_pip=True)
    return venv_path

def get_activate_script():
    """Get the appropriate activation script based on the OS."""
    if platform.system() == "Windows":
        return "venv\\Scripts\\activate"
    return "source venv/bin/activate"

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_path = Path(".env")
    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write("OPENAI_API_KEY=your-api-key-here\n")
            f.write("GPT_MODEL=gpt-3.5-turbo\n")
        print("Please edit .env file and add your OpenAI API key.")

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
    create_env_file()
    create_reports_directory()
    
    # Install dependencies
    install_dependencies()
    
    print("\nInstallation complete! 🎉")
    print("\nTo start using the application:")
    print(f"1. Activate the virtual environment: {activate_cmd}")
    print("2. Edit the .env file and add your OpenAI API key")
    print("3. Start the application: python run_web.py")
    print("4. Open your browser and go to: http://localhost:5000")
    print("\nFor more detailed instructions, please refer to the README.md file.")

if __name__ == "__main__":
    main() 