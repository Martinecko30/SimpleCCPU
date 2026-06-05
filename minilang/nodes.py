class ASTNode:
    def __init__(self, value = None) -> None:
        self.value = value

class ProgramNode(ASTNode):
    def __init__(self, body: list) -> None:
        super().__init__()
        self.body = body

class VarDeclarationNode(ASTNode):
    def __init__(self, value: list[ASTNode], var_name: str, is_pointer: bool = False) -> None:
        super().__init__(value)
        self.var_name = var_name
        self.is_pointer = is_pointer

class BinaryOpNode(ASTNode):
    def __init__(self, value, left: ASTNode, right: ASTNode) -> None:
        super().__init__(value)
        self.left = left
        self.right = right

class UnaryOpNode(ASTNode):
    def __init__(self, value, operand) -> None:
        super().__init__(value)
        self.operand = operand

class NumberNode(ASTNode):
    def __init__(self, value) -> None:
        super().__init__(value)

class AssignmentNode(ASTNode):
    def __init__(self, value, target) -> None:
        super().__init__()
        self.value = value
        self.target = target

class IfStatementNode(ASTNode):
    def __init__(self, condition: ASTNode, body: ASTNode, else_body: ASTNode | None) -> None:
        super().__init__()
        self.condition = condition
        self.body = body
        self.else_body = else_body

class WhileStatementNode(ASTNode):
    def __init__(self, condition, body) -> None:
        super().__init__()
        self.condition = condition
        self.body = body

class ReturnStatementNode(ASTNode):
    def __init__(self, value) -> None:
        super().__init__(value)

class IdentifierNode(ASTNode):
    def __init__(self, value) -> None:
        super().__init__(value)

class FuncDeclarationNode(ASTNode):
    def __init__(self, value: str, params: list[str], body: ASTNode):
        super().__init__(value)
        self.params = params
        self.body = body

class FuncCallNode(ASTNode):
    def __init__(self, value, args: list[ASTNode]) -> None:
        super().__init__(value)
        self.args = args

class BlockNode(ASTNode):
    def __init__(self, statements: list[ASTNode]) -> None:
        super().__init__()
        self.statements = statements

class IndexAccessNode(ASTNode):
    def __init__(self, value: str, index_expr: ASTNode) -> None:
        super().__init__(value)
        self.index_expr = index_expr

class DereferenceNode(ASTNode):
    def __init__(self, operand: ASTNode) -> None:
        super().__init__()
        self.operand = operand

class PointerRefNode(ASTNode):
    def __init__(self, operand: ASTNode) -> None:
        super().__init__()
        self.operand = operand

class ArrayDeclarationNode(ASTNode):
    def __init__(self, value: str, size: ASTNode, elements: list[ASTNode]) -> None:
        super().__init__(value)
        self.size = size
        self.elements = elements

class ExpressionStatement(ASTNode):
    def __init__(self, value: ASTNode) -> None:
        super().__init__(value)

class CharNode(ASTNode):
    def __init__(self, value: int) -> None:
        super().__init__(value)

class StringNode(ASTNode):
    def __init__(self, value: str) -> None:
        super().__init__(value)