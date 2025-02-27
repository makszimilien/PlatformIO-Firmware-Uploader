import subprocess
import os
import tkinter as tk
import tkinter.filedialog  # Import filedialog


def run_command(command, output_text):
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


def upload_firmware(output_text, project_dir_entry):
    # Get the project directory from the input field
    project_dir = project_dir_entry.get()
    # Change to the directory where your PlatformIO project is located
    os.chdir(project_dir)
    venv_path = os.path.join(os.path.dirname(__file__), "venv")

    try:
        # Upload the firmware
        output_text.insert(tk.END, "Uploading firmware...\n")
        run_command(["platformio", "run", "--target", "upload"], output_text)

        # Final success message
        output_text.insert(tk.END, "\nFirmware uploaded successfully!\n")
        return True

    except subprocess.CalledProcessError as e:
        # Error handling
        output_text.insert(tk.END, f"\nError during upload:\n{e.stderr}\n")
        return False


def upload_filesystem(output_text, project_dir_entry):
    # Get the project directory from the input field
    project_dir = project_dir_entry.get()
    # Change to the directory where your PlatformIO project is located
    os.chdir(project_dir)
    venv_path = os.path.join(os.path.dirname(__file__), "venv")

    try:
        # Upload the filesystem image
        output_text.insert(tk.END, "\nUploading filesystem image...\n")
        run_command(["platformio", "run", "--target", "uploadfs"], output_text)

        # Final success message
        output_text.insert(tk.END, "\nFirmware and filesystem uploaded successfully!\n")
        return True

    except subprocess.CalledProcessError as e:
        # Error handling
        output_text.insert(tk.END, f"\nError during upload:\n{e.stderr}\n")
        return False


def upload_all(output_text, project_dir_entry):
    # Clear the previous message
    output_text.delete(1.0, tk.END)
    success = upload_firmware(output_text, project_dir_entry)

    if not success:
        output_text.insert(tk.END, "\nUpload failed. Aborting\n")
        return  # Stop execution if upload fails

    upload_filesystem(output_text, project_dir_entry)


def browse_directory(project_dir_entry):
    # Open a file dialog to browse and select a project directory, then set the selected path in the entry widget.
    directory = tk.filedialog.askdirectory()  # Open a dialog to select a directory
    if directory:
        project_dir_entry.delete(0, tk.END)  # Clear the current entry
        project_dir_entry.insert(0, directory)  # Set the selected directory


# Set up the main window
root = tk.Tk()
root.title("Firmware and Filesystem Uploader")
root.geometry("1500x900")

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

# Create a Frame for buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=10)

# Add Upload Firmware button
start_button = tk.Button(button_frame, text="Upload Firmware",
                         command=lambda: upload_firmware(output_text, project_dir_entry),
                         font=("Arial", 14))
start_button.pack(side=tk.LEFT, padx=10)

# Add Upload Filesystem button
start_button = tk.Button(button_frame, text="Upload Filesystem",
                         command=lambda: upload_filesystem(output_text, project_dir_entry),
                         font=("Arial", 14))
start_button.pack(side=tk.LEFT, padx=10)

# Add Upload All button
start_button = tk.Button(button_frame, text="Upload All",
                         command=lambda: upload_all(output_text, project_dir_entry),
                         font=("Arial", 14))
start_button.pack(side=tk.LEFT, padx=10)

# Create a Text widget to show output messages
output_text = tk.Text(root, font=("Arial", 12), wrap=tk.WORD)
output_text.pack(pady=20, padx=20, fill=tk.BOTH, expand=True)

# Allow the Text widget to scroll
scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=output_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
output_text.config(yscrollcommand=scrollbar.set)

# Start the tkinter event loop
root.mainloop()
