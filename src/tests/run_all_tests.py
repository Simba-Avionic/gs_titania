import os
import subprocess
import sys

FILEPATH = os.path.dirname(__file__)

TESTS_TO_RUN = ['power_test.py', 'air_rate_test.py']

PORT = 'COM5'
BAUD_RATE = 57600

# doesn't work as intended - doesn't print stuff to console until it's finished

def run_python_script(script_path, PORT, BAUD_RATE):
    # Construct the command to run the Python script
    command = [sys.executable, script_path, PORT, BAUD_RATE]

    # Execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

    # Read stdout and stderr line by line
    with process.stdout as stdout, process.stderr as stderr:
        for stdout_line in iter(stdout.readline, ""):
            print(stdout_line, end='')  # Print each line as it is produced

        for stderr_line in iter(stderr.readline, ""):
            print(stderr_line, end='')

    process.wait()  # Wait for the process to complete

if __name__ == "__main__":
    for test_name in TESTS_TO_RUN:
        print("Executing " + test_name)
        script_path = os.path.join(FILEPATH, test_name)
        run_python_script(script_path, PORT, str(BAUD_RATE))