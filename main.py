import sys
from PySide6.QtWidgets import QApplication
from app_platform.ui_shell.app_shell import StemShell

# --- Imports ---
from ides.mathex.ide_plugin import MatlabTool
from ides.mathematica.ide_plugin import MathematicaTool

def run():
    app = QApplication(sys.argv)
    
    shell = StemShell()
    
    # --- Register Tools ---
    shell.register_tool(MatlabTool())
    shell.register_tool(MathematicaTool())
    
    shell.switch_tool(0)
    shell.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    run()