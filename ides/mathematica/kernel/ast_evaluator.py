import sympy
from sympy import Atom, Integral, Derivative, Limit

# Keep the step classes here so both engines can use them to identify matrices
from .step_logic import StepDet, StepInv, StepEigenvals

def evaluate_ast(node, context):
    """Recursively evaluates a SymPy AST within a given context."""
    
    # 1. MACRO DETECTION: Steps[...] and NSteps[...]
    if hasattr(node, 'func'):
        if node.func.__name__ == 'Steps':
            return _handle_steps_macro(node.args, context)
        if node.func.__name__ == 'NSteps':
            return _handle_nsteps_macro(node.args, context)

    # 2. SAFETY TRAP: Prevent nesting UI macros inside mathematical equations
    if hasattr(node, 'func') and node.func.__name__ == 'Manipulate':
        raise ValueError("Manipulate[...] must be the outermost command in the cell. It cannot be nested.")

    # 3. Variable Lookup
    if isinstance(node, sympy.Symbol):
        if node.name in context: return context[node.name]
        return node
        
    # 4. ATOM CHECK
    if isinstance(node, Atom): return node

    # 5. Standard Recursion
    if hasattr(node, 'func') and hasattr(node, 'args'):
        evaluated_args = [evaluate_ast(arg, context) for arg in node.args]
        func_name = node.func.__name__
        
        # Context Dispatch
        if func_name in context:
            return context[func_name](*evaluated_args)
        
        return node.func(*evaluated_args)
        
    return node

def _handle_steps_macro(args, context):
    """Macro handler for Steps[...] (English Instructional format)."""
    if not args: return "Usage: Steps[Expression]"
    
    target_node = args[0]
    func_name = target_node.func.__name__ if hasattr(target_node, 'func') else ""
    
    try:
        eval_args = [evaluate_ast(a, context) for a in getattr(target_node, 'args', [])]
        inert_object = None

        if func_name in ['Integrate', 'Integral']:
            inert_object = Integral(*eval_args)
        elif func_name in ['D', 'Diff', 'Derivative']:
            inert_object = Derivative(*eval_args)
        elif func_name in ['Limit']:
            inert_object = Limit(*eval_args)
        elif func_name in ['Det']:
            inert_object = StepDet(eval_args[0])
        elif func_name in ['Inverse']:
            inert_object = StepInv(eval_args[0])
        elif func_name in ['Eigenvalues']:
            inert_object = StepEigenvals(eval_args[0])
        elif func_name in ['Plot', 'Plot3D', 'Manipulate']:
            return f"<span style='color: #e06c75'><b>Step Gen Error:</b> Cannot generate steps for UI or plotting commands.</span>"
        else:
            return f"Steps[...] does not support '{func_name}' yet."

        # Routs specifically to the original instructional step generator
        from .step_logic import generate_steps
        return generate_steps(inert_object)
    except Exception as e:
        return f"<span style='color: #e06c75'><b>Step Gen Error:</b> {str(e)}</span>"


def _handle_nsteps_macro(args, context):
    """Macro handler for NSteps[...] (Formal Mathematical LaTeX format)."""
    if not args: return "Usage: NSteps[Expression]"
    
    target_node = args[0]
    func_name = target_node.func.__name__ if hasattr(target_node, 'func') else ""
    
    try:
        # If it's an algebraic equation (e.g. NSteps[3x^2 + 5x == 0])
        if func_name == 'Eq' or isinstance(target_node, sympy.Rel):
            eval_args = [evaluate_ast(a, context) for a in target_node.args]
            eq = sympy.Eq(*eval_args)
            from .solver_logic import nsteps_mathematica_style
            return nsteps_mathematica_style(eq)
            
        # If it's Calculus or Matrix Ops
        eval_args = [evaluate_ast(a, context) for a in getattr(target_node, 'args', [])]
        inert_object = None

        if func_name in ['Integrate', 'Integral']:
            inert_object = sympy.Integral(*eval_args)
        elif func_name in ['D', 'Diff', 'Derivative']:
            inert_object = sympy.Derivative(*eval_args)
        elif func_name in ['Limit']:
            inert_object = sympy.Limit(*eval_args)
        elif func_name in ['Det']:
            inert_object = StepDet(eval_args[0])
        elif func_name in ['Inverse']:
            inert_object = StepInv(eval_args[0])
        elif func_name in ['Eigenvalues']:
            inert_object = StepEigenvals(eval_args[0])
            
        if inert_object:
            # THIS IS THE FIX: It now securely routes ONLY to the new dedicated mathematical engine
            from .nstep_logic import generate_nsteps
            return generate_nsteps(inert_object)
            
        return f"NSteps[...] does not formally support '{func_name}' yet."

    except Exception as e:
        return f"<span style='color: #e06c75'><b>NStep Gen Error:</b> {str(e)}</span>"