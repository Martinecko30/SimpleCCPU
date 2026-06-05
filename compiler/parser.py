from minilang.nodes import *
from tokenizer import Tokenizer, Token, TokenType


class MinilangParser:
    def __init__(self, source_code: str) -> None:
        self.tokenizer = Tokenizer(source_code)
        self.tokens = list(reversed(self.tokenizer.tokens))
        self.pos = 0

    def next(self) -> Token:
        return self.tokens.pop()

    def peek(self) -> Token:
        return self.tokens[-1]

    def expect(self, expected_type: TokenType) -> Token:
        token = self.next()
        if token.token_type != expected_type:
            raise SyntaxError(
                f"Expected {expected_type.name}, got {token.token_type.name} ('{token.value}') "
                f"at line {token.line}, col {token.column}"
            )
        return token

    def parse(self) -> ASTNode:
        body = []
        while self.tokens:
            token = self.peek()

            if token.token_type == TokenType.KEY_FUNC:
                body.append(self.parse_func_declaration())
            else:
                body.append(self.parse_statement())
        return ProgramNode(body)


    def parse_func_declaration(self) -> ASTNode:
        self.next() # Consume 'func'

        name_token = self.expect(TokenType.IDENTIFIER)

        self.expect(TokenType.L_BRACKET)
        params = []
        if self.peek().token_type != TokenType.R_BRACKET:
            params.append(self.expect(TokenType.IDENTIFIER).value)
            while self.peek().token_type == TokenType.COMMA:
                self.next()
                params.append(self.expect(TokenType.IDENTIFIER).value)

        self.expect(TokenType.R_BRACKET)

        body_node = self.parse_block()
        return FuncDeclarationNode(name_token.value, params, body_node)

    def parse_block(self) -> ASTNode:
        self.expect(TokenType.L_CURLY)

        statements = []
        while self.peek().token_type != TokenType.R_CURLY:
            statements.append(self.parse_statement())

        self.expect(TokenType.R_CURLY)
        return BlockNode(statements)

    def parse_statement(self) -> ASTNode:
        token = self.peek()

        match token.token_type:
            case TokenType.KEY_LET:
                return self.parse_let()
            case TokenType.KEY_WHILE:
                return self.parse_while()
            case TokenType.KEY_FUNC:
                return self.parse_func_declaration()
            case TokenType.KEY_IF:
                return self.parse_if()
            case TokenType.KEY_RETURN:
                return self.parse_return()
            case _:
                expr = self.parse_expression()
                return ExpressionStatement(expr)

    def parse_return(self) -> ASTNode:
        self.next()
        value = self.parse_expression()
        return ReturnStatementNode(value)

    def parse_expression(self) -> ASTNode:
        return self.parse_assignment()

    def parse_assignment(self) -> ASTNode:
        left = self.parse_comparison()

        if self.tokens and self.peek().token_type == TokenType.EQUAL_SIGN:
            self.next()  # Consume '='

            right = self.parse_assignment()

            return AssignmentNode(value=right, target=left)

        return left

    def parse_let(self) -> ASTNode:
        self.next() # Consume 'let'

        is_pointer = False
        if self.tokens and self.peek().token_type == TokenType.STAR:
            self.next() # Consume '*'
            is_pointer = True

        var_name_token = self.expect(TokenType.IDENTIFIER)

        array_size: ASTNode | None = None
        if self.tokens and self.peek().token_type == TokenType.L_SQUARE:
            self.next() # Consume '['
            array_size = self.parse_expression()
            self.expect(TokenType.R_SQUARE)

        self.expect(TokenType.EQUAL_SIGN)

        if self.tokens and self.peek().token_type == TokenType.L_CURLY:
            self.next() # Consume '{'
            elements = []
            if self.peek().token_type != TokenType.R_CURLY:
                elements.append(self.parse_expression())
                while self.peek().token_type == TokenType.COMMA:
                    self.next()
                    elements.append(self.parse_expression())
            self.expect(TokenType.R_CURLY) # Consume '}'
            value_node: list[ASTNode] = elements
        else:
            expr = self.parse_expression()

            if isinstance(expr, StringNode) and not is_pointer:
                raise SyntaxError(f"Strings must be assigned to a pointer. Try: let *{var_name_token.value} = .../n")
            if is_pointer and not isinstance(expr, (StringNode, IdentifierNode, PointerRefNode)):
                raise SyntaxError(f"Pointer '*{var_name_token.value}' must be initialized with a string, reference, or address.")

            value_node = [expr]

        if array_size is not None:
            return ArrayDeclarationNode(var_name_token.value, array_size, value_node)

        return VarDeclarationNode(value_node, var_name_token.value, is_pointer)

    def parse_if(self) -> ASTNode:
        self.next() # Consume 'if'

        condition = self.parse_expression()

        if self.peek().token_type == TokenType.L_CURLY:
            body = self.parse_block()
        else:
            body = self.parse_statement()

        else_body = None
        if self.tokens and self.peek().token_type == TokenType.KEY_ELSE:
            self.next()  # Consume 'else'
            if self.peek().token_type == TokenType.L_CURLY:
                else_body = self.parse_block()
            else:
                else_body = self.parse_statement()

        return IfStatementNode(condition, body, else_body)

    def parse_while(self) -> ASTNode:
        self.next() # Consume 'while'

        condition = self.parse_expression()

        if self.peek().token_type == TokenType.L_CURLY:
            body = self.parse_block()
        else:
            body = self.parse_statement()

        return WhileStatementNode(condition, body)

    def parse_comparison(self) -> ASTNode:
        left = self.parse_term()

        if self.tokens and self.peek().token_type in (
            TokenType.COMPARE_EQUALS,
            TokenType.NOT_EQUAL,
            TokenType.LESS_THAN,
            TokenType.MORE_THAN,
            TokenType.LESS_OR_EQUAL,
            TokenType.MORE_OR_EQUAL
        ):
            operator_token = self.next()
            right = self.parse_term()

            left = BinaryOpNode(operator_token.value, left, right)
        return left

    def parse_term(self) -> ASTNode:
        left = self.parse_factor()

        while self.tokens and self.peek().token_type in (TokenType.PLUS, TokenType.MINUS):
            operator_token = self.next()
            right = self.parse_factor()

            left = BinaryOpNode(operator_token.value, left, right)

        return left

    def parse_factor(self) -> ASTNode:
        left = self.parse_unary()

        while self.tokens and self.peek().token_type in (TokenType.STAR, TokenType.DIV):
            operator_token = self.next()
            right = self.parse_unary()

            left = BinaryOpNode(operator_token.value, left, right)

        return left

    def parse_unary(self) -> ASTNode:
        if self.tokens and self.peek().token_type in (TokenType.MINUS, TokenType.LOGICAL_NOT, TokenType.AMPERSAND, TokenType.STAR):
            operator_token = self.next()
            operand = self.parse_unary()

            if operator_token.token_type == TokenType.AMPERSAND:
                return PointerRefNode(operand)

            if operator_token.token_type == TokenType.STAR:
                return DereferenceNode(operand)

            return UnaryOpNode(operator_token.value, operand)
        return self.parse_atomic()

    def parse_atomic(self) -> ASTNode:
        if not self.tokens:
            raise SyntaxError("Unexpected end of file")

        token = self.peek()

        match token.token_type:
            case TokenType.NUMBER:
                self.next()
                return NumberNode(int(token.value))

            case TokenType.CHAR:
                self.next()
                raw_char = token.value[1:-1]
                ascii_val = ord(raw_char)
                return CharNode(ascii_val)

            case TokenType.STRING:
                self.next()
                clean_str = token.value[1:-1]
                return StringNode(clean_str)

            case TokenType.L_BRACKET:
                self.next()
                expr = self.parse_expression()

                if not self.tokens or self.peek().token_type != TokenType.R_BRACKET:
                    raise SyntaxError(f"Unexpected ')' after an experession at {self.peek()}")
                self.next()

                return expr

            case TokenType.IDENTIFIER:
                name_token = self.next()
                if self.tokens and self.peek().token_type == TokenType.L_BRACKET:
                    self.next() # Consume '('
                    args = []
                    if self.peek().token_type != TokenType.R_BRACKET:
                        args.append(self.parse_expression())
                        while self.peek().token_type == TokenType.COMMA:
                            self.next() # Consume ','
                            args.append(self.parse_expression())
                    self.expect(TokenType.R_BRACKET)
                    return FuncCallNode(name_token.value, args)

                if self.tokens and self.peek().token_type == TokenType.L_SQUARE:
                    self.next() # Consume '['
                    index_expr = self.parse_expression()
                    self.expect(TokenType.R_SQUARE)
                    return IndexAccessNode(name_token.value, index_expr)

                return IdentifierNode(name_token.value)

        raise SyntaxError(
            f"Unexpected token in expression: '{token.value}' "
            f"at line {token.line}, col {token.column}"
        )


if __name__ == "__main__":
    with open("../minilang/test.mini", 'r') as file:
        source = file.read()

    source = """
    func test(x) {
        let i = 5
        while (x < i) {
            i = i + 1
        }
    }
    """

    parser = MinilangParser(source)
    print(parser.parse())