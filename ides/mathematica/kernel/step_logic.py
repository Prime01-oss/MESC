import sympy
from sympy import latex, Integral, Derivative, Limit, Symbol, Basic, S, oo, zoo, nan
from sympy.integrals.manualintegrate import integral_steps
from .common_types import StepResult

# --- INERT CLASSES FOR MATRIX MACROS ---
class StepDet:
    def __init__(self, mat): self.mat = mat
class StepInv:
    def __init__(self, mat): self.mat = mat
class StepEigenvals:
    def __init__(self, mat): self.mat = mat

# =========================================================================
# --- INSTRUCTIONAL / ENGLISH STEPS (Steps[] Implementation) ---
# =========================================================================

def generate_steps(expr):
    """Universal Entry Point for Steps[...]"""
    if isinstance(expr, Integral):
        return _generate_integral_steps(expr)
    elif isinstance(expr, Derivative):
        return _generate_derivative_steps(expr)
    elif isinstance(expr, Limit):
        return _generate_limit_steps(expr)
    elif isinstance(expr, StepDet):
        return _generate_det_steps(expr)
    elif isinstance(expr, StepInv):
        return _generate_inv_steps(expr)
    elif isinstance(expr, StepEigenvals):
        return _generate_eigenvals_steps(expr)
    else:
        return StepResult(f"<span style='color: #e06c75'>Steps not available for {type(expr).__name__} yet.</span>")

def _gauss_jordan_steps(mat, lines):
    n = mat.shape[0]
    aug = mat.row_join(sympy.eye(n))
    lines.append(f"<b>Augmented Matrix \\([A | I]\\):</b><br> \\({latex(aug)}\\)")
    for c in range(n):
        if aug[c, c] == 0:
            for r in range(c+1, n):
                if aug[r, c] != 0:
                    aug.row_swap(c, r)
                    lines.append(f"<b>Swap Row {c+1} and Row {r+1}:</b> \\(R_{c+1} \\leftrightarrow R_{r+1}\\)")
                    lines.append(f"\\({latex(aug)}\\)")
                    break
            if aug[c, c] == 0:
                lines.append("<span style='color: #e06c75'>Matrix is singular!</span>")
                return None
        pivot = aug[c, c]
        if pivot != 1:
            aug.row_op(c, lambda v, j: sympy.simplify(v / pivot))
            lines.append(f"<b>Normalize Pivot:</b> \\(R_{c+1} \\to \\frac{{1}}{{{latex(pivot)}}} R_{c+1}\\)")
            lines.append(f"\\({latex(aug)}\\)")
        eliminated = False
        for r in range(n):
            if r != c and aug[r, c] != 0:
                factor = aug[r, c]
                aug.row_op(r, lambda v, j: sympy.simplify(v - factor * aug[c, j]))
                lines.append(f"<b>Eliminate:</b> \\(R_{r+1} \\to R_{r+1} - ({latex(factor)}) R_{c+1}\\)")
                eliminated = True
        if eliminated:
            lines.append(f"\\({latex(aug)}\\)")
    inv = aug[:, n:]
    lines.append(f"<b>Extract right side for Inverse:</b><br> \\({latex(inv)}\\)")
    return inv

def _generate_det_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color: #e06c75'>Matrix must be square to compute a determinant.</span>")
        if mat.shape == (1, 1): lines.append("Determinant of a 1x1 matrix is just the element itself.")
        elif mat.shape == (2, 2):
            a, b, c, d = mat[0,0], mat[0,1], mat[1,0], mat[1,1]
            lines.append("<b>Formula for 2x2 Determinant:</b> \\(ad - bc\\)")
            lines.append(f"\\( = ({latex(a)})({latex(d)}) - ({latex(b)})({latex(c)}) \\)")
        elif mat.shape == (3, 3):
            lines.append("<b>Cofactor Expansion along Row 1:</b>")
            lines.append(f"\\( = {latex(mat[0,0])} \\cdot \\det\\begin{{pmatrix}} {latex(mat[1,1])} & {latex(mat[1,2])} \\\\ {latex(mat[2,1])} & {latex(mat[2,2])} \\end{{pmatrix}} " +
                         f"- {latex(mat[0,1])} \\cdot \\det\\begin{{pmatrix}} {latex(mat[1,0])} & {latex(mat[1,2])} \\\\ {latex(mat[2,0])} & {latex(mat[2,2])} \\end{{pmatrix}} " +
                         f"+ {latex(mat[0,2])} \\cdot \\det\\begin{{pmatrix}} {latex(mat[1,0])} & {latex(mat[1,1])} \\\\ {latex(mat[2,0])} & {latex(mat[2,1])} \\end{{pmatrix}} \\)")
        else: lines.append(f"<b>Computing determinant for {mat.shape[0]}x{mat.shape[1]} matrix using row reduction / cofactor expansion...</b>")
        return _build_card(f"Determinant Steps for \\({latex(mat)}\\)", lines, mat.det())
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Det Step Error: {str(e)}</span>")

