import subprocess

def get_frontmost_app():
    try:
        # AppleScript to get the frontmost application
        script = 'tell application "System Events" to get name of first application process whose frontmost is true'
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        app_name = result.stdout.strip()
        return app_name
    except Exception as e:
        return "Unknown App"
