import sympy
from sympy import Eq, latex, Poly, diff
from .common_types import SolutionResult, StepResult

def _build_step_card(title, lines, result):
    """Formats the step-by-step logic into a formal exam-style LaTeX card."""
    html = "<div style='font-family: Consolas; margin: 10px; color: #d4d4d4; text-align: left;'>"
    html += f"<div style='color: #61afef; margin-bottom: 12px; border-bottom: 1px solid #3e3e42; padding-bottom: 4px; font-weight: bold; font-size: 1.1em;'>{title}</div>"
    
    for line in lines:
        html += f"<div style='margin-bottom: 12px;'>{line}</div>"
    
    html += f"""
    <div style='color: #98c379; margin-top: 15px; font-weight: bold; border-top: 1px solid #3e3e42; padding-top: 5px; text-align: left;'>
        Result: \\( \\displaystyle {latex(result)} \\)
    </div>
    </div>
    """
    return StepResult(html)

def solve_mathematica_style(expr, *symbols):
    """
    Implements Mathematica's Solve[expr, vars].
    Auto-detects variables if not provided.
    """
    if not symbols: 
        symbols = tuple(expr.free_symbols)
    
    if not symbols: 
        return "No variables found to solve for."
    
    target = symbols[0]
    
    try:
        sols = sympy.solve(expr, target)
        return SolutionResult([{target: s} for s in sols])
    except:
        if isinstance(expr, Eq):
            expr = expr.lhs - expr.rhs
            
        found_roots = []
        solutions = []
        for guess in range(-5, 6):
            try:
                root = sympy.nsolve(expr, target, guess)
                if not any(abs(root - existing) < 1e-5 for existing in found_roots):
                    found_roots.append(root)
                    solutions.append({target: root})
            except:
                continue
                
        if solutions:
            return SolutionResult(solutions)
            
        return "No symbolic solution found."

def nsolve_mathematica_style(*args):
    """Implements NSolve using sympy.nsolve (Standard behavior)"""
    try:
        res = sympy.nsolve(*args, 0)
        target = args[1] if len(args) > 1 else args[0].free_symbols.pop()
        return SolutionResult([{target: res}])
    except:
        return solve_mathematica_style(*args)

def nsteps_mathematica_style(expr, var=None):
    """
    Implements NSteps as a Formal Step-by-Step Equation Solver.
    Outputs strict mathematical LaTeX without verbose English text.
    """
    if var is None:
        symbols = list(expr.free_symbols)
        if not symbols: return "No variables found."
        var = symbols[0]
        
    if isinstance(expr, Eq):
        lhs, rhs = expr.lhs, expr.rhs
        f = lhs - rhs
    else:
        lhs, rhs = expr, 0
        f = expr

    lines = []
    lines.append(f"\\( \\displaystyle {latex(lhs)} = {latex(rhs)} \\)")
    
    if rhs != 0:
        lines.append(f"\\( \\displaystyle {latex(f)} = 0 \\)")

    try:
        p = Poly(f, var)
        deg = p.degree()
        
        if deg == 1:
            coeffs = p.all_coeffs()
            a, b = coeffs[0], coeffs[1]
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Isolate variable):</div>")
            lines.append(f"\\( \\displaystyle {latex(a)}{var.name} = {latex(-b)} \\)")
            lines.append(f"\\( \\displaystyle {var.name} = \\frac{{{latex(-b)}}}{{{latex(a)}}} \\)")
            res = sympy.simplify(-b/a)
            return _build_step_card("Linear Equation Solution", lines, sympy.Eq(var, res))
            
        elif deg == 2:
            coeffs = p.all_coeffs()
            a, b, c = coeffs[0], coeffs[1], coeffs[2]
            
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Identify coefficients):</div>")
            lines.append(f"\\( a = {latex(a)}, \\; b = {latex(b)}, \\; c = {latex(c)} \\)")
            
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Discriminant \\(\\Delta\\)):</div>")
            disc = sympy.simplify(b**2 - 4*a*c)
            lines.append(f"\\( \\Delta = b^2 - 4ac \\)")
            lines.append(f"\\( \\Delta = ({latex(b)})^2 - 4({latex(a)})({latex(c)}) = {latex(disc)} \\)")
            
            lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 3 (Quadratic Formula):</div>")
            lines.append(f"\\( \\displaystyle {var.name} = \\frac{{-b \\pm \\sqrt{{\\Delta}}}}{{2a}} \\)")
            lines.append(f"\\( \\displaystyle {var.name} = \\frac{{-{latex(b)} \\pm \\sqrt{{{latex(disc)}}}}}{{{latex(2*a)}}} \\)")
            
            res1 = sympy.simplify((-b + sympy.sqrt(disc)) / (2*a))
            res2 = sympy.simplify((-b - sympy.sqrt(disc)) / (2*a))
            
            return _build_step_card("Quadratic Equation Solution", lines, sympy.Eq(var, sympy.FiniteSet(res1, res2)))
    except sympy.polys.polyerrors.PolynomialError:
        pass 

    # Numerical Newton-Raphson Fallback for complex/transcendental equations
    lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 1 (Newton-Raphson Method Formulation):</div>")
    f_prime = diff(f, var)
    lines.append(f"Let \\( f({var.name}) = {latex(f)} \\)")
    lines.append(f"\\( f'({var.name}) = {latex(f_prime)} \\)")
    lines.append(f"\\( \\displaystyle {var.name}_{{n+1}} = {var.name}_n - \\frac{{f({var.name}_n)}}{{f'({var.name}_n)}} \\)")
    
    x_val = 1.0
    lines.append(f"<div style='color: #61afef; font-weight: bold; margin-top: 15px;'>Step 2 (Iteration, starting with \\( {var.name}_0 = 1 \\)):</div>")
    
    for i in range(1, 6):
        fv, dfv = f.subs(var, x_val).evalf(), f_prime.subs(var, x_val).evalf()
        try:
            x_next = x_val - float(fv)/float(dfv)
            lines.append(f"\\( \\displaystyle {var.name}_{i} = {x_val:.5f} - \\frac{{{float(fv):.5f}}}{{{float(dfv):.5f}}} = {x_next:.5f} \\)")
            if abs(x_next - x_val) < 1e-6:
                x_val = x_next
                break
            x_val = x_next
        except TypeError:
            break
            
    try: 
        final_res = sympy.nsolve(f, var, 1.0)
    except: 
        final_res = x_val 
        
    return _build_step_card("Numerical Root Search", lines, sympy.Eq(var, final_res))