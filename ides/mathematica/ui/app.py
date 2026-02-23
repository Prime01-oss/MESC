import os
import base64
import json
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel,
                               QDialog, QTableWidget, QTableWidgetItem,
                               QHeaderView, QSizePolicy, QFileDialog, QMessageBox)
from PySide6.QtCore import Qt, QSize, QSettings
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

from ..kernel.engine import MathematicaBackend
from .toolbar import MathematicaToolbar
from .palettes import BasicMathAssistant, SpecialCharacters

QT_SCROLLBAR_STYLE = """
    QScrollBar:vertical { border: none; background: #1e1e1e; width: 10px; margin: 0px; }
    QScrollBar::handle:vertical { background: #424242; min-height: 20px; border-radius: 5px; margin: 2px; }
    QScrollBar::handle:vertical:hover { background: #4f4f4f; }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

    QScrollBar:horizontal { border: none; background: #1e1e1e; height: 10px; margin: 0px; }
    QScrollBar::handle:horizontal { background: #424242; min-width: 20px; border-radius: 5px; margin: 2px; }
    QScrollBar::handle:horizontal:hover { background: #4f4f4f; }
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
"""

class NotebookPage(QWebEnginePage):
    def __init__(self, app_parent, parent=None):
        super().__init__(parent)
        self.app_parent = app_parent

    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        if message.startswith("EXECUTE:"):
            try:
                parts = message.split(":", 2)
                if len(parts) == 3:
                    self.app_parent.execute_cell(int(parts[1]), base64.b64decode(parts[2]).decode('utf-8'))
            except Exception as e: print(f"Cell Execution Error: {e}")
            
        elif message.startswith("MANIPULATE:"):
            try:
                parts = message.split(":", 4)
                self.app_parent.update_manipulate(
                    cell_id=int(parts[1]),
                    var_name=parts[2],
                    var_value=float(parts[3]),
                    expr_str=base64.b64decode(parts[4]).decode('utf-8')
                )
            except Exception as e: print(f"Manipulate Update Error: {e}")
            
        elif message.startswith("SAVE_STATE:"):
            try:
                parts = message.split(":", 1)
                if len(parts) == 2:
                    ui_state_json = base64.b64decode(parts[1]).decode('utf-8')
                    self.app_parent._save_auto_state(ui_state_json)
            except Exception as e:
                print(f"Auto-save error: {e}")
        else:
            super().javaScriptConsoleMessage(level, message, lineNumber, sourceID)

class VariableInspectorDialog(QDialog):
    def __init__(self, variables, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Variable Inspector")
        self.resize(400, 500)
        self.setStyleSheet(f"""
            QDialog {{ background-color: #252526; color: white; }}
            QTableWidget {{ background-color: #1e1e1e; color: #d4d4d4; border: 1px solid #333; gridline-color: #333; }}
            QHeaderView::section {{ background-color: #333; color: white; padding: 4px; border: none; }}
            {QT_SCROLLBAR_STYLE}
        """)
        
        layout = QVBoxLayout(self)
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Variable", "Value / Expression"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setRowCount(len(variables))
        for i, (name, val) in enumerate(sorted(variables.items())):
            self.table.setItem(i, 0, QTableWidgetItem(name))
            self.table.setItem(i, 1, QTableWidgetItem(str(val)))
            
        layout.addWidget(self.table)
        btn = QPushButton("Close")
        btn.clicked.connect(self.accept)
        btn.setStyleSheet("background: #007acc; color: white; border: none; padding: 8px; border-radius: 4px;")
        layout.addWidget(btn)

class DocumentationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MESC-Mathematica IDE Documentation")
        self.resize(900, 750)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QWebEngineView()
        
        current_dir = os.path.dirname(__file__)
        doc_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "docs", "MATHEMATICA_IDE.html"))
        
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.browser.setHtml(html_content)
        else:
            error_html = f"""
            <div style="color: #d4d4d4; font-family: sans-serif; padding: 20px; background-color: #1e1e1e; height: 100vh;">
                <h2 style="color: #e06c75;">Documentation File Not Found</h2>
                <p>The system looked for the documentation file at:</p>
                <pre style="background: #252526; padding: 10px; border: 1px solid #555;">{doc_path}</pre>
                <p>Please ensure you saved the HTML file exactly as 'MATHEMATICA_IDE.html' in the 'docs' folder.</p>
            </div>
            """
            self.browser.setHtml(error_html)
            
        layout.addWidget(self.browser)

class SyntaxGuideDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("MESC-Mathematica Syntax & User Guide")
        self.resize(950, 750)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.browser = QWebEngineView()
        
        current_dir = os.path.dirname(__file__)
        doc_path = os.path.abspath(os.path.join(current_dir, "..", "..", "..", "docs", "MATHEMATICA_SYNTAX.html"))
        
        if os.path.exists(doc_path):
            with open(doc_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            self.browser.setHtml(html_content)
        else:
            error_html = f"""
            <div style="color: #d4d4d4; font-family: sans-serif; padding: 20px; background-color: #1e1e1e; height: 100vh;">
                <h2 style="color: #e06c75;">Syntax Guide Not Found</h2>
                <p>The system looked for the file at:</p>
                <pre style="background: #252526; padding: 10px; border: 1px solid #555;">{doc_path}</pre>
                <p>Please ensure you saved the file exactly as 'MATHEMATICA_SYNTAX.html' in the 'docs' folder.</p>
            </div>
            """
            self.browser.setHtml(error_html)
            
        layout.addWidget(self.browser)

class MathematicaApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.backend = MathematicaBackend()
        self.current_save_path = ""
        self.palettes = {} 
        self.setStyleSheet(f"QWidget {{ background-color: #1e1e1e; }} {QT_SCROLLBAR_STYLE}")
        self._init_ui()
        self.browser.loadFinished.connect(self._restore_auto_state)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.toolbar = MathematicaToolbar(self)
        layout.addWidget(self.toolbar)

        self.browser = QWebEngineView()
        self.browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.page = NotebookPage(self, self.browser)
        self.browser.setPage(self.page)
        
        self.base_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
            <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
            <style>
                ::-webkit-scrollbar { width: 10px; height: 10px; }
                ::-webkit-scrollbar-track { background: #1e1e1e; }
                ::-webkit-scrollbar-thumb { background: #424242; border-radius: 5px; }
                ::-webkit-scrollbar-thumb:hover { background: #4f4f4f; }
                ::-webkit-scrollbar-corner { background: #1e1e1e; }

                body { background-color: #1e1e1e; color: #d4d4d4; font-family: 'Segoe UI', sans-serif; margin: 0; padding: 15px; padding-bottom: 250px; }
                
                .cell { position: relative; background-color: #252526; border: 1px solid #3e3e42; border-radius: 6px; padding: 10px 15px; margin-bottom: 15px; transition: border 0.2s, box-shadow 0.2s; }
                .cell:focus-within { border: 1px solid #007acc; box-shadow: 0 0 8px rgba(0, 122, 204, 0.2); }
                
                .cell-controls { position: absolute; top: 6px; right: 6px; z-index: 10; opacity: 0; transition: opacity 0.2s ease-in-out; }
                .cell:hover .cell-controls { opacity: 1; }
                .cell-controls button { background: transparent; border: none; color: #cccccc; cursor: pointer; font-size: 18px; line-height: 1; padding: 2px 8px; border-radius: 4px; font-weight: bold; font-family: sans-serif; }
                .cell-controls button:hover { color: #ffffff; background-color: #e06c75; }

                .row { display: flex; gap: 10px; }
                .row-out { margin-top: 10px; display: none; border-top: 1px dashed #3e3e42; padding-top: 10px; } 
                
                .prompt { font-family: Consolas; font-weight: bold; font-size: 13px; width: 65px; text-align: right; flex-shrink: 0; padding-top: 6px; user-select: none; }
                .prompt-in { color: #61afef; }
                .prompt-out { color: #7f8c8d; }
                textarea { flex-grow: 1; background-color: transparent; color: #dcdcaa; border: none; padding: 4px 8px; font-family: Consolas, monospace; font-size: 14px; font-weight: bold; resize: none; overflow: hidden; outline: none; }
                .output-container { flex-grow: 1; overflow-x: auto; padding-top: 6px; font-family: Consolas, monospace;}
            </style>
        </head>
        <body>
            <div id="notebook"></div>
            <script>
                let maxCellId = 0;
                let activeCellId = 1;

                function autoResize(el) {
                    el.style.height = 'auto';
                    el.style.height = (el.scrollHeight) + 'px';
                }

                function handleKey(e, id) {
                    if (e.key === 'Enter' && e.shiftKey) {
                        e.preventDefault();
                        let code = e.target.value;
                        if (code.trim() === '') return;
                        console.log("EXECUTE:" + id + ":" + btoa(unescape(encodeURIComponent(code))));
                    }
                }

                function createCell(id) {
                    if (id > maxCellId) maxCellId = id;
                    activeCellId = id;
                    let html = `
                    <div class='cell' id='cell-${id}'>
                        <div class='cell-controls' id='controls-${id}' style='display: none;'>
                            <button onclick="deleteCell(${id})" title="Delete Cell">×</button>
                        </div>
                        <div class='row'>
                            <div class='prompt prompt-in'>In[${id}]:=</div>
                            <textarea id='input-${id}' rows='1' placeholder='Type math here... (Shift+Enter to run)' oninput='autoResize(this)' onfocus='activeCellId = ${id}' onblur='autoSave()' onkeydown='handleKey(event, ${id})'></textarea>
                        </div>
                        <div class='row row-out' id='row-out-${id}'>
                            <div class='prompt prompt-out'>Out[${id}]=</div>
                            <div class='output-container' id='output-${id}'></div>
                        </div>
                    </div>
                    `;
                    document.getElementById('notebook').insertAdjacentHTML('beforeend', html);
                    let ta = document.getElementById(`input-${id}`);
                    ta.focus();
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }

                function deleteCell(id) {
                    let cell = document.getElementById(`cell-${id}`);
                    if (cell) {
                        cell.remove();
                        
                        // Dynamically update maxCellId so you can safely delete bottom cells
                        let maxFound = 0;
                        document.querySelectorAll('.cell').forEach(c => {
                            let idMatch = c.id ? c.id.match(/cell-(\d+)/) : null;
                            if (idMatch) {
                                let curId = parseInt(idMatch[1]);
                                if (curId > maxFound) maxFound = curId;
                            }
                        });
                        maxCellId = maxFound;
                        
                        if (maxCellId === 0) createCell(1);
                        autoSave();
                    }
                }

                function autoSave() {
                    const state = getNotebookState();
                    console.log("SAVE_STATE:" + btoa(unescape(encodeURIComponent(state))));
                }

                function setOutput(id, b64_html) {
                    try {
                        const html = decodeURIComponent(escape(window.atob(b64_html)));
                        const outDiv = document.getElementById(`output-${id}`);
                        const rowOut = document.getElementById(`row-out-${id}`);
                        
                        if (outDiv) outDiv.innerHTML = html;
                        if (rowOut) rowOut.style.display = 'flex';
                        
                        const controls = document.getElementById(`controls-${id}`);
                        if (controls) controls.style.display = 'block';
                        
                        // Safely check if MathJax is fully initialized to prevent TypeError crashing
                        if (typeof MathJax !== 'undefined' && typeof MathJax.typesetPromise === 'function') {
                            MathJax.typesetPromise([outDiv]).then(() => {
                                if (id >= maxCellId - 1) window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                            }).catch(err => console.error("MathJax Render Error:", err));
                        }
                    } catch (e) {
                        console.error("Output Display Error:", e);
                    }
                    
                    // Always guarantee the next cell exists if we executed the bottom cell
                    if (id === maxCellId) {
                        if (!document.getElementById(`cell-${maxCellId + 1}`)) {
                            createCell(maxCellId + 1);
                        }
                    }
                    autoSave();
                }

                function appendSystemMessage(b64_html) {
                    const html = decodeURIComponent(escape(window.atob(b64_html)));
                    let sysHtml = `
                    <div class='cell' style='border-color: #569cd6; background-color: #1e1e1e;'>
                        <div class='row'>
                            <div class='prompt' style='color: #569cd6;'>Sys:</div>
                            <div class='output-container' style='display: block;'>${html}</div>
                        </div>
                    </div>
                    `;
                    let activeCell = document.getElementById(`cell-${maxCellId}`);
                    if (activeCell) activeCell.insertAdjacentHTML('beforebegin', sysHtml);
                    else document.getElementById('notebook').insertAdjacentHTML('beforeend', sysHtml);
                }

                function updateManipulate(value, cellId, varName, b64Expr) {
                    let lbl = document.getElementById(`val-${varName}-${cellId}`);
                    if(lbl) lbl.innerText = parseFloat(value).toFixed(2);
                    console.log(`MANIPULATE:${cellId}:${varName}:${value}:${b64Expr}`);
                    autoSave();
                }

                function clearNotebook() {
                    document.getElementById('notebook').innerHTML = "";
                    maxCellId = 0;
                    activeCellId = 1;
                    createCell(1);
                    autoSave();
                }

                function getNotebookState() {
                    let cells = [];
                    document.querySelectorAll('.cell').forEach(cell => {
                        let idMatch = cell.id ? cell.id.match(/cell-(\d+)/) : null;
                        if (idMatch) {
                            let id = parseInt(idMatch[1]);
                            let ta = document.getElementById(`input-${id}`);
                            let outDiv = document.getElementById(`output-${id}`);
                            let rowOut = document.getElementById(`row-out-${id}`);

                            cells.push({
                                type: 'code',
                                id: id,
                                input: ta ? ta.value : "",
                                output: outDiv ? outDiv.innerHTML : "",
                                hasOutput: rowOut ? (rowOut.style.display !== 'none' && rowOut.style.display !== '') : false
                            });
                        } else if (cell.querySelector('.prompt') && cell.querySelector('.prompt').innerText === 'Sys:') {
                            let outContainer = cell.querySelector('.output-container');
                            cells.push({
                                type: 'system',
                                content: outContainer ? outContainer.innerHTML : ""
                            });
                        }
                    });
                    return JSON.stringify({
                        maxCellId: maxCellId,
                        cells: cells
                    });
                }

                function restoreNotebookState(b64_state) {
                    const state = JSON.parse(decodeURIComponent(escape(window.atob(b64_state))));
                    document.getElementById('notebook').innerHTML = "";
                    maxCellId = state.maxCellId || 0;
                    activeCellId = maxCellId || 1;
                    
                    if (state.cells && state.cells.length > 0) {
                        state.cells.forEach(c => {
                            if (c.type === 'system') {
                                let sysHtml = `
                                <div class='cell' style='border-color: #569cd6; background-color: #1e1e1e;'>
                                    <div class='row'>
                                        <div class='prompt' style='color: #569cd6;'>Sys:</div>
                                        <div class='output-container' style='display: block;'>${c.content}</div>
                                    </div>
                                </div>
                                `;
                                document.getElementById('notebook').insertAdjacentHTML('beforeend', sysHtml);
                            } else {
                                let id = c.id;
                                let displayStyle = c.hasOutput ? "display: flex;" : "display: none;";
                                let btnStyle = c.hasOutput ? "display: block;" : "display: none;";
                                let html = `
                                <div class='cell' id='cell-${id}'>
                                    <div class='cell-controls' id='controls-${id}' style='${btnStyle}'>
                                        <button onclick="deleteCell(${id})" title="Delete Cell">×</button>
                                    </div>
                                    <div class='row'>
                                        <div class='prompt prompt-in'>In[${id}]:=</div>
                                        <textarea id='input-${id}' rows='1' placeholder='Type math here... (Shift+Enter to run)' oninput='autoResize(this)' onfocus='activeCellId = ${id}' onblur='autoSave()' onkeydown='handleKey(event, ${id})'>${c.input}</textarea>
                                    </div>
                                    <div class='row row-out' id='row-out-${id}' style='${displayStyle}'>
                                        <div class='prompt prompt-out'>Out[${id}]=</div>
                                        <div class='output-container' id='output-${id}'>${c.output}</div>
                                    </div>
                                </div>
                                `;
                                document.getElementById('notebook').insertAdjacentHTML('beforeend', html);
                                let ta = document.getElementById(`input-${id}`);
                                if (ta) autoResize(ta);
                            }
                        });
                    } else if (state.html) {
                        // Backwards compatibility for raw HTML legacy saves
                        document.getElementById('notebook').innerHTML = state.html;
                        document.querySelectorAll('textarea').forEach(ta => {
                            if (ta.hasAttribute('data-value')) {
                                ta.value = ta.getAttribute('data-value');
                                autoResize(ta);
                            }
                        });
                    } else {
                        createCell(1);
                    }
                    
                    if (typeof MathJax !== 'undefined' && typeof MathJax.typesetPromise === 'function') {
                        MathJax.typesetPromise().catch(e => console.error(e));
                    }
                    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
                }

                createCell(1);
            </script>
        </body>
        </html>
        """
        self.browser.setHtml(self.base_html)
        layout.addWidget(self.browser)

    def _save_auto_state(self, ui_state_json_str):
        try:
            settings = QSettings("Mathematica", "IDE")
            settings.setValue("auto_ui_state", ui_state_json_str)
            vars_dict = self.backend.get_user_variables() if hasattr(self.backend, 'get_user_variables') else self.backend.session_vars
            backend_state = {k: str(v) for k, v in vars_dict.items()}
            settings.setValue("auto_backend_state", json.dumps(backend_state))
        except Exception as e: print(f"Failed to auto-save: {e}")

    def _restore_auto_state(self, ok):
        if ok:
            try:
                import sympy
                settings = QSettings("Mathematica", "IDE")
                backend_state_json = settings.value("auto_backend_state", None)
                if backend_state_json:
                    state = json.loads(backend_state_json)
                    self.backend.command_mapping.update({k: sympy.sympify(v_str) for k, v_str in state.items()})
                ui_state_json_str = settings.value("auto_ui_state", None)
                if ui_state_json_str:
                    b64_state = base64.b64encode(ui_state_json_str.encode('utf-8')).decode('utf-8')
                    self.browser.page().runJavaScript(f"restoreNotebookState('{b64_state}');")
            except Exception as e: print(f"Failed to auto-restore: {e}")

    def execute_cell(self, cell_id, code):
        result_html = self.backend.execute(code, cell_id=cell_id)
        if not result_html or not str(result_html).strip():
            result_html = "<span style='color: #666;'><i>(No output)</i></span>"
        b64_html = base64.b64encode(result_html.encode('utf-8')).decode('utf-8')
        self.browser.page().runJavaScript(f"setOutput({cell_id}, '{b64_html}');")

    def update_manipulate(self, cell_id, var_name, var_value, expr_str):
        try:
            old_val = self.backend.command_mapping.get(var_name, None)
            self.backend.command_mapping[var_name] = var_value
            res_html = self.backend.execute(expr_str, cell_id=cell_id)
            if old_val is not None: self.backend.command_mapping[var_name] = old_val
            else: del self.backend.command_mapping[var_name]
            if not res_html or not str(res_html).strip(): res_html = "<i>(No output)</i>"
            b64_html = base64.b64encode(res_html.encode('utf-8')).decode('utf-8')
            js = f"""
            (function() {{
                const display = document.getElementById('manipulate-display-{cell_id}');
                if (display) {{
                    display.innerHTML = decodeURIComponent(escape(window.atob('{b64_html}')));
                    if (typeof MathJax !== 'undefined' && typeof MathJax.typesetPromise === 'function') {{
                        MathJax.typesetPromise([display]).catch(e => console.error(e));
                    }}
                }}
            }})();
            """
            self.browser.page().runJavaScript(js)
        except Exception as e: print(f"Manipulate Error: {e}")

    def show_palette(self, name):
        """Spawns or brings the requested palette to the front."""
        if name == "basic":
            if "basic" not in self.palettes:
                self.palettes["basic"] = BasicMathAssistant(self)
            self.palettes["basic"].show()
            self.palettes["basic"].raise_()
        elif name == "special":
            if "special" not in self.palettes:
                self.palettes["special"] = SpecialCharacters(self)
            self.palettes["special"].show()
            self.palettes["special"].raise_()

    def insert_template(self, text):
        """Inserts text exactly at the active cursor position, gracefully checking focus."""
        b64_text = base64.b64encode(text.encode('utf-8')).decode('utf-8')
        js = f"""
            let ta = document.getElementById(`input-${{activeCellId}}`);
            if (!ta) {{
                ta = document.getElementById(`input-${{maxCellId}}`);
            }}
            if (ta) {{
                let insertText = decodeURIComponent(escape(window.atob('{b64_text}')));
                let start = ta.selectionStart;
                let end = ta.selectionEnd;
                
                if (start === undefined || start === null) {{
                    start = ta.value.length;
                    end = ta.value.length;
                }}
                
                ta.value = ta.value.substring(0, start) + insertText + ta.value.substring(end);
                
                // Advance cursor safely
                ta.selectionStart = ta.selectionEnd = start + insertText.length;
                
                autoResize(ta);
                ta.focus();
            }}
        """
        self.browser.page().runJavaScript(js)

    def evaluate_notebook(self):
        self.output_display_message("<i>Notebook Evaluation Triggered...</i>")
        
    def quit_kernel(self):
        # Full Backend Wipe
        self.backend = MathematicaBackend()
        self.output_display_message("<b style='color: #e06c75;'>Kernel has been restarted. All variables and definitions have been cleared.</b>")
        # Force a DOM state save so variables aren't accidentally restored from old cache
        self.browser.page().runJavaScript("autoSave();")

    def show_message(self, title, msg):
        QMessageBox.information(self, title, msg)
        
    def show_documentation(self):
        """Spawns the native PySide6 Documentation window using QWebEngineView."""
        dlg = DocumentationDialog(self)
        dlg.exec()
        
    def show_syntax_guide(self):
        """Spawns the Syntax & User Guide window."""
        dlg = SyntaxGuideDialog(self)
        dlg.exec()

    def save_session_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Mathematica Notebook", "", "Math Notebook (*.mathnotebook);;All Files (*)")
        if file_path:
            self.current_save_path = file_path
            self.browser.page().runJavaScript("getNotebookState();", self._finish_save_session)

    def _finish_save_session(self, ui_state_json_str):
        try:
            ui_state = json.loads(ui_state_json_str)
            user_vars = self.backend.get_user_variables()
            backend_state = {k: str(v) for k, v in user_vars.items()}
            with open(self.current_save_path, 'w', encoding='utf-8') as f:
                json.dump({"ui_state": ui_state, "backend_state": backend_state}, f, indent=4)
            QMessageBox.information(self, "Success", "Notebook saved successfully!")
        except Exception as e: QMessageBox.critical(self, "Error", f"Failed to save notebook: {str(e)}")

    def load_session_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Mathematica Notebook", "", "Math Notebook (*.mathnotebook);;All Files (*)")
        if file_path:
            try:
                import sympy
                with open(file_path, 'r', encoding='utf-8') as f: data = json.load(f)
                if "backend_state" in data:
                    self.backend.command_mapping.update({k: sympy.sympify(v_str) for k, v_str in data["backend_state"].items()})
                if "ui_state" in data:
                    b64_state = base64.b64encode(json.dumps(data["ui_state"]).encode('utf-8')).decode('utf-8')
                    self.browser.page().runJavaScript(f"restoreNotebookState('{b64_state}');")
                self.output_display_message(f"<i>Loaded notebook from: {file_path.split('/')[-1]}</i>")
            except Exception as e: QMessageBox.critical(self, "Error", f"Failed to load notebook: {str(e)}")

    def export_pdf_dialog(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Export Notebook to PDF", "", "PDF Document (*.pdf)")
        if file_path:
            self.page.pdfPrintingFinished.connect(self._on_pdf_finished)
            self.page.printToPdf(file_path)

    def _on_pdf_finished(self, file_path, success):
        try: self.page.pdfPrintingFinished.disconnect(self._on_pdf_finished)
        except: pass
        if success: QMessageBox.information(self, "Success", f"Notebook exported to PDF:\n{file_path}")

    def output_display_message(self, html_msg):
        b64_html = base64.b64encode(html_msg.encode('utf-8')).decode('utf-8')
        self.browser.page().runJavaScript(f"appendSystemMessage('{b64_html}');")

    def clear_history(self):
        self.browser.page().runJavaScript("clearNotebook();")

    def show_variables(self):
        vars_dict = self.backend.get_user_variables() if hasattr(self.backend, 'get_user_variables') else self.backend.session_vars 
        VariableInspectorDialog(vars_dict, self).exec()
        
    def set_simple_mode(self, enabled):
        """Toggles Simple Mode in the backend engine."""
        self.backend.simple_mode = enabled
        state_msg = "ON" if enabled else "OFF"
        color = "#98c379" if enabled else "#e06c75"
        self.output_display_message(f"<b style='color: {color};'>Simple Mode is now {state_msg}.</b>")