def _generate_inv_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color: #e06c75'>Matrix must be square to be inverted.</span>")
        det = mat.det()
        lines.append(f"<b>Step 1: Compute the Determinant (\\(|A|\\))</b>")
        lines.append(f"\\(|A| = {latex(det)}\\)")
        if det == 0:
            lines.append("<span style='color: #e06c75'>The determinant is 0. The matrix is singular and cannot be inverted.</span>")
            return _build_card(f"Inverse Steps for \\({latex(mat)}\\)", lines, "Undefined")
        if mat.shape == (2, 2):
            a, b, c, d = mat[0,0], mat[0,1], mat[1,0], mat[1,1]
            lines.append("<b>Step 2: Swap the main diagonal, negate the off-diagonal</b>")
            adj = sympy.Matrix([[d, -b], [-c, a]])
            lines.append(f"Adjugate Matrix = \\({latex(adj)}\\)")
            lines.append("<b>Step 3: Multiply by \\(\\frac{1}{|A|}\\)</b>")
        else:
            lines.append("<b>Step 2: Augment with Identity Matrix and apply Gauss-Jordan Elimination</b>")
            _gauss_jordan_steps(mat, lines)
        return _build_card(f"Inverse Steps for \\({latex(mat)}\\)", lines, mat.inv())
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Inverse Step Error: {str(e)}</span>")

def _generate_eigenvals_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color: #e06c75'>Matrix must be square to find eigenvalues.</span>")
        lam = sympy.Symbol('\\lambda')
        n = mat.shape[0]
        I = sympy.eye(n)
        char_mat = mat - lam * I
        lines.append(f"<b>Step 1: Set up the Characteristic Equation</b> \\(|A - \\lambda I| = 0\\)")
        lines.append(f"\\( A - \\lambda I = {latex(char_mat)} \\)")
        char_poly = char_mat.det()
        lines.append(f"<b>Step 2: Compute the Determinant</b>")
        lines.append(f"Characteristic Polynomial: \\( {latex(char_poly)} = 0 \\)")
        roots = sympy.solve(char_poly, lam)
        lines.append(f"<b>Step 3: Solve for \\(\\lambda\\)</b>")
        if not roots: lines.append("No explicit analytical roots found.")
        else: lines.append(f"Roots (Eigenvalues): \\( \\lambda \\in \\{{ {', '.join([latex(r) for r in roots])} \\}} \\)")
        final_res = sympy.Matrix(list(mat.eigenvals().keys())) 
        return _build_card(f"Eigenvalue Steps for \\({latex(mat)}\\)", lines, final_res)
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Eigenvalue Step Error: {str(e)}</span>")

def _generate_integral_steps(expr):
    try:
        integrand = expr.function
        symbol = expr.limits[0][0]
        rule = integral_steps(integrand, symbol)
        printer = IntegralStepPrinter(symbol)
        lines = printer.print_steps(rule)
        final_res = sympy.integrate(integrand, symbol)
        return _build_card(f"Integration Steps for \\({latex(integrand)}\\)", lines, final_res, "+ C")
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Integration Step Error: {str(e)}</span>")

def _generate_derivative_steps(expr):
    try:
        current_expr = expr.expr
        symbols = expr.variables
        lines = []
        for i, symbol in enumerate(symbols):
            if len(symbols) > 1: lines.append(f"<br><b style='color:#c678dd;'>Step {i+1}: Partial derivative w.r.t \\({latex(symbol)}\\)</b>")
            _walk_derivative(current_expr, symbol, lines)
            current_expr = sympy.diff(current_expr, symbol)
            if len(symbols) > 1 and i < len(symbols) - 1: lines.append(f"<i style='color:#7f8c8d;'>Intermediate result: \\({latex(current_expr)}\\)</i>")
        title = f"Derivative Steps for \\({latex(expr.expr)}\\)"
        if len(symbols) > 1: title = f"Partial Derivative Steps for \\({latex(expr.expr)}\\)"
        return _build_card(title, lines, current_expr)
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Derivative Step Error: {str(e)}</span>")

