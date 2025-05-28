from PyQt6.QtWidgets import (QApplication)
import sys
from GlassMorphicLogin import GlassMorphicLogin
from movrs_apis import update_json_fields




if __name__ == "__main__":
    update_json_fields([['state', '']])

    app = QApplication(sys.argv)
    window = GlassMorphicLogin()
    window.show()
    sys.exit(app.exec())
