import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from app_platform.ui_shell.app_shell import StemShell

# --- Imports ---
from ides.mathex.ide_plugin import MatlabTool
from ides.mathematica.ide_plugin import MathematicaTool

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # Fallback to the current directory
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

def run():
    # 1. Windows Taskbar Icon Fix (AppUserModelID)
    if sys.platform == "win32":
        import ctypes
        myappid = 'mesc.mathematical.environment.1.0' 
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        
    app = QApplication(sys.argv)
    
    # 2. Use the new PyInstaller-safe path resolver
    icon_path = get_resource_path(os.path.join("ides", "mathex", "resources", "icon.ico"))
    
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