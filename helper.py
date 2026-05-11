import subprocess


def run_command(command: str):
    result = subprocess.run(
        command,
        shell=True,
        text=True,
        capture_output=True
    )

    print(result.stdout)

    if result.stderr:
        print(result.stderr)
