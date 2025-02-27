import subprocess
import os
import tkinter as tk
import serial
import sys
import time
import tkinter.filedialog  # Import filedialog


def run_command(command, output_text):
    """
    Run a command in a subprocess within a virtual environment and update the output_text widget with real-time output.
    If `venv_path` is provided, the command is executed within that virtual environment.
    """

    print("Executable path:", command[0])

    # Start the subprocess
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Process the output line by line
    for line in process.stdout:
        print(line)
        output_text.insert(tk.END, line)
        output_text.see(tk.END)  # Scroll to the end
        output_text.update_idletasks()

    # Wait for the command to complete and get the return code
    process.wait()
    if process.returncode != 0:
        for line in process.stderr:
            print(line)
            output_text.insert(tk.END, line)
            output_text.see(tk.END)  # Scroll to the end
            output_text.update_idletasks()
        raise subprocess.CalledProcessError(process.returncode, command)


def upload_firmware_and_filesystem(output_text, project_dir):
    # Change to the directory where your PlatformIO project is located

    os.chdir(project_dir)
    venv_path = os.path.join(os.path.dirname(__file__), "venv")

    try:
        # Step 1: Upload the firmware
        output_text.insert(tk.END, "Uploading firmware...\n")
        run_command(["platformio", "run", "--target", "upload"], output_text)

        # Step 2: Upload the filesystem image
        output_text.insert(tk.END, "\nUploading filesystem image...\n")
        run_command(["platformio", "run", "--target", "uploadfs"], output_text)

        # Final success message
        output_text.insert(tk.END, "\nFirmware and filesystem uploaded successfully!\n")
        return True

    except subprocess.CalledProcessError as e:
        # Error handling
        output_text.insert(tk.END, f"\nError during upload:\n{e.stderr}\n")
        return False


def init_serial(baud, com_port):
    # If COM port provided, use that
    port = com_port.get()
    if port != "":
        try:
            s = serial.Serial(port, baud, timeout=1)
            print(f"Serial port {port} is open.")
            s.dtr = False
            s.rts = False
            return s
        except serial.SerialException:
            print(f"Failed to open {port}. Falling back to scanning ports.")

    # First, check for /dev/ttyUSB ports
    for i in range(6):  # Checking from /dev/ttyUSB0 to /dev/ttyUSB5
        port = f"/dev/ttyUSB{i}"
        try:
            s = serial.Serial(port, baud, timeout=1)
            print(f"Serial port {port} is open.")
            s.dtr = False
            s.rts = False
            return s
        except serial.SerialException:
            print(f"Failed to open {port}. Trying the next port.")

    # If no /dev/ttyUSB port is found, check for COM ports
    for i in range(50):  # Checking from COM0 to COM49
        port = f"COM{i}"
        try:
            s = serial.Serial(port, baud, timeout=1)
            print(f"Serial port {port} is open.")
            s.dtr = False
            s.rts = False
            return s
        except serial.SerialException:
            print(f"Failed to open {port}. Trying the next port.")

    print("Failed to open any of the ports from /dev/ttyUSB0 to /dev/ttyUSB5 or COM0 to COM9.")
    time.sleep(40)
    sys.exit(1)


def start_test(output_text, pwm_value, probe_value):
    serial = init_serial(115200, com_port_entry)
    time.sleep(2)
    pwm_error = 50
    probe_error = 100
    data = f"{pwm_value}\n"

    # Send the bytes over the serial port
    serial.write(data.encode())
    output_text.insert(tk.END, f"Start test with: {pwm_value}us PWM value\n")
    output_text.see(tk.END)  # Scroll to the end
    output_text.update_idletasks()
    time.sleep(1)
    serial.reset_input_buffer()

    pwm_read = None
    measurement = None
    start_time = time.time()  # Start the timeout timer

    # Read the buffer until "pwmRead" is found or timeout occurs
    while time.time() - start_time < 10:  # 10-second timeout
        test_result = serial.readline().decode('utf-8').strip()
        print(f"Received response: {test_result}")

        # Check if the line contains "pwmRead:"
        if "pwmRead:" in test_result:
            pwm_read = int(test_result.split("pwmRead:")[1].strip())

            # Read the next line for "position:"
            test_result = serial.readline().decode('utf-8').strip()
            print(f"Received response: {test_result}")
            if "position:" in test_result:
                measurement = int(test_result.split("position:")[1].strip())
            break  # Exit the loop after finding the necessary lines

    # Check if the timeout was reached
    if pwm_read is None or measurement is None:
        output_text.insert(tk.END, "Measurement failed: Timeout reached.\n")
        output_text.see(tk.END)  # Scroll to the end
        output_text.update_idletasks()
        return  # Exit the function if timeout occurs

    # Process and display results
    output_text.insert(tk.END, f"PWM input value: {pwm_read}\n")
    output_text.insert(tk.END, f"Probe measurement value: {measurement}\n")

    # Validate the results
    if pwm_value - pwm_error < pwm_read < pwm_value + pwm_error:
        output_text.insert(tk.END, "PWM input test finished successfully!\n")
    else:
        output_text.insert(tk.END, "PWM input test failed!\n")

    if probe_value - probe_error < measurement < probe_value + probe_error:
        output_text.insert(tk.END, "Measurement test finished successfully!\n")
    else:
        output_text.insert(tk.END, "Measurement test failed!\n")

    output_text.see(tk.END)  # Scroll to the end
    output_text.update_idletasks()


