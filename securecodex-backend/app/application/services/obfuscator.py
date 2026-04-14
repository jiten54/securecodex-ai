import ast
import random
import string
import base64
from typing import Dict

class Obfuscator(ast.NodeTransformer):
    """
    Core Obfuscation Engine using Python's AST module.
    Transforms source code to make it difficult to read while preserving logic.
    """

    def __init__(self, level: str = "medium"):
        self.level = level
        self.name_mapping: Dict[str, str] = {}
        self.reserved_names = set(dir(__builtins__) + ["self", "cls", "_scx_decode"])
        self.added_decoder = False

    def _generate_random_name(self, length: int = 8) -> str:
        """Generate a random obfuscated name starting with an underscore."""
        return "_" + "".join(random.choices(string.ascii_letters + string.digits, k=length))

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Rename variables and function calls (if they are local/defined)."""
        if self.level in ["low", "medium", "high"]:
            if node.id not in self.reserved_names:
                if node.id not in self.name_mapping:
                    self.name_mapping[node.id] = self._generate_random_name()
                node.id = self.name_mapping[node.id]
        return self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Rename function names and inject dead code."""
        if self.level in ["low", "medium", "high"]:
            if node.name not in self.reserved_names:
                if node.name not in self.name_mapping:
                    self.name_mapping[node.name] = self._generate_random_name()
                node.name = self.name_mapping[node.name]

        # Dead code injection (High level)
        if self.level == "high":
            dead_code = ast.If(
                test=ast.Constant(value=False),
                body=[ast.Expr(value=ast.Call(
                    func=ast.Name(id="print", ctx=ast.Load()),
                    args=[ast.Constant(value="DEBUG_TRACE_" + self._generate_random_name())],
                    keywords=[]
                ))],
                orelse=[]
            )
            node.body.insert(random.randint(0, len(node.body)), dead_code)

        return self.generic_visit(node)

    def visit_Constant(self, node: ast.Constant) -> ast.AST:
        """Encrypt string literals (Medium/High level)."""
        if isinstance(node.value, str) and self.level in ["medium", "high"]:
            # Skip very short strings or internal markers
            if len(node.value) < 2:
                return node

            encoded_str = base64.b64encode(node.value.encode()).decode()
            self.added_decoder = True
            
            # Replace string with: _scx_decode("base64_string")
            return ast.Call(
                func=ast.Name(id="_scx_decode", ctx=ast.Load()),
                args=[ast.Constant(value=encoded_str)],
                keywords=[]
            )
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        """Obfuscate control flow (High level)."""
        if self.level == "high":
            # Change 'if x' to 'if (True and x)'
            node.test = ast.BoolOp(
                op=ast.And(),
                values=[ast.Constant(value=True), node.test]
            )
        return self.generic_visit(node)

    def obfuscate(self, code: str) -> str:
        """
        Main entry point for obfuscation.
        Parses code, applies transformations, and returns obfuscated source.
        """
        try:
            tree = ast.parse(code)
            transformed_tree = self.visit(tree)
            ast.fix_missing_locations(transformed_tree)
            
            obfuscated_code = ast.unparse(transformed_tree)

            # Add decoder function if strings were encrypted
            if self.added_decoder:
                decoder_func = (
                    "import base64 as _b64\n"
                    "def _scx_decode(s): return _b64.b64decode(s).decode()\n\n"
                )
                obfuscated_code = decoder_func + obfuscated_code

            return obfuscated_code
        except SyntaxError as e:
            raise ValueError(f"Invalid Python code: {str(e)}")
        except Exception as e:
            raise Exception(f"Obfuscation failed: {str(e)}")
