from PyQt6.QtWidgets import (QApplication)
import sys
import os
import subprocess
from movrs_client.GlassMorphicLogin import GlassMorphicLogin
from movrs_client.movrs_apis import update_json_fields

def main():
    # Determine the base directory of the installed package
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    setup_complete_flag = os.path.join(BASE_DIR, ".setup_complete")

    if not os.path.exists(setup_complete_flag):
        script_path = os.path.join(BASE_DIR, "setup_nvidia_docker.sh")
        if os.path.exists(script_path):
            try:
                # Make the script executable
                subprocess.run(["sudo", "chmod", "+x", script_path], check=True)
                # Run the script
                subprocess.run(["sudo", script_path], check=True)
                # Create the flag file to indicate setup is complete
                with open(setup_complete_flag, "w") as f:
                    f.write("NVIDIA Docker setup complete.")
            except subprocess.CalledProcessError as e:
                print(f"Error during NVIDIA Docker setup: {e}")
                # Decide if you want to exit or continue if setup fails
                # For now, we'll print the error and continue
            except IOError as e:
                print(f"Error creating setup flag file: {e}")

    update_json_fields([['state', '']])
    app = QApplication(sys.argv)
    window = GlassMorphicLogin()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
