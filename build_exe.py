import PyInstaller.__main__
import os

# Define the entry point
entry_point = "main.py"

# Assets to include
# Format: "source_path;destination_path" for Windows
assets_path = "assets;assets"

# Build configuration
PyInstaller.__main__.run([
    entry_point,
    "--onefile",
    "--windowed", # No console window
    "--name=ClinicManagerPro",
    f"--add-data={assets_path}",
    "--icon=assets/clinic.ico",
    "--clean",
])

print("\n" + "="*50)
print("Build Finished!")
print("The executable is located in the 'dist' folder.")
print("="*50)
