# App-Aware Clipboard Manager

## Description
A smart clipboard manager built with **PyQt6** that tracks multiple copied items from various applications on macOS. Users can view and manage their clipboard history efficiently, filtered by the application they copied from. The tool supports quick copy-back of previous items.  

## Features
- Tracks all copied text from any app (Chrome, Word, IDEs, etc.).  
- Displays a **dropdown of recent applications** to filter clipboard items.  
- Shows **clipboard history** with timestamps.  
- **Right-click to copy items back** to the system clipboard.  
- Works reliably on macOS with live clipboard monitoring.  

## Future Enhancements
- Support for images and rich text.  
- Search/filter within an app.  
- Pin favorite items for quick access.  
- Save and load history across sessions.  

## Tech Stack
- Python 3.x  
- PyQt6 for GUI  
- AppleScript (via subprocess) to detect frontmost app on macOS  

## How to Run

Follow these steps to run the App-Aware Clipboard Manager on macOS:

1. **Clone the repository** (or download the project folder):

```bash
git clone <your-repo-url>
cd <project-folder>
```
2. **Create a virtual environment** (recommended)

```bash
# macOS/Linux
python3 -m venv venv
source venv/bin/activate

# Windows
python -m venv venv
venv\Scripts\activate
```
3. **Install dependencies:**

```bash
pip install PyQt6
```
4. **Run the application:**

```bash
python main.py
```
5. The GUI will open. Copy text from any app, and it will appear in the clipboard manager.
 - Use the dropdown to filter items by the app they were copied from.
 - Right-click an item to copy it back to the clipboard.
