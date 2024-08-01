import os
import subprocess
import sys

FILEPATH = os.path.dirname(__file__)

TESTS_TO_RUN = ['power_test.py']

PORT = 'COM5'
BAUD_RATE = 57600

def run_python_script(script_path, PORT, BAUD_RATE):
    # Construct the command to run the Python script
    command = [sys.executable, script_path] + [PORT, BAUD_RATE]

    # Execute the command
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    
    # Read stdout and stderr line by line
    for stdout_line in iter(process.stdout.readline, ""):
        print(stdout_line, end='')  # Print each line as it is produced

    process.stdout.close()
    process.wait()  # Wait for the process to complete

    # Print any remaining stderr output
    for stderr_line in process.stderr:
        print(stderr_line, end='')
    
    process.stderr.close()

if __name__ == "__main__":
    for test_name in TESTS_TO_RUN:
        print("Executing " + test_name)
        script_path = os.path.join(FILEPATH, test_name)
        run_python_script(script_path, PORT, str(BAUD_RATE))