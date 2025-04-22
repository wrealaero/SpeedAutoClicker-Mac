import requests
from version import __version__

def check_update():
    try:
        r = requests.get("https://api.github.com/repos/wrealaero/SpeedAutoClicker-Mac/releases/latest")
        latest_version = r.json()["tag_name"]
        return latest_version != f"v{__version__}"
    except:
        return False
