from minilang.nodes import *
from minilang.nodes import ProgramNode
from parser import MinilangParser, ASTNode

class Compiler:
    def __init__(self, source_code: str) -> None:
        self.parser = MinilangParser(source_code)
        self.program = self.parser.parse()
        self.asm_lines: list[str] = []
        self.variables: dict[str, str] = dict()
        self.current_offset = 0
        self.label_counter = 0

    def generate_label(self, prefix: str):
        self.label_counter += 1
        return f"{prefix}_{self.label_counter}"

    def compile_to_file(self, path_to_file: str) -> None:
        self.compile()
        with open(path_to_file, 'w') as file:
            file.write("\n".join(self.asm_lines))

    def compile(self) -> None:
        self.visit(self.program)
        self.asm_lines.append("HLT")

        self.optimization_pass()

    def optimization_pass(self, depth=0) -> None:
        if depth >= 3:
            return

        optimized: list[str] = []

        for line in self.asm_lines:
            if not optimized:
                optimized.append(line)
                continue

            prev_line = optimized[-1]

            if prev_line.startswith("PUSH ") and line.startswith("POP "):
                push_val = prev_line.split(" ")[1]
                pop_val = line.split(" ")[1]

                if push_val in ("BP", "SP") or pop_val in ("BP", "SP"):
                    optimized.append(line)
                    continue

                optimized.pop()

                if push_val == pop_val:
                    pass
                else:
                    optimized.append(f"PUT {push_val} -> {pop_val}")

            else:
                optimized.append(line)

        self.asm_lines = optimized
        self.optimization_pass(depth + 1)

    def visit(self, node: ASTNode) -> None:
        if node is None:
            return

        match node:
            case ProgramNode():
                for statement in node.body:
                    self.visit(statement)
            case BlockNode():
                for statement in node.statements:
                    self.visit(statement)
            case NumberNode():
                self.visit_number(node)
            case CharNode():
                self.visit_char(node)
            case StringNode():
                self.visit_string(node)
            case BinaryOpNode():
                self.visit_binary_op(node)
            case VarDeclarationNode():
                self.visit_let(node)
            case IdentifierNode():
                self.visit_identifier(node)
            case AssignmentNode():
                self.visit_assignment(node)
            case UnaryOpNode():
                self.visit_unary_op(node)
            case IfStatementNode():
                self.visit_if(node)
            case WhileStatementNode():
                self.visit_while(node)
            case ArrayDeclarationNode():
                self.visit_array_declaration(node)
            case IndexAccessNode():
                self.visit_index_access(node)
            case FuncDeclarationNode():
                self.visit_func_declaration(node)
            case FuncCallNode():
                self.visit_func_call(node)
            case ReturnStatementNode():
                self.visit_return(node)
            case DereferenceNode():
                self.visit_dereference(node)
            case ExpressionStatement():
                self.visit_expression_statement(node)
            case _:
                raise NotImplementedError(f"Compiler doesn't know how to compile {node} yet!")

    def visit_expression_statement(self, node: ExpressionStatement) -> None:
        self.visit(node.value)
        self.asm_lines.append("POP r2")

    def visit_return(self, node: ReturnStatementNode) -> None:
        self.visit(node.value)
        self.asm_lines.append("POP r1")
        self.asm_lines.append("POP BP")
        self.asm_lines.append("RET")

    def visit_func_call(self, node: FuncCallNode) -> None:
        if node.args:
            for arg in node.args:
                self.visit(arg)

        self.asm_lines.append(f"CALL FUNC_{node.value}_START")

        if node.args:
            for _ in node.args:
                self.asm_lines.append("POP r2")

        self.asm_lines.append("PUSH r1")

    def visit_func_declaration(self, node: FuncDeclarationNode) -> None:
        func_name = node.value

        self.asm_lines.append(f"JMP FUNC_{func_name}_END")
        self.asm_lines.append(f"FUNC_{func_name}_START:")

        self.asm_lines.append(f"PUSH BP")
        self.asm_lines.append(f"PUT SP -> BP")

        if node.params:
            num_params = len(node.params)
            for i, param_name in enumerate(node.params):
                offset = num_params - i + 1
                self.variables[param_name] = f"BP_OFFSET:{offset}"

        self.visit(node.body)

        self.asm_lines.append("POP BP")
        self.asm_lines.append("RET")
        self.asm_lines.append(f"FUNC_{func_name}_END:")

    def visit_index_access(self, node: IndexAccessNode) -> None:
        self.visit_identifier(IdentifierNode(node.value))

        self.visit(node.index_expr)

        self.asm_lines.append("POP r2")  # r2 = index
        self.asm_lines.append("POP r1")  # r1 = base address

        self.asm_lines.append("ADD r1, r2 -> r1")
        self.asm_lines.append("PUT *r1 -> r1")

        self.asm_lines.append("PUSH r1")

    def visit_array_declaration(self, node: ArrayDeclarationNode) -> None:
        size = node.size.value

        base_address = self.current_offset
        self.variables[node.value] = f"m{base_address}"

        self.variables[node.value] = f"ARRAY:{base_address}"

        self.current_offset += size

        if node.elements:
            for i, element_node in enumerate(node.elements):
                self.visit(element_node)
                self.asm_lines.append("POP r1")
                self.asm_lines.append(f"PUT r1 -> m{base_address + i}")

    def visit_if(self, node: IfStatementNode) -> None:
        else_label = self.generate_label("IF_ELSE")
        end_label = self.generate_label("IF_END")

        self.visit(node.condition)
        self.asm_lines.append("POP r1")

        else_body = node.else_body

        target_label = else_label if else_body else end_label
        self.asm_lines.append(f"JZ r1 -> {target_label}")

        self.visit(node.body)

        if else_body:
            self.asm_lines.append(f"JMP {end_label}")

            self.asm_lines.append(f"{else_label}:")
            self.visit(else_body)

        self.asm_lines.append(f"{end_label}:")

    def visit_while(self, node: WhileStatementNode) -> None:
        start_label = self.generate_label("WHILE_START")
        end_label = self.generate_label("WHILE_END")

        self.asm_lines.append(f"{start_label}:")
        self.visit(node.condition)

        self.asm_lines.append("POP r1")

        self.asm_lines.append(f"JZ r1 -> {end_label}")

        self.visit(node.body)

        self.asm_lines.append(f"JMP {start_label}")

        self.asm_lines.append(f"{end_label}:")

    def visit_let(self, node: VarDeclarationNode) -> None:
        self.visit(node.value)
        self.asm_lines.append("POP r1")

        mem_address = f"m{self.current_offset}"

        self.variables[node.var_name] = mem_address
        self.current_offset += 1

        self.asm_lines.append(f"PUT r1 -> {mem_address}")

    def visit_identifier(self, node: IdentifierNode) -> None:
        var_name = node.value

        if var_name not in self.variables:
            raise NameError(f"Variable '{var_name}' is not defined!")

        mem_address = self.variables[var_name]

        if mem_address.startswith("BP_OFFSET:"):
            offset = mem_address.split(":")[1]
            self.asm_lines.append("PUT BP -> r1")
            self.asm_lines.append(f"ADD r1, {offset} -> r1")
            self.asm_lines.append("PUT *r1 -> r1")
            self.asm_lines.append("PUSH r1")
        elif mem_address.startswith("ARRAY:"):
            address_val = mem_address.split(":")[1]
            self.asm_lines.append(f"PUT {address_val} -> r1")
            self.asm_lines.append("PUSH r1")
        else:
            self.asm_lines.append(f"PUT {mem_address} -> r1")
            self.asm_lines.append("PUSH r1")

    def visit_assignment(self, node: AssignmentNode) -> None:
        self.visit(node.value)

        if isinstance(node.target, IdentifierNode):
            self.asm_lines.append("POP r3")
            var_name = node.target.value

            if var_name not in self.variables:
                raise NameError(
                    f"Cannot assign to undefined variable '{var_name}'")

            mem_address = self.variables[var_name]

            if mem_address.startswith("BP_OFFSET:"):
                offset = mem_address.split(":")[1]
                self.asm_lines.append("PUT BP -> r1")
                self.asm_lines.append(f"ADD r1, {offset} -> r1")
                self.asm_lines.append("PUT r3 -> *r1")

            elif mem_address.startswith("ARRAY:"):
                raise TypeError(f"Cannot reassign array base pointer '{var_name}'")

            else:
                self.asm_lines.append(f"PUT r3 -> {mem_address}")

            self.asm_lines.append("PUSH r3")

        elif isinstance(node.target, IndexAccessNode):
            self.visit_identifier(IdentifierNode(node.target.value))
            self.visit(node.target.index_expr)

            self.asm_lines.append("POP r2")  # r2 = evaluated index
            self.asm_lines.append("POP r1")  # r1 = evaluated base address
            self.asm_lines.append("POP r3")  # r3 = new value (from top of method)

            self.asm_lines.append("ADD r1, r2 -> r1")
            self.asm_lines.append("PUT r3 -> *r1")

            self.asm_lines.append("PUSH r3")

        elif isinstance(node.target, DereferenceNode):
            self.asm_lines.append("POP r3")  # r3 = new value

            self.visit(node.target.operand)
            self.asm_lines.append("POP r1")  # r1 = pointer address

            self.asm_lines.append("PUT r3 -> *r1")
            self.asm_lines.append("PUSH r3")

    def visit_dereference(self, node: DereferenceNode) -> None:
        self.visit(node.operand)

        self.asm_lines.append("POP r1")
        self.asm_lines.append("PUT *r1 -> r1")
        self.asm_lines.append("PUSH r1")

    def visit_unary_op(self, node: UnaryOpNode) -> None:

        op = node.value
        if op == "-":
            self.visit(node.operand)
            self.asm_lines.append("POP r1")
            self.asm_lines.append("MUL r1, -1 -> r1")
            self.asm_lines.append("PUSH r1")

        elif op == "&":
            var_name = node.operand.value

            mem_string = self.variables[var_name]
            address_number = mem_string.replace("m", "")

            self.asm_lines.append(f"PUT {address_number} -> r1")
            self.asm_lines.append("PUSH r1")

    def visit_binary_op(self, node: BinaryOpNode) -> None:
        self.visit(node.left)

        self.visit(node.right)

        self.asm_lines.append("POP r2")
        self.asm_lines.append("POP r1")

        op = node.value
        if op == "+":
            self.asm_lines.append("ADD r1, r2 -> r1")
        elif op == "-":
            self.asm_lines.append("SUB r1, r2 -> r1")
        elif op == "*":
            self.asm_lines.append("MUL r1, r2 -> r1")
        elif op == "/":
            self.asm_lines.append("DIV r1, r2 -> r1")

        elif op == "==":
            self.asm_lines.append("SEQ r1, r2 -> r1")
        elif op == "!=":
            self.asm_lines.append("SEQ r1, r2 -> r1")
            self.asm_lines.append("SUB 1, r1 -> r1")
        elif op == ">=":
            self.asm_lines.append("SLT r1, r2 -> r1")
            self.asm_lines.append("SUB 1, r1 -> r1")
        elif op == "<=":
            self.asm_lines.append("SGT r1, r2 -> r1")
            self.asm_lines.append("SUB 1, r1 -> r1")
        elif op == ">":
            self.asm_lines.append("SGT r1, r2 -> r1")
        elif op == "<":
            self.asm_lines.append("SLT r1, r2 -> r1")

        self.asm_lines.append("PUSH r1")

    def visit_string(self, node: StringNode) -> None:
        base_address = self.current_offset

        for char in node.value:
            ascii_val = ord(char)
            self.asm_lines.append(f"PUT {ascii_val} -> m{self.current_offset}")
            self.current_offset += 1

        self.asm_lines.append(f"PUT 0 -> m{self.current_offset}")
        self.current_offset += 1

        self.asm_lines.append(f"PUSH m{base_address}")

    def visit_char(self, node: CharNode) -> None:
        self.asm_lines.append(f"PUSH {node.value}")

    def visit_number(self, node: NumberNode) -> None:
        self.asm_lines.append(f"PUSH {node.value}")

if __name__ == "__main__":
    with open("../minilang/test.mini", 'r') as file:
        source = file.read()

    compiler = Compiler(source)
    compiler.compile_to_file("program.casm")