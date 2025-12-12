import os
import sys
from qt_app import TrayApp


if __name__ == '__main__':
    ROOT = os.path.dirname(os.path.abspath(__file__))
    os.chdir(ROOT)

    app = TrayApp.instance()
    try:
        app.run()
    except KeyboardInterrupt:
        app.quit()
        sys.exit(0)