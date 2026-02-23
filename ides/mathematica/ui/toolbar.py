from PySide6.QtWidgets import QToolBar, QWidget, QSizePolicy, QToolButton, QMenu, QMessageBox, QPushButton
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QAction
from PySide6.QtCore import Qt, QSize

class MinimalIcon:
    @staticmethod
    def get(name, color="#cccccc", size=24):
        pix = QPixmap(size, size)
        pix.fill(Qt.transparent)
        painter = QPainter(pix)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor(color))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)

        if name == "trash":
            painter.drawRect(7, 8, 10, 11) 
            painter.drawLine(5, 6, 19, 6)  
            painter.drawLine(10, 4, 14, 4) 
            pen.setWidth(1)
            painter.setPen(pen)
            painter.drawLine(10, 10, 10, 17)
            painter.drawLine(14, 10, 14, 17)
        elif name == "list":
            painter.drawLine(9, 7, 18, 7)
            painter.drawLine(9, 12, 18, 12)
            painter.drawLine(9, 17, 18, 17)
            pen.setWidth(3)
            painter.setPen(pen)
            painter.drawPoint(5, 7)
            painter.drawPoint(5, 12)
            painter.drawPoint(5, 17)
        elif name == "load":
            painter.drawRoundedRect(4, 9, 16, 11, 2, 2)
            painter.drawLine(4, 9, 10, 9)
            painter.drawLine(10, 9, 12, 6)
            painter.drawLine(12, 6, 18, 6)
            painter.drawLine(18, 6, 20, 9)
        elif name == "save":
            painter.drawRoundedRect(5, 4, 14, 16, 2, 2)
            painter.drawLine(5, 15, 19, 15)
            painter.drawLine(19, 4, 19, 8) 
            painter.drawRect(8, 15, 8, 5)
        elif name == "pdf":
            painter.drawRect(6, 3, 12, 18)
            painter.drawLine(10, 9, 14, 9)
            painter.drawLine(10, 13, 14, 13)
            painter.drawLine(10, 17, 12, 17)

        painter.end()
        return QIcon(pix)

