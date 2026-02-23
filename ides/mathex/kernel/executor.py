import ast
import traceback
import sys
import threading
from ides.mathex.language.transpiler import transpile
from ides.mathex.kernel.session import KernelSession
from ides.mathex.kernel.loader import load_and_register
from ides.mathex.language.functions import registry

# ==========================================================
# DEBUGGER ARCHITECTURE
# ==========================================================
class DebugContext:
    """
    Manages the state of the interactive debugger.
    The UI Thread interacts with this object to Step/Resume.
    """
    def __init__(self, line_map, breakpoints):
        self.line_map = line_map          # Map: Python Line -> MATLAB Line
        self.breakpoints = set(breakpoints) # Set of MATLAB Line numbers
        self.paused = False
        self.condition = threading.Condition()
        self.current_locals = {}
        self.command = "continue" # 'step', 'continue', 'quit'
        self.current_ml_line = -1

    def wait_for_user(self):
        """Blocks the execution thread until UI releases it."""
        with self.condition:
            self.paused = True
            # [Protocol] The KernelWorker captures this stdout and updates the UI
            print(f"__DEBUG_PAUSED__:{self.current_ml_line}") 
            
            # Wait for UI to call resume()
            self.condition.wait()
            
            self.paused = False
            return self.command

    def resume(self, cmd="continue"):
        """Called by UI thread (via Session) to unblock execution."""
        with self.condition:
            self.command = cmd
            self.condition.notify()

def _create_trace_func(debug_ctx: DebugContext):
    """
    Creates the hook function for sys.settrace.
    """
    def trace_dispatch(frame, event, arg):
        if event != 'line':
            return trace_dispatch

        # 1. Get current Python line
        py_line = frame.f_lineno
        
        # 2. Map to MATLAB line
        # We only stop if this Python line corresponds to a real User line
        ml_line = debug_ctx.line_map.get(py_line)
        
        if ml_line is not None:
            debug_ctx.current_ml_line = ml_line
            
            # 3. Check Breakpoint OR Step Mode
            should_stop = (ml_line in debug_ctx.breakpoints) or \
                          (debug_ctx.command == 'step')

            if should_stop:
                # Capture variables for Inspector
                debug_ctx.current_locals = frame.f_locals.copy()
                
                # Reset step command so we don't stop on every sub-instruction
                if debug_ctx.command == 'step':
                    debug_ctx.command = 'continue' 
                
                # BLOCK EXECUTION
                cmd = debug_ctx.wait_for_user()
                
                if cmd == 'quit':
                    sys.exit(0) # Abort execution
                    
        return trace_dispatch

    return trace_dispatch

