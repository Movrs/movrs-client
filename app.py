from PyQt6.QtWidgets import (QApplication)
import sys
from GlassMorphicLogin import GlassMorphicLogin




if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GlassMorphicLogin()
    window.show()
    sys.exit(app.exec())