class MathematicaToolbar(QToolBar):
    def __init__(self, parent_app):
        super().__init__(parent_app)
        self.app = parent_app
        self.setMovable(False)
        self.setIconSize(QSize(16, 16))
        
        self.setStyleSheet("""
            QToolBar { 
                background-color: #2d2d2d; 
                border: none;
                border-bottom: 1px solid #1e1e1e; 
                spacing: 4px; 
                padding: 4px 6px;
            }
            QToolButton { 
                background-color: transparent; 
                border: 1px solid transparent; 
                border-radius: 4px; 
                color: #cccccc; 
                padding: 4px 8px; 
                font-family: "Segoe UI", sans-serif;
                font-size: 10pt; 
            }
            QToolButton:hover { background-color: #454545; }
            QToolButton:pressed, QToolButton::menu-button:pressed { background-color: #094771; color: white; }
            QToolButton::menu-indicator { image: none; }
            QMenu {
                background-color: #252526;
                color: #cccccc;
                border: 1px solid #3e3e42;
                border-radius: 4px;
                padding: 4px 0px;
                font-family: "Segoe UI", sans-serif;
            }
            QMenu::item { padding: 6px 24px 6px 24px; }
            QMenu::item:selected { background-color: #0061a8; color: white; }
            QMenu::separator { background-color: #3e3e42; height: 1px; margin: 4px 0px; }
        """)
        self._setup_actions()

    def _setup_actions(self):
        act_load = QAction("Load Notebook", self)
        act_load.setIcon(MinimalIcon.get("load"))
        act_load.triggered.connect(self.app.load_session_dialog)
        self.addAction(act_load)

        act_save = QAction("Save Notebook", self)
        act_save.setIcon(MinimalIcon.get("save"))
        act_save.triggered.connect(self.app.save_session_dialog)
        self.addAction(act_save)

        act_clear = QAction("Clear Notebook", self)
        act_clear.setIcon(MinimalIcon.get("trash"))
        act_clear.triggered.connect(self.app.clear_history)
        self.addAction(act_clear)
        
        act_pdf = QAction("Export to PDF", self)
        act_pdf.setIcon(MinimalIcon.get("pdf"))
        act_pdf.triggered.connect(self.app.export_pdf_dialog)
        self.addAction(act_pdf)

        # --- PREMIUM SIMPLE MODE BUTTON (LEFT SIDE) ---
        self.simple_mode_btn = QPushButton("Simple Mode: OFF", self)
        self.simple_mode_btn.setCheckable(True)
        self.simple_mode_btn.setCursor(Qt.PointingHandCursor)
        self.simple_mode_btn.setStyleSheet("""
            QPushButton {
                background-color: #1e1e1e;
                color: #888888;
                border: 1px solid #3e3e42;
                border-radius: 12px;
                padding: 4px 18px;
                font-family: "Segoe UI", sans-serif;
                font-size: 9pt;
                font-weight: bold;
                margin: 0px 4px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: #cccccc;
                border: 1px solid #555555;
            }
            QPushButton:checked {
                background-color: #007acc;
                color: #ffffff;
                border: 1px solid #005f9e;
            }
        """)
        self.simple_mode_btn.toggled.connect(self._toggle_simple_mode)
        self.addWidget(self.simple_mode_btn)

        # --- RIGHT SPACER ---
        empty = QWidget()
        empty.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        empty.setStyleSheet("background-color: transparent;") 
        self.addWidget(empty)

        # --- RIGHT MENUS ---
        self._add_palettes_menu()
        self._add_graphics_menu()
        self._add_evaluation_menu()
        self._add_help_menu()

    def _toggle_simple_mode(self, checked):
        # Update text; colors are handled automatically by the :checked CSS state!
        self.simple_mode_btn.setText("Simple Mode: ON" if checked else "Simple Mode: OFF")
        self.app.set_simple_mode(checked)

    def _create_menu_btn(self, text):
        btn = QToolButton(self)
        btn.setText(f"{text} ▾")
        btn.setToolButtonStyle(Qt.ToolButtonTextOnly)
        btn.setPopupMode(QToolButton.InstantPopup)
        btn.setCursor(Qt.PointingHandCursor)
        return btn

    def _add_palettes_menu(self):
        btn = self._create_menu_btn("Palettes")
        menu = QMenu(btn)
        
        act_basic = QAction("Basic Math Assistant", self)
        act_basic.triggered.connect(lambda: self.app.show_palette("basic"))
        
        act_special = QAction("Special Characters", self)
        act_special.triggered.connect(lambda: self.app.show_palette("special"))
        
        menu.addAction(act_basic)
        menu.addAction(act_special)
        btn.setMenu(menu)
        self.addWidget(btn)

    def _add_graphics_menu(self):
        btn = self._create_menu_btn("Graphics")
        menu = QMenu(btn)
        
        act_2d = QAction("Insert 2D Plot Template", self)
        act_2d.triggered.connect(lambda: self.app.insert_template("Plot[Sin[x], {x, -10, 10}]"))
        
        act_3d = QAction("Insert 3D Plot Template", self)
        act_3d.triggered.connect(lambda: self.app.insert_template("Plot3D[Sin[x]*Cos[y], {x, -5, 5}, {y, -5, 5}]"))
        
        menu.addAction(act_2d)
        menu.addAction(act_3d)
        btn.setMenu(menu)
        self.addWidget(btn)

    def _add_evaluation_menu(self):
        btn = self._create_menu_btn("Evaluation")
        menu = QMenu(btn)
        
        act_eval_nb = QAction("Evaluate Notebook", self)
        act_eval_nb.triggered.connect(self.app.evaluate_notebook)
        
        act_quit = QAction("Quit Kernel", self)
        act_quit.triggered.connect(self.app.quit_kernel)
        
        menu.addAction(act_eval_nb)
        menu.addSeparator()
        menu.addAction(act_quit)
        btn.setMenu(menu)
        self.addWidget(btn)

    def _add_help_menu(self):
        btn = self._create_menu_btn("Help")
        menu = QMenu(btn)
        
        act_doc = QAction("About Mathematica", self)
        act_doc.triggered.connect(self.app.show_documentation)

        act_syntax = QAction("Syntax/User Guide", self)
        act_syntax.triggered.connect(self.app.show_syntax_guide)
        
        menu.addAction(act_doc)
        menu.addAction(act_syntax)
        btn.setMenu(menu)
        self.addWidget(btn)