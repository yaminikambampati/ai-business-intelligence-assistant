"""Convenience script to run the application."""
import subprocess
import sys
import os


def run_backend():
    """Run the FastAPI backend."""
    print("Starting FastAPI backend...")
    subprocess.run([sys.executable, "-m", "uvicorn", "backend.main:app", "--reload"])


def run_frontend():
    """Run the Streamlit frontend."""
    print("Starting Streamlit frontend...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "frontend/app.py"])


def run_tests():
    """Run the test suite."""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "-v"])


def load_data():
    """Load CSV data into database."""
    print("Loading CSV data...")
    csv_path = "data/sales.csv"
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at {csv_path}")
        print("Please place your sales.csv file in the data/ directory")
        return
    subprocess.run([sys.executable, "-m", "backend.data_loader", "--csv", csv_path])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run.py [backend|frontend|test|load]")
        print("  backend  - Start FastAPI backend server")
        print("  frontend - Start Streamlit frontend")
        print("  test     - Run automated tests")
        print("  load     - Load CSV data into database")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "backend":
        run_backend()
    elif command == "frontend":
        run_frontend()
    elif command in ["test", "tests"]:
        run_tests()
    elif command == "load":
        load_data()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python run.py [backend|frontend|test|load]")
        sys.exit(1)
