#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import venv
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8 or higher."""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8 or higher is required.")
        sys.exit(1)

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    # Get the directory where the script is located
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    venv_path = script_dir / "venv"
    
    # Check if venv exists and has the correct structure
    if venv_path.exists():
        # Check if the Python executable exists in the expected location
        if platform.system() == "Windows":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        if not python_path.exists():
            print(f"Existing virtual environment at {venv_path} appears to be corrupted.")
            print("Removing it and creating a new one...")
            try:
                shutil.rmtree(venv_path)
            except Exception as e:
                print(f"Error removing virtual environment: {e}")
                print("Please manually delete the 'venv' directory and try again.")
                sys.exit(1)
        else:
            print(f"Virtual environment already exists at {venv_path}")
            return venv_path
    
    # Create a new virtual environment
    print("Creating virtual environment...")
    try:
        venv.create(venv_path, with_pip=True)
        print(f"Virtual environment created at {venv_path}")
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

def get_python_executable():
    """Get the Python executable path for the virtual environment."""
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    if platform.system() == "Windows":
        python_path = script_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_path = script_dir / "venv" / "bin" / "python"
    
    # Check if the executable exists
    if not python_path.exists():
        print(f"Error: Python executable not found at {python_path}")
        print("The virtual environment may not have been created properly.")
        print("Try removing the 'venv' directory and running the installation again.")
        sys.exit(1)
    
    return str(python_path)

def install_dependencies():
    """Install required packages."""
    print("Installing dependencies...")
    try:
        # Get the script directory
        script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        requirements_path = script_dir / "requirements.txt"
        
        # Get the Python executable for the virtual environment
        venv_python = get_python_executable()
        print(f"Using Python at: {venv_python}")
        
        # Upgrade pip first
        subprocess.run([venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True)
        # Install requirements
        subprocess.run([venv_python, "-m", "pip", "install", "-r", str(requirements_path)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: Failed to install dependencies: {e}")
        sys.exit(1)

def create_env_file():
    """Create .env file if it doesn't exist."""
    # Get the script directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    env_path = script_dir / ".env"
    
    if not env_path.exists():
        print("Creating .env file...")
        with open(env_path, "w") as f:
            f.write("OPENAI_API_KEY=your-api-key-here\n")
            f.write("GPT_MODEL=gpt-3.5-turbo\n")
            
            # Set port based on OS
            if platform.system() == "Darwin":  # macOS
                f.write("PORT=5001\n")
                print("Using port 5001 for macOS to avoid AirPlay conflicts")
            else:
                f.write("PORT=5000\n")
                
        print("Please edit .env file and add your OpenAI API key.")

def create_reports_directory():
    """Create reports directory if it doesn't exist."""
    # Get the script directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    reports_path = script_dir / "reports"
    
    if not reports_path.exists():
        print("Creating reports directory...")
        reports_path.mkdir()

def main():
    """Main installation function."""
    print("Starting CTO Signal Scanner installation...")
    
    # Get the script directory
    script_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    print(f"Installation directory: {script_dir}")
    
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
    print(f"1. Navigate to the installation directory: cd {script_dir}")
    print(f"2. Activate the virtual environment: {activate_cmd}")
    print("3. Edit the .env file and add your OpenAI API key")
    print("4. Start the application: python run_web.py")
    if platform.system() == "Darwin":  # macOS
        print("5. Open your browser and go to: http://localhost:5001")
    else:
        print("5. Open your browser and go to: http://localhost:5000")
    print("\nFor more detailed instructions, please refer to the README.md file.")

if __name__ == "__main__":
    main() 