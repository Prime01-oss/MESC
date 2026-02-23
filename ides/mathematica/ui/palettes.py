from PySide6.QtWidgets import (QWidget, QVBoxLayout, QGridLayout,
                               QPushButton, QLabel, QFrame)
from PySide6.QtCore import Qt

class PaletteWindow(QWidget):
    def __init__(self, title, app_parent):
        # Qt.Tool makes it a floating tool window. 
        # Passing app_parent ensures it stays cleanly on top of the main IDE.
        super().__init__(app_parent, Qt.Tool)
        self.app_parent = app_parent
        self.setWindowTitle(title)
        
        # FIX: Changed font-size from 14px to 10pt
        self.setStyleSheet("""
            QWidget { 
                background-color: #252526; 
                color: #cccccc; 
                font-family: 'Segoe UI', sans-serif; 
            }
            QPushButton { 
                background-color: #333333; 
                border: 1px solid #3e3e42; 
                border-radius: 4px; 
                padding: 6px; 
                font-size: 10pt; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #454545; 
                border: 1px solid #007acc; 
            }
            QPushButton:pressed { 
                background-color: #094771; 
                color: white;
            }
            QLabel { 
                font-weight: bold; 
                color: #e0e0e0;
                margin-top: 8px; 
                margin-bottom: 2px; 
            }
        """)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(6)

    def add_section(self, title, buttons_data, columns=4):
        if title:
            self.layout.addWidget(QLabel(title))
            
        grid = QGridLayout()
        grid.setSpacing(4)
        row, col = 0, 0
        for label, template in buttons_data:
            btn = QPushButton(label)
            # CRITICAL FIX: Prevent buttons from stealing focus from the Notebook Cell!
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setCursor(Qt.PointingHandCursor)
            
            # Send the template text to the main app's active cell
            btn.clicked.connect(lambda checked=False, t=template: self.app_parent.insert_template(t))
            grid.addWidget(btn, row, col)
            
            col += 1
            if col >= columns:
                col = 0
                row += 1
                
        self.layout.addLayout(grid)
        
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #3e3e42;")
        line.setFixedHeight(1)
        self.layout.addWidget(line)

class BasicMathAssistant(PaletteWindow):
    def __init__(self, app_parent):
        super().__init__("Basic Math Assistant", app_parent)
        self.resize(280, 450)

        calc_buttons = [
            ("√", "Sqrt[]"), ("x²", "^2"), ("xⁿ", "^"), ("/", "/"),
            ("π", "Pi"), ("e", "E"), ("∞", "Infinity"), ("i", "I"),
        ]
        self.add_section("Common", calc_buttons, columns=4)

        calculus_buttons = [
            ("∫", "Integrate[, x]"), ("∂", "D[, x]"), ("∑", "Sum[, {i, 1, n}]"), ("∏", "Product[, {i, 1, n}]"),
            ("Lim", "Limit[, x -> 0]"), ("Series", "Series[, {x, 0, 3}]")
        ]
        self.add_section("Calculus", calculus_buttons, columns=2)

        func_buttons = [
            ("Sin", "Sin[]"), ("Cos", "Cos[]"), ("Tan", "Tan[]"), 
            ("Log", "Log[]"), ("Exp", "Exp[]"), ("Abs", "Abs[]")
        ]
        self.add_section("Functions", func_buttons, columns=3)
        self.layout.addStretch()

class SpecialCharacters(PaletteWindow):
    def __init__(self, app_parent):
        super().__init__("Special Characters", app_parent)
        self.resize(320, 300)

        greek_lower = [
            ("α", "Alpha"), ("β", "Beta"), ("γ", "Gamma"), ("δ", "Delta"),
            ("ε", "Epsilon"), ("ζ", "Zeta"), ("η", "Eta"), ("θ", "Theta"),
            ("λ", "Lambda"), ("μ", "Mu"), ("π", "Pi"), ("σ", "Sigma"),
            ("τ", "Tau"), ("φ", "Phi"), ("ω", "Omega")
        ]
        self.add_section("Lowercase Greek", greek_lower, columns=5)
        
        greek_upper = [
            ("Γ", "Gamma"), ("Δ", "Delta"), ("Θ", "Theta"), 
            ("Λ", "Lambda"), ("Σ", "Sigma"), ("Ω", "Omega")
        ]
        self.add_section("Uppercase Greek", greek_upper, columns=5)
        
        operators = [
            ("==", "=="), ("≠", "!="), ("≤", "<="), ("≥", ">="),
            ("→", "->"), ("∞", "Infinity")
        ]
        self.add_section("Operators", operators, columns=4)
        self.layout.addStretch()