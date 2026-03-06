from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QStackedWidget, QPushButton, QFrame, QLabel, QMenu)
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QIcon, QPixmap, QCloseEvent
import sys
import os

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        # Go up two levels from app_platform/ui_shell to reach the project root
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    return os.path.join(base_path, relative_path)

class CustomTitleBar(QFrame):
    def __init__(self, parent_window):
        super().__init__(parent_window)
        self.parent_window = parent_window
        self.setFixedHeight(40) 
        self.setObjectName("TitleBar")
        
        # Premium VS Code / Modern Fluent Design CSS
        self.setStyleSheet("""
            QFrame#TitleBar {
                background-color: #181818;
                border-bottom: 1px solid #333333; /* The crisp, continuous separator line */
            }
            
            /* FORCE containers to be transparent so they don't mask the background or border */
            QWidget#transparent-box {
                background-color: transparent;
                border: none;
            }
            
            QLabel {
                background-color: transparent;
                color: #cccccc;
                font-family: "Segoe UI", "Helvetica Neue", sans-serif;
                font-size: 10pt;
            }
            QLabel#app-title {
                font-weight: 600;
                font-size: 10pt;
                color: #e0e0e0;
                letter-spacing: 0.5px;
            }
            
            /* Window Control Buttons - Flush, Native Feel */
            QPushButton[cssClass="ctrl-btn"] {
                background-color: transparent;
                border: none;
                color: #cccccc;
                font-family: "Segoe UI Symbol", "Segoe MDL2 Assets", sans-serif;
                font-size: 9pt;
                width: 46px;
                height: 39px; /* 1px less than parent height so it doesn't cover the bottom border */
                margin: 0px;
                border-radius: 0px; 
            }
            QPushButton[cssClass="ctrl-btn"]:hover { 
                background-color: #2d2d2d; 
                color: #ffffff; 
            }
            QPushButton#close-btn:hover { 
                background-color: #e81123; 
                color: #ffffff; 
            }
            
            /* Premium Breadcrumb "Pill" Container */
            QFrame#breadcrumb-pill {
                background-color: #222222;
                border: 1px solid #333333;
                border-radius: 6px;
            }
            QFrame#breadcrumb-pill:hover {
                background-color: #2a2d2e;
                border: 1px solid #454545;
            }

            /* Breadcrumb Interactive Button */
            QPushButton[cssClass="breadcrumb-btn"] {
                background-color: transparent;
                color: #cccccc;
                border: none;
                font-family: "Segoe UI", sans-serif;
                font-size: 10pt;
                padding: 3px 6px;
                border-radius: 4px;
            }
            QPushButton[cssClass="breadcrumb-btn"]:hover {
                background-color: #333538;
                color: #ffffff;
            }
            QPushButton[cssClass="breadcrumb-btn"]::menu-indicator {
                image: none; /* Hide default OS dropdown arrow */
            }
        """)
        
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(12, 0, 0, 0) # 0 margin on the right to keep window controls flush
        self.layout.setSpacing(0)
        
        # --- LEFT: Logo & App Title ---
        self.left_container = QWidget()
        self.left_container.setObjectName("transparent-box") # Fixes the grey background block
        self.left_layout = QHBoxLayout(self.left_container)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(10)
        
        # Load App Logo (Inside App) - NOW USING get_resource_path
        self.logo_label = QLabel()
        logo_path = get_resource_path(os.path.join("ides", "mathex", "resources", "logo.png"))
        logo_pixmap = QPixmap(logo_path)
        if not logo_pixmap.isNull():
            self.logo_label.setPixmap(logo_pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
        self.app_title = QLabel("MESC-Modular Enviornment for Scientific Computation")
        self.app_title.setObjectName("app-title")
        
        self.left_layout.addWidget(self.logo_label)
        self.left_layout.addWidget(self.app_title)
        self.layout.addWidget(self.left_container)
        
        self.layout.addStretch(1) # Push controls to the right
        
        # --- RIGHT: Window Controls ---
        self.ctrl_container = QWidget()
        self.ctrl_container.setObjectName("transparent-box") # Fixes the grey background block
        self.ctrl_layout = QHBoxLayout(self.ctrl_container)
        self.ctrl_layout.setContentsMargins(0, 0, 0, 0)
        self.ctrl_layout.setSpacing(0)
        
        # Using clean, crisp Unicode characters to perfectly replicate the Win/Linux controls in Dark Mode
        self.min_btn = QPushButton("─")
        self.min_btn.setProperty("cssClass", "ctrl-btn")
        self.min_btn.clicked.connect(self.parent_window.showMinimized)
        
        self.max_btn = QPushButton("□")
        self.max_btn.setProperty("cssClass", "ctrl-btn")
        self.max_btn.clicked.connect(self.toggle_maximize)
        
        self.close_btn = QPushButton("✕")
        self.close_btn.setObjectName("close-btn")
        self.close_btn.setProperty("cssClass", "ctrl-btn")
        self.close_btn.clicked.connect(self.parent_window.close)
        
        self.ctrl_layout.addWidget(self.min_btn)
        self.ctrl_layout.addWidget(self.max_btn)
        self.ctrl_layout.addWidget(self.close_btn)
        self.layout.addWidget(self.ctrl_container)

        # --- CENTER: Breadcrumbs (The Command Center Pill) ---
        self.breadcrumb_pill = QFrame(self)
        self.breadcrumb_pill.setObjectName("breadcrumb-pill")
        self.bc_layout = QHBoxLayout(self.breadcrumb_pill)
        self.bc_layout.setContentsMargins(12, 2, 12, 2)
        self.bc_layout.setSpacing(4)
        
        self.root_label = QLabel("Select Tool")
        self.root_label.setStyleSheet("font-weight: 500;")
        
        self.separator = QLabel("›")
        self.separator.setStyleSheet("color: #656565; font-size: 12pt; padding-bottom: 3px;")
        
        self.tool_selector_btn = QPushButton("No IDE Selected  ▾")
        self.tool_selector_btn.setCursor(Qt.PointingHandCursor)
        self.tool_selector_btn.setProperty("cssClass", "breadcrumb-btn")
        
        # Premium Dropdown Menu
        self.tool_menu = QMenu(self)
        self.tool_menu.setStyleSheet("""
            QMenu {
                background-color: #1e1e1e;
                color: #cccccc;
                border: 1px solid #333333;
                border-radius: 6px;
                font-family: "Segoe UI", sans-serif;
                font-size: 10pt;
                padding: 4px 0px;
                margin-top: 4px;
            }
            QMenu::item { padding: 6px 28px 6px 24px; }
            QMenu::item:selected { background-color: #0061a8; color: white; }
        """)
        self.tool_selector_btn.setMenu(self.tool_menu)
        
        self.bc_layout.addWidget(self.root_label)
        self.bc_layout.addWidget(self.separator)
        self.bc_layout.addWidget(self.tool_selector_btn)
        
        self._drag_pos = None

    def resizeEvent(self, event):
        """Forces the breadcrumb pill to be mathematically dead-center in the window."""
        super().resizeEvent(event)
        bc_width = self.breadcrumb_pill.sizeHint().width()
        bc_height = self.breadcrumb_pill.sizeHint().height()
        
        x_center = (self.width() - bc_width) // 2
        y_center = (self.height() - bc_height) // 2
        
        self.breadcrumb_pill.setGeometry(x_center, y_center, bc_width, bc_height)

    # --- Custom Window Behaviors (Dragging & Maximizing) ---
    def toggle_maximize(self):
        if self.parent_window.isMaximized():
            self.parent_window.showNormal()
            self.max_btn.setText("□")
        else:
            self.parent_window.showMaximized()
            self.max_btn.setText("❐")

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.parent_window.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and event.buttons() == Qt.LeftButton:
            self.parent_window.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()
        
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggle_maximize()


class StemShell(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Hide OS borders to allow the single-row top layout
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        
        # Set the OS-level window title for the Taskbar preview
        self.setWindowTitle("MESC")
        
        # Set Taskbar Icon (Application level) - NOW USING get_resource_path
        icon_path = get_resource_path(os.path.join("ides", "mathex", "resources", "icon.ico"))
        self.setWindowIcon(QIcon(icon_path))
        
        self.resize(1400, 900)
        
        self.central_widget = QWidget()
        self.central_widget.setObjectName("AppCentralWidget")
        
        # CRITICAL FIX: Only apply this background to the main container ID, 
        # so it doesn't leak into the Title Bar's child elements.
        self.central_widget.setStyleSheet("QWidget#AppCentralWidget { background-color: #1e1e1e; }") 
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Attach Custom Title Bar
        self.title_bar = CustomTitleBar(self)
        self.main_layout.addWidget(self.title_bar)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.tools = []

    def register_tool(self, tool):
        index = len(self.tools)
        self.tools.append(tool)
        self.stack.addWidget(tool.get_widget())
        
        # Add tool to the breadcrumb dropdown menu
        action = self.title_bar.tool_menu.addAction(tool.get_name())
        action.triggered.connect(lambda checked=False, idx=index: self.switch_tool(idx))
        
        if index == 0:
            self.switch_tool(0)

    def switch_tool(self, index):
        old_index = self.stack.currentIndex()
        if old_index >= 0 and old_index < len(self.tools):
            self.tools[old_index].on_deactivate()
            
        self.stack.setCurrentIndex(index)
        active_tool = self.tools[index]
        active_tool.on_activate()
        
        # Update Breadcrumb text while keeping the arrow
        self.title_bar.tool_selector_btn.setText(f"{active_tool.get_name()}  ▾")
        self.title_bar.resizeEvent(None)

    def closeEvent(self, event):
        """
        Forward the close event to all registered tool widgets.
        This ensures IDEs like Mathex can trigger their internal saving logic (persistence).
        """
        for tool in self.tools:
            widget = tool.get_widget()
            if hasattr(widget, 'closeEvent'):
                # Create and send a close event to the child widget manually
                close_evt = QCloseEvent()
                widget.closeEvent(close_evt)
        event.accept()