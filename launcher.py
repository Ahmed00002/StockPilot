# launcher.py
import sys
import subprocess
from pathlib import Path

def launch() -> None:
    """Wrapper script to configure environment variables and execute main.py safely."""
    base_dir = Path(__file__).parent.resolve()
    main_script = base_dir / "main.py"
    
    if not main_script.exists():
        print(f"Error: Could not find entry script at {main_script}")
        sys.exit(1)
        
    try:
        print("Launching StockPilot AI...")
        subprocess.run([sys.executable, str(main_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Application terminated with code {e.returncode}")
    except KeyboardInterrupt:
        print("\nApplication interrupted by user.")

if __name__ == "__main__":
    launch()