def _walk_derivative(expr, symbol, lines, depth=0):
    indent = "&nbsp;" * (depth * 4)
    if not expr.has(symbol):
        lines.append(f"{indent}Derivative of constant \\({latex(expr)}\\) w.r.t \\({latex(symbol)}\\) is 0.")
        return
    if expr.is_Pow and expr.base == symbol and not expr.exp.has(symbol):
        n = expr.exp
        lines.append(f"{indent}<b>Power Rule:</b> \\(\\frac{{d}}{{d{symbol}}} ({latex(expr)}) = {latex(n)}{symbol}^{{{latex(n-1)}}} \\)")
        return
    if expr.is_Add:
        lines.append(f"{indent}<b>Sum Rule:</b> Differentiate term-by-term:")
        for arg in expr.args: _walk_derivative(arg, symbol, lines, depth + 1)
        return
    if expr.is_Mul:
        constants = [a for a in expr.args if not a.has(symbol)]
        functions = [a for a in expr.args if a.has(symbol)]
        if constants and functions:
            c = sympy.Mul(*constants)
            f = sympy.Mul(*functions)
            lines.append(f"{indent}<b>Constant Multiple Rule:</b> Factor out constant \\({latex(c)}\\)")
            lines.append(f"{indent}Compute: \\( {latex(c)} \\times \\frac{{d}}{{d{symbol}}}({latex(f)}) \\)")
            _walk_derivative(f, symbol, lines, depth + 1)
            return
        elif len(functions) >= 2:
            u, v = functions[0], sympy.Mul(*functions[1:])
            lines.append(f"{indent}<b>Product Rule:</b> \\(\\frac{{d}}{{d{symbol}}}(uv) = u'v + uv'\\)")
            lines.append(f"{indent}- Let \\(u = {latex(u)}\\), \\(v = {latex(v)}\\)")
            _walk_derivative(u, symbol, lines, depth + 1)
            _walk_derivative(v, symbol, lines, depth + 1)
            return
    if hasattr(expr, 'args') and expr.args:
        arg = expr.args[0]
        if arg.has(symbol) and len(expr.args) == 1:
            lines.append(f"{indent}<b>Chain Rule</b> for \\({latex(expr)}\\):")
            dummy_u = sympy.Symbol('u')
            outer_diff = expr.func(dummy_u).diff(dummy_u).subs(dummy_u, arg)
            lines.append(f"{indent}- Differentiate outer function w.r.t inner: \\(\\rightarrow {latex(outer_diff)}\\)")
            lines.append(f"{indent}- Multiply by derivative of inner function \\({latex(arg)}\\):")
            _walk_derivative(arg, symbol, lines, depth + 1)
            return
    lines.append(f"{indent}Compute \\(\\frac{{d}}{{d{symbol}}} {latex(expr)}\\)")

def _generate_limit_steps(expr):
    try:
        f, x, a = expr.args[0], expr.args[1], expr.args[2]
        lines = []
        try:
            val_at_a = f.subs(x, a)
            if val_at_a.is_finite:
                lines.append(f"<b>Direct Substitution:</b> Substitute \\({latex(x)} \\to {latex(a)}\\).")
                lines.append(f"Result: \\({latex(val_at_a)}\\)")
                return _build_card(f"Limit of \\({latex(f)}\\)", lines, val_at_a)
        except: pass
        num, den = f.as_numer_denom()
        val_num, val_den = num.subs(x, a), den.subs(x, a)
        lines.append(f"Check limit type at \\({latex(x)} \\to {latex(a)}\\):")
        lines.append(f"Numerator \\(\\to {latex(val_num)}\\), Denominator \\(\\to {latex(val_den)}\\)")
        if val_num == 0 and val_den == 0:
            lines.append(f"Indeterminate form \\(0/0\\). Apply <b>L'Hôpital's Rule</b>.")
            lines.append(f"Differentiate Num and Denom:")
            lines.append(f"\\(\\lim \\frac{{{latex(num.diff(x))}}}{{{latex(den.diff(x))}}}\\)")
        elif val_den == 0 and val_num != 0:
            lines.append("Denominator is 0, Numerator is non-zero. Limit is likely \\(\\infty\\) or undefined.")
        return _build_card(f"Limit Steps for \\({latex(f)}\\)", lines, expr.doit())
    except Exception as e: return StepResult(f"<span style='color: #e06c75'>Limit Step Error: {str(e)}</span>")