def start_upload(output_text, project_dir_entry, pwm_value_entry, probe_value_entry):
    # Clear the previous message
    output_text.delete(1.0, tk.END)

    # Get the project directory from the input field
    project_dir = project_dir_entry.get()
    print("Project dir")
    print(project_dir)

    # Call the upload function and check if it was successful
    success = upload_firmware_and_filesystem(output_text, project_dir)

    if not success:
        output_text.insert(tk.END, "\nUpload failed. Aborting test...\n")
        return  # Stop execution if upload fails

    # Get user inputs for pwm_value and probe_value
    pwm_value = int(pwm_value_entry.get())
    probe_value = int(probe_value_entry.get())

    # Start testing
    start_test(output_text, pwm_value, probe_value)


def start_test_only(output_text, pwm_value_entry, probe_value_entry):
    # Clear the previous message
    output_text.delete(1.0, tk.END)

    # Get user inputs for pwm_value and probe_value
    pwm_value = int(pwm_value_entry.get())
    probe_value = int(probe_value_entry.get())

    # Start testing
    start_test(output_text, pwm_value, probe_value)


def browse_directory(project_dir_entry):
    """
    Open a file dialog to browse and select a project directory, then set the selected path in the entry widget.
    """
    directory = tk.filedialog.askdirectory()  # Open a dialog to select a directory
    if directory:
        project_dir_entry.delete(0, tk.END)  # Clear the current entry
        project_dir_entry.insert(0, directory)  # Set the selected directory


# Set up the main window
root = tk.Tk()
root.title("Firmware and Filesystem Uploader")
root.geometry("900x900")

# Create a Frame for the input fields
input_frame = tk.Frame(root)
input_frame.pack(pady=20, padx=10)

# Add Project Directory input
project_dir_label = tk.Label(input_frame, text="Project Directory:", font=("Arial", 12))
project_dir_label.grid(row=0, column=0, padx=10, pady=10, sticky="e")
project_dir_entry = tk.Entry(input_frame, font=("Arial", 12), width=50)
project_dir_entry.grid(row=0, column=1, padx=10, pady=10, sticky="w")
project_dir_entry.insert(0, "")
browse_button = tk.Button(input_frame, text="Browse", command=lambda: browse_directory(project_dir_entry),
                          font=("Arial", 10))
browse_button.grid(row=0, column=2, padx=10, pady=10)

# Add PWM Value input
pwm_value_label = tk.Label(input_frame, text="PWM Value (us):", font=("Arial", 12))
pwm_value_label.grid(row=1, column=0, padx=10, pady=10, sticky="e")
pwm_value_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
pwm_value_entry.grid(row=1, column=1, padx=10, pady=10, sticky="w")
# Set a default value for PWM Value (optional)
pwm_value_entry.insert(0, "2000")

# Add Probe Value input
probe_value_label = tk.Label(input_frame, text="Probe Value:", font=("Arial", 12))
probe_value_label.grid(row=2, column=0, padx=10, pady=10, sticky="e")
probe_value_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
probe_value_entry.grid(row=2, column=1, padx=10, pady=10, sticky="w")
# Set a default value for Probe Value (optional)
probe_value_entry.insert(0, "1500")

# Add COM Port input
com_port_label = tk.Label(input_frame, text='COM Port (eg.: "COM7"):', font=("Arial", 12))
com_port_label.grid(row=3, column=0, padx=10, pady=10, sticky="e")
com_port_entry = tk.Entry(input_frame, font=("Arial", 12), width=20)
com_port_entry.grid(row=3, column=1, padx=10, pady=10, sticky="w")

# Create a Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Add Start Upload and Test button
start_button = tk.Button(button_frame, text="Start Upload and Test",
                         command=lambda: start_upload(output_text, project_dir_entry, pwm_value_entry,
                                                      probe_value_entry),
                         font=("Arial", 14))
start_button.pack(side=tk.LEFT, padx=10)

# Add Start Test button
test_button = tk.Button(button_frame, text="Start Test",
                        command=lambda: start_test_only(output_text, pwm_value_entry, probe_value_entry),
                        font=("Arial", 14))
test_button.pack(side=tk.LEFT, padx=10)

# Create a Text widget to show output messages
output_text = tk.Text(root, font=("Arial", 12), wrap=tk.WORD)
output_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Allow the Text widget to scroll
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

# Start the tkinter event loop
root.mainloop()
