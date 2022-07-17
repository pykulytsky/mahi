import subprocess


def main():
    cmd = ["uvicorn", "app.main:app", "--workers", "4", "--host", "0.0.0.0", "--port", "8000"]

    subprocess.run(cmd)
