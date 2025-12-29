import os
import sys
import subprocess
import shutil
import platform

def get_separator():
    """Get the separator for --add-data argument based on OS."""
    if platform.system() == "Windows":
        return ";"
    return ":"

def build():
    print("Starting build process...")
    
    # Base directory
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base_dir)
    
    icon_name = "icon.png"
    script_name = "main.py"
    app_name = "pdf-manager"
    
    # Check if icon exists
    if not os.path.exists(icon_name):
        print(f"Error: {icon_name} not found in {base_dir}")
        return

    # Construct PyInstaller command
    sep = get_separator()
    cmd = [
        "pyinstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name", app_name,
        "--add-data", f"{icon_name}{sep}.",
        # Add any other resources here, e.g. config.json if you want a default one
        # "--add-data", f"config.json{sep}.", 
    ]
    
    # Platform specific options
    if platform.system() == "Windows":
        # On Windows, PyInstaller prefers .ico, but newer versions often handle it. 
        # For best results, one might convert to .ico, but we'll try passing the png first.
        # If strict .ico is needed, we would add conversion logic here using Pillow.
        cmd.extend(["--icon", icon_name])
    elif platform.system() == "Darwin": # macOS
        cmd.extend(["--icon", icon_name])
        # macOS specific bundle identifier could be added here
        # cmd.extend(["--osx-bundle-identifier", "com.example.pdfmanager"])
    
    cmd.append(script_name)
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        subprocess.check_call(cmd)
        print("\nBuild completed successfully!")
        print(f"Executable can be found in the 'dist' folder: {os.path.join(base_dir, 'dist')}")
    except subprocess.CalledProcessError as e:
        print(f"\nBuild failed with error code {e.returncode}")
    except FileNotFoundError:
        print("\nError: 'pyinstaller' command not found. Please ensure it is installed and in your PATH.")
        print("Try running: pip install pyinstaller")

if __name__ == "__main__":
    build()
