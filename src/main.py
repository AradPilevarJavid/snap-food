from platform_core import Platform
from gui import App
from storage import STORAGE_TYPE

if __name__ == "__main__":
    platform = Platform(STORAGE_TYPE)
    app = App(platform)
    app.run()