def _build_card(title, lines, result, suffix=""):
    html = "<div style='font-family: Consolas; margin: 10px;'>"
    html += f"<div style='color: #61afef; margin-bottom: 8px; border-bottom: 1px solid #3e3e42; padding-bottom: 4px;'><b>{title}</b></div>"
    for idx, line in enumerate(lines):
        html += f"<div style='color: #d4d4d4; margin-bottom: 6px; padding-left: 10px; border-left: 2px solid #444;'>{idx+1}. {line}</div>"
    html += f"<div style='color: #98c379; margin-top: 15px; font-weight: bold; border-top: 1px solid #3e3e42; padding-top: 5px; text-align: left;'>Result: \\( \\displaystyle {latex(result)} {suffix} \\)</div></div>"
    return StepResult(html)

class IntegralStepPrinter:
    def __init__(self, symbol): self.symbol = symbol
    def print_steps(self, rule):
        self.lines = []
        self._walk(rule)
        return self.lines
    def _walk(self, rule):
        name = rule.__class__.__name__
        if name == 'PowerRule':
            b, e = getattr(rule, 'base', 'x'), getattr(rule, 'exp', 'n')
            self.lines.append(f"Apply <b>Power Rule</b>: \\(\\int {b}^{{{e}}} d{self.symbol} = \\frac{{{b}^{{{e}+1}}}}{{{e}+1}}\\)")
        elif name == 'AddRule':
            self.lines.append("Integrate term-by-term:")
            for sub in getattr(rule, 'substeps', []): self._walk(sub)
        elif name == 'ConstantTimesRule':
            c = getattr(rule, 'constant', 'c')
            self.lines.append(f"Factor out constant \\({latex(c)}\\):")
            if hasattr(rule, 'substep'): self._walk(rule.substep)
        elif name == 'URule':
            u_func = getattr(rule, 'u_func', 'f(x)')
            self.lines.append(f"<b>Substitution:</b> Let \\(u = {latex(u_func)}\\).")
            if hasattr(rule, 'substep'): self._walk(rule.substep)
            self.lines.append("Substitute back \\(u\\).")
        elif name == 'PartsRule':
             self.lines.append(f"<b>Integration by Parts:</b> \\(\\int u dv = uv - \\int v du\\)")
             if hasattr(rule, 'second_step'): self._walk(rule.second_step) 
        else:
            self.lines.append(f"Apply <b>{name.replace('Rule','')}</b>")
            if hasattr(rule, 'substep'): self._walk(rule.substep)


# =========================================================================
# --- FORMAL MATHEMATICAL STEPS (NSteps Implementation) ---
# =========================================================================

def generate_nsteps(expr):
    """Universal Entry Point for NSteps[] (Math-styled formatting)"""
    if isinstance(expr, Integral):
        return _generate_formal_integral_steps(expr)
    elif isinstance(expr, Derivative):
        return _generate_formal_derivative_steps(expr)
    elif isinstance(expr, Limit):
        return _generate_formal_limit_steps(expr)
    elif isinstance(expr, StepDet):
        return _generate_formal_det_steps(expr)
    elif isinstance(expr, StepInv):
        return _generate_formal_inv_steps(expr)
    elif isinstance(expr, StepEigenvals):
        return _generate_formal_eigenvals_steps(expr)
    else:
        # Ultimate fallback
        return generate_steps(expr)

def _build_formal_card(title, lines, result, suffix=""):
    """Creates a beautiful, strict mathematical exam-style box."""
    html = "<div style='font-family: Consolas; margin: 10px; color: #d4d4d4; text-align: left;'>"
    if title:
        html += f"<div style='color: #61afef; margin-bottom: 12px; border-bottom: 1px solid #3e3e42; padding-bottom: 4px; font-weight: bold; font-size: 1.1em;'>{title}</div>"
    
    for line in lines:
        html += f"<div style='margin-bottom: 12px;'>{line}</div>"
    
    html += f"""
    <div style='color: #98c379; margin-top: 15px; font-weight: bold; border-top: 1px solid #3e3e42; padding-top: 5px; text-align: left;'>
        Result: \\( \\displaystyle {latex(result)} {suffix} \\)
    </div>
    </div>
    """
    return StepResult(html)

