# PlatformIO MCU Compiler & Uploader

This tool allows you to compile and upload PlatformIO projects to microcontrollers. To use it, you need to have PlatformIO Core installed on your PC.

## Prerequisites

### Install Python
The easiest way to set up PlatformIO is by installing Python first. You can download the latest version from the official website:

[Download Python](https://www.python.org)

This program has been tested with **Python 3.12.7**.

### Windows Installation Options
When installing Python on Windows, select the following options:
- ✅ Use admin privileges when installing `py.exe`
- ✅ Add `python.exe` to PATH
- ✅ Install `pip`
- ✅ Install `td/tk`
- ✅ Python test suite
- ✅ Precompile standard library

## Install PlatformIO
Once Python is installed, open the command prompt and run:

```
pip install platformio
```

## Fix Missing PATH Issue
If you receive a missing PATH warning message, you need to add it manually:

1. Open **System Properties**:
   - Go to **System** → **Advanced system settings** → **Environment Variables**
2. Under **System Variables**, find and select **Path**, then click **Edit**.
3. Click **New** and add the following path (adjust for your username and Python version):

   ```
   C:\Users\username\AppData\Roaming\Python\Python312\Scripts
   ```

4. Click **OK** to save and close the settings.

You're now ready to compile and upload PlatformIO projects to your MCU!
