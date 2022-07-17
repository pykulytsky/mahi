import subprocess


def main():
    cmd = ["uvicorn", "app.main:app", "--reload"]
    subprocess.run(cmd)
