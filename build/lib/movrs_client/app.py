from PyQt6.QtWidgets import (QApplication)
import sys
from movrs_client.GlassMorphicLogin import GlassMorphicLogin
from movrs_client.movrs_apis import update_json_fields

def main():
    update_json_fields([['state', '']])

    app = QApplication(sys.argv)
    window = GlassMorphicLogin()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