# -----------------------------------------------------------
# MAIN EXECUTOR (UPGRADED)
# -----------------------------------------------------------
def execute(code: str, session: KernelSession, breakpoints: list = None):
    """
    MATLAB execution semantics (PRINT-BASED) with DEBUG SUPPORT.
    
    Args:
        breakpoints (list): List of line numbers (int) to pause at.
    """

    code = code.strip()
    if not code:
        return None

    suppress = code.endswith(";")
    if suppress:
        code = code[:-1].strip()

    tracer = None

    try:
        # Transpile Code to Python
        py, line_map = transpile(code)
        
        # ------------------------------------------------
        # DEBUGGER SETUP
        # ------------------------------------------------
        if breakpoints:
            ctx = DebugContext(line_map, breakpoints)
            # Attach context to session so UI can find it: session.debug_context.resume()
            session.debug_context = ctx 
            tracer = _create_trace_func(ctx)
            sys.settrace(tracer)

        tree = ast.parse(py, mode="exec")

        # ------------------------------------------------
        # FUNCTION DEFINITIONS
        # ------------------------------------------------
        if tree.body and isinstance(tree.body[0], ast.FunctionDef):
            exec(py, session.globals)
            return None

        # ------------------------------------------------
        # FINAL EXPRESSION
        # ------------------------------------------------
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = tree.body[-1]
            body = tree.body[:-1]

            if body:
                exec(
                    compile(ast.Module(body=body, type_ignores=[]), "<ml>", "exec"),
                    session.globals,
                )

            value = eval(
                compile(ast.Expression(last.value), "<ml>", "eval"),
                session.globals,
            )

            # ------------------------------
            # MATLAB COMMAND EXECUTION
            # ------------------------------
            # 1. Check for explicit command flag
            is_cmd = getattr(value, "__mathex_command__", False)

            # 2. Implicit Call Strategy (Variables vs Functions)
            if not is_cmd and callable(value) and isinstance(last.value, ast.Name):
                is_cmd = True

            if callable(value) and is_cmd:
                try:
                    # Check if it is a SCRIPT that needs the workspace
                    if getattr(value, "__mathex_script__", False):
                        value(session.globals)
                    else:
                        # Standard function/command call
                        try:
                            value()
                        except TypeError as e:
                            # Handle "Not enough input arguments" gracefully
                            msg = str(e)
                            if "required" in msg or "missing" in msg or "argument" in msg:
                                print(f"Error: Not enough input arguments.")
                                return None
                            raise e
                            
                    return None
                except Exception as e:
                    raise e

            # ------------------------------
            # PLOTTING CALL (DO NOT PRINT)
            # ------------------------------
            if hasattr(value, "__class__") and value.__class__.__name__.endswith("Handle"):
                session.globals["ans"] = value
                return None

            # ------------------------------
            # NORMAL EXPRESSION
            # ------------------------------
            if value is not None:
                session.globals["ans"] = value
                if not suppress:
                    if isinstance(value, bool):
                        print(f"ans =\n\n  logical\n\n     {1 if value else 0}")
                    elif isinstance(value, list):
                        from shared.symbolic_core.arrays import MatlabArray
                        print(f"ans =\n\n{MatlabArray(value)}")
                    elif hasattr(value, "_data"):
                        print(f"ans =\n\n{value}")
                    else:
                        print(f"ans =\n\n     {value}")
            return None

        # ------------------------------------------------
        # STATEMENTS ONLY
        # ------------------------------------------------
        exec(py, session.globals)

        if (
            not suppress
            and len(tree.body) == 1
            and isinstance(tree.body[0], ast.Assign)
        ):
            target = tree.body[0].targets[0]
            if isinstance(target, ast.Name):
                name = target.id
                val = session.globals.get(name)
                if isinstance(val, bool):
                    print(f"{name} =\n\n  logical\n\n     {1 if val else 0}")
                elif isinstance(val, list):
                    from shared.symbolic_core.arrays import MatlabArray
                    print(f"{name} =\n\n{MatlabArray(val)}")
                elif hasattr(val, "_data"):
                    print(f"{name} =\n\n{val}")
                else:
                    print(f"{name} =\n\n     {val}")

    except NameError as e:
        # Disable tracer during error handling
        if tracer: sys.settrace(None)

        # ==========================================================
        # MAGIC: Auto-Discovery & Lazy Loading
        # ==========================================================
        try:
            var_name = str(e).split("'")[1]
            if load_and_register(var_name):
                entry = registry.get(var_name)
                if entry:
                    session.globals[var_name] = entry.func
                    # Recursively execute now that it's loaded
                    return execute(code, session, breakpoints)
        except Exception:
            pass
        
        # Print Traceback for Devs (stderr)
        traceback.print_exc(file=sys.stderr)

        l_map = locals().get('line_map', {})
        _handle_matlab_error(e, code, l_map)
        return e 

    except Exception as e:
        # Disable tracer on crash
        if tracer: sys.settrace(None)

        # Print Traceback for Devs (stderr)
        traceback.print_exc(file=sys.stderr)

        l_map = locals().get('line_map', {})
        _handle_matlab_error(e, code, l_map)
        return e 
    
    finally:
        # CRITICAL: Always uninstall tracer or the entire Python process will crawl
        if 'tracer' in locals() and tracer:
            sys.settrace(None)
            session.debug_context = None 
    
    return None


def _handle_matlab_error(e, code, line_map=None):
    """
    Translates Python exceptions to MATLAB error messages.
    """
    if line_map is None:
        line_map = {}

    # ------------------------------------------------------------------
    # 1. Determine Location (Line Number Mapping)
    # ------------------------------------------------------------------
    _, _, tb = sys.exc_info()
    py_line = -1
    
    # [UPGRADE] Explicit check for SyntaxError line info
    # SyntaxErrors don't always appear in traceback the same way
    if isinstance(e, SyntaxError) and e.lineno is not None:
        py_line = e.lineno
    else:
        # Standard traceback for runtime errors
        for frame in traceback.extract_tb(tb):
            if frame.filename in ("<ml>", "<string>"):
                py_line = frame.lineno
    
    matlab_line_str = ""
    if py_line > 0:
        m_line = line_map.get(py_line, "?")
        if m_line != "?":
            matlab_line_str = f" (Line {m_line})"

    # ------------------------------------------------------------------
    # 2. User Facing Error Message
    # ------------------------------------------------------------------
    msg = str(e)
    exc_type = type(e).__name__
    
    # [PROTOCOL] The UI parses "Error (Line X):" to highlight the editor
    prefix = f"Error{matlab_line_str}:"

    if "SyntaxError" in exc_type:
        print(f"{prefix} Invalid syntax near '{code.strip()}'")
        return

    if isinstance(e, NameError):
        try:
            var_name = str(e).split("'")[1]
            print(f"{prefix} Undefined function or variable '{var_name}'.")
        except IndexError:
            print(f"{prefix} Undefined function or variable.")
        return

    if isinstance(e, IndexError):
        print(f"{prefix} Index exceeds the number of array elements.")
        return

    if isinstance(e, ValueError):
        if "broadcast" in msg or "shape" in msg:
            print(f"{prefix} Matrix dimensions must agree.")
            return

    print(f"{prefix} {msg}")