# --- FORMAL DERIVATIVES ---
def _generate_formal_derivative_steps(expr):
    try:
        current_expr = expr.expr
        symbols = expr.variables
        lines = []
        
        for i, symbol in enumerate(symbols):
            if len(symbols) > 1:
                lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step {i+1} (Partial Derivative w.r.t \\( {latex(symbol)} \\)):</div>")
            else:
                lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Differentiate w.r.t \\( {latex(symbol)} \\)):</div>")
                
            lines.append(f"\\( \\displaystyle \\frac{{d}}{{d{latex(symbol)}}} \\left[ {latex(current_expr)} \\right] \\)")
            
            # Identify high-level rules mathematically
            if current_expr.is_Add:
                parts = [f"\\frac{{d}}{{d{latex(symbol)}}}\\left({latex(arg)}\\right)" for arg in current_expr.args]
                lines.append(f"\\( \\displaystyle = {' + '.join(parts)} \\)")
            elif current_expr.is_Mul:
                lines.append(f"\\( \\text{{Apply Product/Constant Rules}} \\)")
            elif hasattr(current_expr, 'args') and current_expr.args and current_expr.args[0] != symbol:
                lines.append(f"\\( \\text{{Apply Chain Rule: }} \\frac{{d}}{{dx}} f(g(x)) = f'(g(x)) \\cdot g'(x) \\)")
                
            current_expr = sympy.diff(current_expr, symbol)
            lines.append(f"\\( \\displaystyle = {latex(current_expr)} \\)")
            
        title = "Differentiation" if len(symbols) == 1 else "Partial Differentiation"
        return _build_formal_card(title, lines, current_expr)
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Derivative Step Error: {str(e)}</span>")

# --- FORMAL LIMITS ---
def _generate_formal_limit_steps(expr):
    try:
        f = expr.args[0]
        x = expr.args[1]
        a = expr.args[2]
        lines = []
        
        lines.append(f"Evaluate: \\( \\displaystyle \\lim_{{{latex(x)} \\to {latex(a)}}} {latex(f)} \\)")
        
        num, den = f.as_numer_denom()
        
        if den == 1:
            val = f.subs(x, a)
            if val.is_finite:
                lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Direct Substitution):</div>")
                lines.append(f"\\( \\displaystyle = {latex(val)} \\)")
                return _build_formal_card("Limit Evaluation", lines, expr.doit())

        val_num = num.subs(x, a)
        val_den = den.subs(x, a)
        
        lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Test Substitution \\( {latex(x)} = {latex(a)} \\)):</div>")
        lines.append(f"\\( \\displaystyle \\to \\frac{{{latex(val_num)}}}{{{latex(val_den)}}} \\)")
        
        if val_num == 0 and val_den == 0:
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (L'Hôpital's Rule):</div>")
            lines.append(f"Apply rule for indeterminate form \\(\\frac{{0}}{{0}}\\):")
            lines.append(f"\\( \\displaystyle \\lim_{{{latex(x)} \\to {latex(a)}}} \\frac{{\\frac{{d}}{{d{latex(x)}}}({latex(num)})}}{{\\frac{{d}}{{d{latex(x)}}}({latex(den)})}} \\)")
            
            dnum = num.diff(x)
            dden = den.diff(x)
            lines.append(f"\\( \\displaystyle = \\lim_{{{latex(x)} \\to {latex(a)}}} \\frac{{{latex(dnum)}}}{{{latex(dden)}}} \\)")
            
            val2 = (dnum/dden).subs(x, a)
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 3 (Substitute):</div>")
            lines.append(f"\\( \\displaystyle = {latex(val2)} \\)")
            
        final_res = expr.doit()
        return _build_formal_card("Limit Evaluation", lines, final_res)
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Limit Step Error: {str(e)}</span>")

