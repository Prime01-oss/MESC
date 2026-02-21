import os
from PySide6.QtWidgets import QDialog, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtWebEngineWidgets import QWebEngineView

# Replace your existing GuideDialog with this one!
class GuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Mathex IDE - User Guide")
        self.resize(950, 750)
        
        self.setStyleSheet("QDialog { background-color: #252526; }")
        
        # Zero-margin layout to strip away the dialog borders
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        self.browser = QWebEngineView()
        
        # Resolve path exactly like we did for Mathematica
        current_dir = os.path.dirname(__file__)
        doc_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "docs", "MATHEX_GUIDE.html"))
        
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.browser.setHtml(html_content)
        else:
            error_html = f"""
            <div style="color: #d4d4d4; font-family: sans-serif; padding: 20px; background-color: #1e1e1e; height: 100vh; margin: 0;">
                <h2 style="color: #e06c75;">Documentation File Not Found</h2>
                <p>The system looked for the file at:</p>
                <pre style="background: #252526; padding: 10px; border: 1px solid #555;">{doc_path}</pre>
                <p>Please ensure you saved the HTML file exactly as 'MATHEX_GUIDE.html' in the 'docs' folder.</p>
            </div>
            """
            self.browser.setHtml(error_html)
            
        layout.addWidget(self.browser)

# (If you have an AboutDialog down here, leave it alone!)