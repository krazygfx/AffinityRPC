<h1 align="center">AffinityRPC</h1>

<p align="center">
  <strong>Discord Rich Presence integration for Affinity Studio by Canva</strong>
</p>

<p align="center">
  <br>
  <img src="https://img.shields.io/badge/version-1.0.0-blue.svg" alt="Version"> &nbsp;
  <img src="https://img.shields.io/badge/platform-Windows-lightgrey.svg" alt="Platform"> &nbsp;
  <br>
  <img src="https://github.com/user-attachments/assets/7f50f19d-c246-4663-9364-88c796640d98" alt="License">
</p>



A custom Discord Rich Presence integration for Affinity Studio by Canva. It displays your currently active project status directly on your Discord profile using a clean, native, and lightweight interface.

# AffinityRPC - Discord Rich Presence

<img width="2000" height="1000" alt="PRUEBA" src="https://github.com/user-attachments/assets/24e4b700-1c55-4a3b-961b-0b6a1079686f" />

A custom Discord Rich Presence integration for Affinity Studio by Canva. It displays your currently active project status directly on your Discord profile.

## Prerequisites

The program communicates with Affinity via its local MCP server. You must enable this feature before running the application:
1. Open Affinity application.
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
* **Smart Process Monitoring:** Seamlessly connects to Discord when `Affinity.exe` is launched and instantly clears your status the moment it closes.
* **Real-time Tracking:** Automatically detects your active document and updates your Rich Presence instantly.
* **Idle & Menu States:** Displays a "Browsing menus" status when the application is open but no project is active.
* **Privacy Mode:** Hides your sensitive project names on Discord while keeping the activity and timer visible.
* **Extension Toggle:** Choose whether to display the specific file extension (e.g., `.af`, `.psd`, `.ai`) on your profile.
* **Bilingual Support:** Interface adapts automatically to English or Spanish based on your system locale (includes a manual toggle).
* **System Tray Integration:** Runs silently in the background with a fully featured context menu for quick access.
* **Autostart:** Configurable option to launch seamlessly with Windows.

* ### Troubleshooting: Stuck on "Browsing menus"

Occasionally, your Discord Rich Presence might get stuck displaying **"Browsing menus"** even when you have a document actively open. 

**Why does this happen?**
This RPC tool relies on Affinity's local scripting API (communicating via port `6767`). Since this API is relatively new, Affinity's internal web server can sometimes crash or freeze in the background (throwing an `ECONNREFUSED` error). When this happens, our tool detects that the application is open, but cannot retrieve the document data.

**How to fix it:**
* **Restart Affinity:** Completely close and reopen your Affinity application. This usually restarts their internal server and restores the connection.
* **Restart your PC:** If closing the app doesn't work, a background "zombie" process might be keeping port `6767` locked. A quick system reboot will clear the locked port and force the API to reset.

*Note: This is a known limitation of Affinity's current API architecture and not a bug within the RPC script itself.*