# --- FORMAL MATRICES ---
def _generate_formal_det_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color:#e06c75'>Matrix must be square.</span>")
            
        lines.append(f"\\( \\displaystyle A = {latex(mat)} \\)")
        
        if mat.shape == (2,2):
            a, b, c, d = mat[0,0], mat[0,1], mat[1,0], mat[1,1]
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (2x2 Determinant Formula):</div>")
            lines.append(f"\\( \\displaystyle \\det(A) = ad - bc \\)")
            lines.append(f"\\( \\displaystyle \\det(A) = ({latex(a)})({latex(d)}) - ({latex(b)})({latex(c)}) \\)")
        elif mat.shape == (3,3):
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Cofactor Expansion along Row 1):</div>")
            lines.append(f"\\( \\displaystyle \\det(A) = {latex(mat[0,0])} \\begin{{vmatrix}} {latex(mat[1,1])} & {latex(mat[1,2])} \\\\ {latex(mat[2,1])} & {latex(mat[2,2])} \\end{{vmatrix}} " +
                         f"- {latex(mat[0,1])} \\begin{{vmatrix}} {latex(mat[1,0])} & {latex(mat[1,2])} \\\\ {latex(mat[2,0])} & {latex(mat[2,2])} \\end{{vmatrix}} " +
                         f"+ {latex(mat[0,2])} \\begin{{vmatrix}} {latex(mat[1,0])} & {latex(mat[1,1])} \\\\ {latex(mat[2,0])} & {latex(mat[2,1])} \\end{{vmatrix}} \\)")
            
            d1 = mat[1,1]*mat[2,2] - mat[1,2]*mat[2,1]
            d2 = mat[1,0]*mat[2,2] - mat[1,2]*mat[2,0]
            d3 = mat[1,0]*mat[2,1] - mat[1,1]*mat[2,0]
            
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Evaluate Minors):</div>")
            lines.append(f"\\( \\displaystyle \\det(A) = {latex(mat[0,0])}({latex(d1)}) - ({latex(mat[0,1])})({latex(d2)}) + ({latex(mat[0,2])})({latex(d3)}) \\)")
            
        return _build_formal_card("Determinant Evaluation", lines, mat.det())
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Det Step Error: {str(e)}</span>")

def _generate_formal_inv_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color:#e06c75'>Matrix must be square.</span>")
            
        det = mat.det()
        lines.append(f"\\( \\displaystyle A = {latex(mat)} \\)")
        lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Find Determinant):</div>")
        lines.append(f"\\( \\displaystyle \\det(A) = {latex(det)} \\)")
        
        if det == 0:
            lines.append(f"\\( \\displaystyle \\det(A) = 0 \\implies A^{{-1}} \\text{{ does not exist.}} \\)")
            return _build_formal_card("Inverse Matrix", lines, "Undefined")
            
        if mat.shape == (2,2):
            a, b, c, d = mat[0,0], mat[0,1], mat[1,0], mat[1,1]
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Adjugate Formula):</div>")
            lines.append(f"\\( \\displaystyle A^{{-1}} = \\frac{{1}}{{\\det(A)}} \\begin{{pmatrix}} d & -b \\\\ -c & a \\end{{pmatrix}} \\)")
            adj = sympy.Matrix([[d, -b], [-c, a]])
            lines.append(f"\\( \\displaystyle A^{{-1}} = \\frac{{1}}{{{latex(det)}}} {latex(adj)} \\)")
        else:
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Row Reduction / Gauss-Jordan):</div>")
            aug = mat.row_join(sympy.eye(mat.shape[0]))
            lines.append(f"\\( \\displaystyle [A | I] = {latex(aug)} \\)")
            lines.append(f"\\( \\displaystyle \\dots \\xrightarrow{{\\text{{Row Operations}}}} \\dots \\)")
            lines.append(f"\\( \\displaystyle [I | A^{{-1}}] = {latex(mat.inv().row_join(sympy.eye(mat.shape[0]))[:,mat.shape[0]:])} \\)")
            
        return _build_formal_card("Inverse Matrix", lines, mat.inv())
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Inverse Step Error: {str(e)}</span>")

def _generate_formal_eigenvals_steps(expr):
    try:
        mat = expr.mat
        lines = []
        if not hasattr(mat, 'is_square') or not mat.is_square:
            return StepResult("<span style='color:#e06c75'>Matrix must be square.</span>")
            
        lam = sympy.Symbol('\\lambda')
        I = sympy.eye(mat.shape[0])
        char_mat = mat - lam * I
        
        lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Characteristic Equation):</div>")
        lines.append(f"\\( \\displaystyle \\det(A - \\lambda I) = 0 \\)")
        lines.append(f"\\( \\displaystyle A - \\lambda I = {latex(char_mat)} \\)")
        
        char_poly = char_mat.det()
        lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Evaluate Determinant):</div>")
        lines.append(f"\\( \\displaystyle {latex(char_poly)} = 0 \\)")
        
        roots = sympy.solve(char_poly, lam)
        lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 3 (Solve for \\(\\lambda\\)):</div>")
        lines.append(f"\\( \\displaystyle \\lambda \\in \\{{ {', '.join([latex(r) for r in roots])} \\}} \\)")
        
        res = sympy.Matrix(list(mat.eigenvals().keys()))
        return _build_formal_card("Eigenvalues", lines, res)
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Eigenvalue Step Error: {str(e)}</span>")

