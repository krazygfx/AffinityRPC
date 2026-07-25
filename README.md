<h1 align="center">AffinityRPC</h1>

<p align="center">
  <strong>Discord Rich Presence integration for Affinity Studio by Canva</strong>
</p>

<p align="center">
  
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version">
  
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform">
  
  <img src="https://github.com/user-attachments/assets/7f50f19d-c246-4663-9364-88c796640d98" alt="License">
</p>




A custom Discord Rich Presence integration for Affinity Studio by Canva. It displays your currently active project status directly on your Discord profile using a clean, native, and lightweight interface.

# AffinityRPC - Discord Rich Presence

A custom Discord Rich Presence integration for Affinity Studio by Canva. It displays your currently active project status directly on your Discord profile.

## Prerequisites

The program communicates with Affinity via its local MCP server. You must enable this feature before running the application:
1. Open any Affinity application.
2. Navigate to the Settings or Preferences menu.
3. Locate and enable the local MCP server option (operating on port 6767 by default).

## Installation

### Option 1: Portable Executable (Recommended)
1. Navigate to the **Releases** section on the right side of this repository.
2. Download the `AffinityRPC_Portable.zip` file.
3. Extract the folder to your preferred location.
4. Run `AffinityRPC.exe`.

*Security Notice: The executable is compiled using PyInstaller. Due to the nature of this packaging tool, some security systems (such as Windows Defender) may flag it as a false positive heuristic detection. If this occurs, please add a directory exclusion in your antivirus settings.*

### Option 2: Running from Source
If you prefer to inspect and run the code manually:
1. Ensure Python 3.x is installed on your system.
2. Clone this repository.
3. Install the required dependencies: 
   `pip install -r requirements.txt`
4. Run the script: 
   `python affinity.py`

## Features
* **Real-time Tracking:** Automatically detects the active Affinity document.
* **Bilingual Support:** Interface translates automatically to English or Spanish based on system locale (with manual toggle available).
* **System Tray Integration:** Runs silently in the background.
* **Autostart:** Configurable option to launch with Windows seamlessly.
