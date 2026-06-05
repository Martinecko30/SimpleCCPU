import re

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class FuncDecl(ASTNode):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params
        self.body = body

# === STATEMENTS ===
class Let(ASTNode):
    def __init__(self, name, value_expr):
        self.name = name
        self.value_expr = value_expr

class ArrayDecl(ASTNode):
    def __init__(self, name, size):
        self.name = name
        self.size = size

class Assign(ASTNode):
    def __init__(self, target, value_expr):
        self.target = target
        self.value_expr = value_expr

class If(ASTNode):
    def __init__(self, condition, true_body, false_body):
        self.condition = condition
        self.true_body = true_body
        self.false_body = false_body

class While(ASTNode):
    def __init__(self, condition, body):
        self.condition = condition
        self.body = body

class CallStmt(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Return(ASTNode):
    def __init__(self, value_expr):
        self.value_expr = value_expr

class Putc(ASTNode):
    def __init__(self, value_expr):
        self.value_expr = value_expr

# === EXPRESSIONS ===
class BinOp(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class CallExpr(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Variable(ASTNode):
    def __init__(self, name):
        self.name = name

class Number(ASTNode):
    def __init__(self, value):
        self.value = value

class ArrayAccess(ASTNode):
    def __init__(self, name, index_expr):
        self.name = name
        self.index_expr = index_expr

class AddressOf(ASTNode):
    def __init__(self, name):
        self.name = name

class Dereference(ASTNode):
    def __init__(self, name):
        self.name = name


class MinilangParser:
    def __init__(self, source_code: str):
        self.lines = []
        for line in source_code.split('\n'):
            line = line.split('//')[0].strip()
            if line:
                self.lines.append(line)
        self.pos = 0

    def _current_line(self):
        return self.lines[self.pos] if self.pos < len(self.lines) else None

    def parse(self):
        statements = self._parse_block(end_tokens=[])
        return Program(statements)

    def _parse_block(self, end_tokens):
        statements = []

        while self.pos < len(self.lines):
            line = self._current_line()
            tokens = line.split()
            command = tokens[0]

            if command in end_tokens:
                break

            self.pos += 1

            if command == "ARRAY":
                match = re.match(r"ARRAY\s+(\w+)\[(\d+)\]", line)
                statements.append(
                    ArrayDecl(match.group(1), int(match.group(2))))

            elif command == "LET" and tokens[2] == "=":
                var_name = tokens[1]
                value_expr = self._parse_expression(" ".join(tokens[3:]))
                statements.append(Let(var_name, value_expr))

            elif command == "FUNC":
                match = re.match(r"FUNC\s+(\w+)\s*\((.*)\)", line)
                func_name = match.group(1)
                params = [p.strip() for p in
                          match.group(2).split(',')] if match.group(
                    2).strip() else []

                body = self._parse_block(['ENDFUNC'])
                self.pos += 1
                statements.append(FuncDecl(func_name, params, body))

            elif command == "WHILE":
                cond_expr = self._parse_operand(tokens[1])
                body = self._parse_block(['END'])
                self.pos += 1
                statements.append(While(cond_expr, body))

            elif command == "IF":
                cond_expr = self._parse_operand(tokens[1])
                true_body = self._parse_block(['ELSE', 'END'])

                false_body = []
                if self._current_line() and self._current_line().startswith("ELSE"):
                    self.pos += 1
                    false_body = self._parse_block(['END'])

                self.pos += 1
                statements.append(If(cond_expr, true_body, false_body))

            elif command == "PUTC":
                statements.append(Putc(self._parse_operand(tokens[1])))

            elif command == "RETURN":
                val = self._parse_operand(tokens[1]) if len(tokens) > 1 else None
                statements.append(Return(val))

            elif command.startswith("CALL"):
                call_node = self._parse_call(line)
                statements.append(CallStmt(call_node.name, call_node.args))

            elif len(tokens) >= 3 and tokens[1] == "=":
                target = self._parse_operand(tokens[0])
                value_expr = self._parse_expression(" ".join(tokens[2:]))
                statements.append(Assign(target, value_expr))

            else:
                raise SyntaxError(f"Neznáma syntax: {line}")

        return statements

    def _parse_expression(self, expr_str: str):
        if expr_str.startswith("CALL"):
            return self._parse_call(expr_str)

        tokens = expr_str.split()
        if len(tokens) == 3:
            return BinOp(self._parse_operand(tokens[0]), tokens[1],
                         self._parse_operand(tokens[2]))
        elif len(tokens) == 1:
            return self._parse_operand(tokens[0])

        raise SyntaxError(f"Zlý výraz: {expr_str}")

    def _parse_operand(self, token: str):
        if token.isdigit() or (token.startswith('-') and token[1:].isdigit()):
            return Number(int(token))
        elif token.startswith('&'):
            return AddressOf(token[1:])
        elif token.startswith('*'):
            return Dereference(token[1:])
        elif "[" in token:
            name, idx_str = token[:-1].split("[")
            return ArrayAccess(name, self._parse_operand(idx_str))
        else:
            return Variable(token)

    def _parse_call(self, call_expr: str) -> CallExpr:
        match: re.Match[str] | None = re.match(r"CALL\s+(\w+)\s*\((.*)\)", call_expr)

        if match is None:
            raise Exception("This shouldn't happen")

        func_name = match.group(1)
        args_str = match.group(2).strip()
        args = [self._parse_operand(a.strip()) for a in
                args_str.split(',')] if args_str else []
        return CallExpr(func_name, args)

def print_ast(node, indent=""):
    if isinstance(node, Program):
        print("PROGRAM")
        for stmt in node.statements:
            print_ast(stmt, indent + "  ")
    elif isinstance(node, FuncDecl):
        print(f"{indent}FUNC {node.name}({', '.join(node.params)})")
        for stmt in node.body:
            print_ast(stmt, indent + "  ")
    elif isinstance(node, If):
        print(f"{indent}IF")
        print(f"{indent}  Condition: ", end="")
        print_ast(node.condition)
        print(f"{indent}  Then:")
        for stmt in node.true_body: print_ast(stmt, indent + "    ")
        if node.false_body:
            print(f"{indent}  Else:")
            for stmt in node.false_body: print_ast(stmt,
                                                   indent + "    ")
    elif isinstance(node, Let):
        print(f"{indent}LET {node.name} = ", end="")
        print_ast(node.value_expr)
    elif isinstance(node, Assign):
        print(f"{indent}ASSIGN ", end="")
        print_ast(node.target)
        print(" = ", end="")
        print_ast(node.value_expr)
    elif isinstance(node, While):
        print(f"{indent}WHILE")
        print(f"{indent}  Condition: ", end="")
        print_ast(node.condition)
        print(f"{indent}  Body:")
        for stmt in node.body: print_ast(stmt, indent + "    ")
    elif isinstance(node, BinOp):
        print(f"BinOp(", end="")
        print_ast(node.left)
        print(f" {node.op} ", end="")
        print_ast(node.right)
        print(")", end="")
    elif isinstance(node, Variable):
        print(f"Var({node.name})", end="")
    elif isinstance(node, Number):
        print(f"Num({node.value})", end="")
    elif isinstance(node, CallExpr) or isinstance(node, CallStmt):
        print(f"CALL {node.name}(...)", end="")
        if isinstance(node, CallStmt): print()
    else:
        print(f"{indent}{node.__class__.__name__}")

class MinilangCompiler:
    def __init__(self) -> None:
        self.variables: dict[str, str | int] = {}
        self.free_memory_pointer = 150
        self.asm_code = ["PUT 100 -> m99"]
        self.label_counter = 0

        self.current_func_locals = 0
        self.global_vars_backup: dict[str, str | int] = {}

    def compile(self, ast_root) -> str:
        self.visit(ast_root)
        self.asm_code.append("HLT")
        return "\n".join(self.asm_code)

    def visit(self, node) -> None:
        method_name = f'visit_{node.__class__.__name__}'
        visitor = getattr(self, method_name, self.generic_visit)
        visitor(node)

    def generic_visit(self, node) -> None:
        raise Exception(f"Chýba implementácia pre: {node.__class__.__name__}")

    # ==========================================
    # 1. ŠTRUKTÚRA PROGRAMU A PREMENNÉ
    # ==========================================
    def visit_Program(self, node) -> None:
        for stmt in node.statements:
            self.visit(stmt)

    def visit_ArrayDecl(self, node) -> None:
        self.variables[node.name] = self.free_memory_pointer
        self.free_memory_pointer += node.size

    def visit_Let(self, node) -> None:
        if self.current_func_locals is not None:
            self.current_func_locals += 1

            offset = -(self.current_func_locals - 1)
            self.variables[node.name] = f"BP{offset}" if offset != 0 else "BP"
            self.asm_code.append("PUSH 0")
        else:
            self.variables[node.name] = self.free_memory_pointer
            self.free_memory_pointer += 1

        self.visit_Assign(Assign(Variable(node.name), node.value_expr))

    def visit_Assign(self, node) -> None:
        self.evaluate_expression(node.value_expr, target_reg="r8")
        dest_operand = self._get_dest_operand(node.target)
        self.asm_code.append(f"PUT r8 -> {dest_operand}")

    def visit_If(self, node) -> None:
        self.label_counter += 1
        else_label = f"else_{self.label_counter}"
        endif_label = f"endif_{self.label_counter}"

        self.evaluate_expression(node.condition, "r1")
        self.asm_code.append(f"JZ r1, {else_label}")

        for stmt in node.true_body:
            self.visit(stmt)

        self.asm_code.append(f"JMP {endif_label}")
        self.asm_code.append(f"{else_label}:")

        for stmt in node.false_body:
            self.visit(stmt)

        self.asm_code.append(f"{endif_label}:")

    def visit_While(self, node) -> None:
        self.label_counter += 1
        start_label = f"loop_start_{self.label_counter}"
        end_label = f"loop_end_{self.label_counter}"

        self.asm_code.append(f"{start_label}:")
        self.evaluate_expression(node.condition, "r1")
        self.asm_code.append(f"JZ r1, {end_label}")

        for stmt in node.body:
            self.visit(stmt)

        self.asm_code.append(f"JMP {start_label}")
        self.asm_code.append(f"{end_label}:")

    def visit_FuncDecl(self, node) -> None:
        self.label_counter += 1
        skip_label = f"skip_func_{self.label_counter}"

        self.asm_code.append(f"JMP {skip_label}")
        self.asm_code.append(f"{node.name}:")

        self.global_vars_backup = self.variables.copy()

        self.asm_code.append("PUSH BP")
        self.asm_code.append("PUT SP -> BP")
        self.current_func_locals = 0

        for i, p in enumerate(reversed(node.params)):
            self.variables[p] = f"BP+{i + 3}"

        for stmt in node.body:
            self.visit(stmt)

        self.visit_Return(None)

        self.asm_code.append(f"{skip_label}:")
        self.current_func_locals = 0
        self.variables = self.global_vars_backup

    def visit_Return(self, node) -> None:
        if node and node.value_expr:
            self.evaluate_expression(node.value_expr, "r1")
        else:
            self.asm_code.append("PUT 0 -> r1")

        if self.current_func_locals is not None:
            self.asm_code.append("PUT BP -> SP")

            self.asm_code.append("POP BP")

        self.asm_code.append("RET")

    def visit_CallStmt(self, node) -> None:
        self.evaluate_expression(node,"r1")

    def visit_Putc(self, node) -> None:
        self.evaluate_expression(node.value_expr, "r2")
        self.asm_code.append("PUT m99 -> r7")
        self.asm_code.append("PUT r2 -> *r7")
        self.asm_code.append("INC r7")
        self.asm_code.append("PUT r7 -> m99")

    def evaluate_expression(self, expr_node, target_reg="r1") -> None:
        name = expr_node.__class__.__name__

        if name == "Number":
            self.asm_code.append(f"PUT {expr_node.value} -> {target_reg}")

        elif name == "Variable":
            dest = self._get_dest_operand(expr_node)
            self.asm_code.append(f"PUT {dest} -> {target_reg}")

        elif name == "AddressOf":
            addr = self.variables[expr_node.name]
            self.asm_code.append(f"PUT {addr} -> {target_reg}")

        elif name == "Dereference":
            dest = self._get_dest_operand(Variable(expr_node.name))
            self.asm_code.append(f"PUT {dest} -> r4")
            self.asm_code.append(f"PUT *r4 -> {target_reg}")

        elif name == "ArrayAccess":
            dest = self._get_dest_operand(expr_node)
            self.asm_code.append(f"PUT {dest} -> {target_reg}")

        elif name == "BinOp":
            self.evaluate_expression(expr_node.left, "r2")
            self.evaluate_expression(expr_node.right, "r3")

            op_map = {'+': 'ADD', '-': 'SUB', '*': 'MUL', '/': 'DIV',
                      '<<': 'SHL', '>>': 'SHR'}
            asm_op = op_map[expr_node.op]
            self.asm_code.append(f"{asm_op} r2, r3 -> {target_reg}")

        elif name in ["CallExpr", "CallStmt"]:
            for arg_expr in expr_node.args:
                self.evaluate_expression(arg_expr, "r2")
                self.asm_code.append("PUSH r2")

            self.asm_code.append(f"CALL {expr_node.name}")

            # Caller Cleanup
            for _ in expr_node.args:
                self.asm_code.append("POP r6")

            if target_reg != "r1":
                self.asm_code.append(f"PUT r1 -> {target_reg}")

    def _get_dest_operand(self, target_node) -> str:
        """Vracia string (napr. 'm150' alebo '*r4') a pripraví registre."""
        name = target_node.__class__.__name__

        if name == "Variable":
            addr = self.variables[target_node.name]
            if isinstance(addr, str) and "BP" in addr:
                offset = addr.replace("BP", "").replace("+", "")
                self.asm_code.append("PUT BP -> r4")
                if offset and offset != "0":
                    self.asm_code.append(f"ADD r4, {offset} -> r4")
                return "*r4"
            return f"m{addr}"

        elif name == "Dereference":
            dest = self._get_dest_operand(Variable(target_node.name))
            self.asm_code.append(f"PUT {dest} -> r4")
            self.asm_code.append("PUT *r4 -> r4")
            return "*r4"

        elif name == "ArrayAccess":
            self.evaluate_expression(target_node.index_expr, "r5")

            addr = self.variables[target_node.name]
            if isinstance(addr, str) and "BP" in addr:
                offset = addr.replace("BP", "").replace("+", "")
                self.asm_code.append("PUT BP -> r4")
                if offset and offset != "0":
                    self.asm_code.append(f"ADD r4, {offset} -> r4")
                self.asm_code.append("PUT *r4 -> r4")
            else:
                self.asm_code.append(f"PUT {addr} -> r4")

            self.asm_code.append("ADD r4, r5 -> r4")
            return "*r4"

        assert False, "This shouldn't happen"

# --- TEST KOMPILÁTORA ---
if __name__ == "__main__":
    with open("minilang/MiniOS.mini", 'r', encoding="utf-8") as file:
        minilang_code = file.read()

    parser = MinilangParser(minilang_code)
    ast_tree = parser.parse()

    # print_ast(ast_tree)

    compiler = MinilangCompiler()
    compiled_casm = compiler.compile(ast_tree)

    with open("program.casm", "w") as f:
        f.write(compiled_casm)