# --- FORMAL INTEGRALS ---
def _generate_formal_integral_steps(expr):
    """Outputs formal LaTeX steps exactly like handwritten math."""
    try:
        from sympy.integrals.manualintegrate import integral_steps
        integrand = expr.function
        symbol = expr.limits[0][0]
        rule = integral_steps(integrand, symbol)
        
        lines = []
        lines.append(f"\\( \\displaystyle \\int {latex(integrand)} \\, d{symbol} \\)")
        
        printer = FormalIntegralStepPrinter(symbol)
        step_lines = printer.print_steps(rule)
        lines.extend(step_lines)
        
        final_res = sympy.integrate(integrand, symbol)
        
        html = "<div style='font-family: Consolas; margin: 10px; color: #d4d4d4; text-align: left;'>"
        for line in lines:
            html += f"<div style='margin-bottom: 12px;'>{line}</div>"
        
        html += f"""
        <div style='color: #98c379; margin-top: 15px; font-weight: bold; border-top: 1px solid #3e3e42; padding-top: 5px; text-align: left;'>
            Result: \\( \\displaystyle \\int {latex(integrand)} \\, d{symbol} = {latex(final_res)} + C \\)
        </div>
        </div>
        """
        return StepResult(html)
    except Exception as e:
        return StepResult(f"<span style='color: #e06c75'>Integration Step Error: {str(e)}</span>")

class FormalIntegralStepPrinter:
    def __init__(self, symbol):
        self.symbol = symbol
        self.lines = []
        self.step_num = 1

    def print_steps(self, rule):
        self.lines = []
        self._walk(rule)
        return self.lines

    def _walk(self, rule):
        if not rule: return
        name = rule.__class__.__name__
        
        if name == 'PartsRule':
            u, dv = rule.u, rule.dv
            du = sympy.diff(u, self.symbol)
            v = sympy.integrate(dv, self.symbol)
            orig_int = sympy.Integral(u * dv, self.symbol)
            new_int = sympy.Integral(v * du, self.symbol)
            
            self.lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 20px;'>Step {self.step_num} (Integration by parts):</div>")
            self.step_num += 1
            
            self.lines.append(f"Let \\( u = {latex(u)}, \\; dv = {latex(dv)} \\, d{self.symbol} \\)")
            self.lines.append(f"\\( du = {latex(du)} \\, d{self.symbol}, \\; v = {latex(v)} \\)")
            self.lines.append(f"\\( \\displaystyle {latex(orig_int)} = {latex(u*v)} - {latex(new_int)} \\)")
            
            if hasattr(rule, 'second_step'): self._walk(rule.second_step)
                
        elif name == 'URule':
            u_var = getattr(rule, 'u_var', sympy.Symbol('u'))
            u_func = rule.u_func
            du_dx = sympy.diff(u_func, self.symbol)
            
            self.lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 20px;'>Step {self.step_num} (Substitution):</div>")
            self.step_num += 1
            
            self.lines.append(f"Let \\( {latex(u_var)} = {latex(u_func)} \\)")
            self.lines.append(f"\\( d{latex(u_var)} = ({latex(du_dx)}) \\, d{self.symbol} \\)")
            
            if hasattr(rule, 'substep'): self._walk(rule.substep)
            self.lines.append(f"Substitute back \\( {latex(u_var)} = {latex(u_func)} \\).")
                
        elif name == 'AlternativeRule':
            if hasattr(rule, 'alternatives') and rule.alternatives:
                self._walk(rule.alternatives[0])
                
        elif name == 'ConstantTimesRule':
            if hasattr(rule, 'substep'): self._walk(rule.substep)
                
        elif name == 'AddRule':
            if hasattr(rule, 'substeps'):
                for sub in rule.substeps: self._walk(sub)
        else:
            if hasattr(rule, 'substep'): self._walk(rule.substep)