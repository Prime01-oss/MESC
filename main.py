import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app_platform.ui_shell.app_shell import StemShell

# --- Imports ---
from ides.mathex.ide_plugin import MatlabTool
from ides.mathematica.ide_plugin import MathematicaTool

def run():
    # 1. Windows Taskbar Icon Fix (AppUserModelID)
    if sys.platform == "win32":
        import ctypes
        myappid = 'mesc.mathematical.environment.1.0' # Arbitrary string identifying your app
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
    app = QApplication(sys.argv)
    
    # 2. Build an absolute path to ensure the icon is always found
    basedir = os.path.dirname(__file__)
    icon_path = os.path.join(basedir, "ides", "mathex", "resources", "icon.ico")
    
    # 3. Set the icon globally on the application level
    app.setWindowIcon(QIcon(icon_path))
    
    shell = StemShell()
    
    # --- Register Tools ---
    shell.register_tool(MatlabTool())
    shell.register_tool(MathematicaTool())
    
    shell.switch_tool(0)
    shell.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()