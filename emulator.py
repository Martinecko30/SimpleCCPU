from enum import Enum

from system_bus import SystemBus


class Operation(Enum):
    ADD = (1, 3)
    SUB = (2, 3)

    INC = (3, 1)
    DEC = (4, 1)

    MUL = (5, 3)
    DIV = (6, 3)
    SHL = (7, 3)
    SHR = (8, 3)

    PUT = (9, 2)

    PUSH = (10, 1)
    POP = (11, 1)

    JMP = (12, 1)
    JZ = (13, 2)
    JNZ = (14, 2)

    INT = (15, 1)
    IRET = (16, 0)

    CALL = (17, 1)
    RET = (18, 0)

    HLT = (0, 0)

    def __init__(self, opcode: int, operand_count: int):
        self.opcode = opcode
        self.operand_count = operand_count

class Status(Enum):
    OK = 1
    HALTED = 2
    BAD_OPERAND = 3
    MEMORY_ERROR = 4
    BAD_INSTRUCTION = 5
    MATH_ERROR = 6
    UNHANDLED_INTERRUPT = 7

class Instruction:
    def __init__(self, operation: Operation, operands: list[str]):
        self.op = operation
        self.operands = operands


def parse_to_instructions(file_name: str) -> list[Instruction]:
    raw_lines = []
    labels = {}

    instruction_index = 0
    with open(file_name, 'r', encoding='utf-8') as f:
        for original_line_number, line in enumerate(f, start=1):
            if ';' in line:
                line = line.split(';', 1)[0]

            line = line.strip()

            if not line:
                continue

            if line.endswith(':'):
                label_name = line[:-1].strip()
                labels[label_name] = instruction_index
            else:
                raw_lines.append((original_line_number, line))
                instruction_index += 1

    instructions = []
    for line_number, line in raw_lines:
        parts = line.split(maxsplit=1)
        op_str = parts[0].upper()

        try:
            operation = Operation[op_str]
        except KeyError:
            raise ValueError(
                f"Chyba syntaxe: Neznáma inštrukcia '{op_str}' na riadku {line_number}")

        operands = []
        if len(parts) > 1:
            raw_operands = parts[1].replace(',', ' ').replace('->', ' ')
            operands = raw_operands.split()

            for i in range(len(operands)):
                if operands[i] in labels:
                    operands[i] = str(labels[operands[i]])

        instructions.append(Instruction(operation, operands))

    return instructions


class Emulator:
    """Simple Custom CPU"""
    def __init__(self, bus: SystemBus) -> None:
        self.__bus = bus
        self.__registers = {
            'r1': 0,
            'r2': 0,
            'r3': 0,
            'r4': 0,
            'r5': 0,
            'r6': 0,
            'r7': 0,
            'r8': 0,
            'SP': bus.memory_size - 1,
            'BP': bus.memory_size - 1
        }

        self.__PC = 0
        self.__code_lines = 0

        self.__status = Status.OK

    def reset(self):
        self.__PC = 0
        self.__bus.ram = [0] * self.__bus.memory_size
        self.__status = Status.OK
        self.__registers = dict.fromkeys(self.__registers, 0)
        self.__registers['SP'] = self.__bus.memory_size - 1
        self.__code_lines = 0

    def run_program(self, file_name: str, debug: bool)\
            -> tuple[Status, int, int]:
        """file_name should lead to Custom-ASM file"""
        code: list[Instruction] = parse_to_instructions(file_name)
        self.__code_lines = len(code)

        while self.__status == Status.OK and self.__PC < self.__code_lines:
            if self.__bus.interrupt_line is not None:
                vector = self.__bus.interrupt_line
                self.__bus.interrupt_line = None

                isr_address = self.__bus.read(vector)
                if isr_address != 0:
                    self.__bus.write(self.__registers['SP'], self.__PC)
                    self.__registers['SP'] -= 1
                    self.__PC = isr_address

            instr = code[self.__PC]

            self.__PC += 1

            self._execute_instruction(instr, debug)


        if self.__PC >= self.__code_lines and self.__status == Status.OK:
            self.__status = Status.MEMORY_ERROR

        return self.__status, self.__PC, self.__registers['SP']

    def _execute_instruction(self, instruction: Instruction, debug: bool)\
            -> None:
        instr_name = f"_{instruction.op.name.lower()}"

        # DEBUGGING
        if debug:
            print(f"Executing: {instruction.op.name}, Operands: {instruction.operands}, Expected: {instruction.op.value}")

        if len(instruction.operands) != instruction.op.operand_count:
            self.__status = Status.BAD_OPERAND
            return

        if hasattr(self, instr_name):
            exec_method = getattr(self, instr_name)
            exec_method(instruction.operands)
        else:
            self.__status = Status.BAD_INSTRUCTION

    def __val_reg(self, register: str) -> bool:
        return register in self.__registers

    def _read_operand(self, op: str):
        """Returns the integer value of a literal, register, or memory cell. Returns None on error."""
        try:
            if op.startswith('*'):
                reg = op[1:]
                if not self.__val_reg(reg): return None
                address = self.__registers[reg]
                if 0 <= address < self.__bus.memory_size:
                    return self.__bus.read(address)
                return None

            elif self.__val_reg(op):
                return self.__registers[op]

            elif op.startswith('m'):
                cell = int(op[1:])
                if 0 <= cell < self.__bus.memory_size:
                    return self.__bus.read(cell)
                return None

            else:
                return int(op)

        except ValueError:
            return None

    def _write_operand(self, op: str, value: int) -> bool:
        """Writes a value to a register or memory cell. Returns True on success, False on error."""
        try:
            if op.startswith('*'):
                reg = op[1:]
                if not self.__val_reg(reg): return False
                address = self.__registers[reg]
                self.__bus.write(address, value)
                return True

            elif self.__val_reg(op):
                self.__registers[op] = value
                return True

            elif op.startswith('m'):
                address = int(op[1:])
                self.__bus.write(address, value)
                return True

            else:
                # Cannot write to a literal value!
                return False

        except ValueError:
            return False

    def _add(self, args: list[str]) -> None:
        val1 = self._read_operand(args[0])
        val2 = self._read_operand(args[1])

        if val1 is None or val2 is None:
            self.__status = Status.BAD_OPERAND
            return

        result = val1 + val2

        if not self._write_operand(args[2], result):
            self.__status = Status.BAD_OPERAND

    def _sub(self, args: list[str]) -> None:
        val1 = self._read_operand(args[0])
        val2 = self._read_operand(args[1])

        if val1 is None or val2 is None:
            self.__status = Status.BAD_OPERAND
            return

        result = val1 - val2

        if not self._write_operand(args[2], result):
            self.__status = Status.BAD_OPERAND

    def _inc(self, args: list[str]) -> None:
        val = self._read_operand(args[0])

        if val is None:
            self.__status = Status.BAD_OPERAND
            return

        val += 1

        if not self._write_operand(args[0], val):
            self.__status = Status.BAD_OPERAND

    def _dec(self, args: list[str]) -> None:
        val = self._read_operand(args[0])

        if val is None:
            self.__status = Status.BAD_OPERAND
            return

        val -= 1

        if not self._write_operand(args[0], val):
            self.__status = Status.BAD_OPERAND

    def _put(self, args: list[str]) -> None:
        src, dest = args[0], args[1]

        val = self._read_operand(src)
        if val is None:
            self.__status = Status.BAD_OPERAND
            return

        success = self._write_operand(dest, val)
        if not success:
            self.__status = Status.BAD_OPERAND

    def _push(self, args: list[str]) -> None:
        val = self._read_operand(args[0])
        if val is None:
            self.__status = Status.BAD_OPERAND
            return

        self.__bus.write(self.__registers['SP'], val)
        self.__registers['SP'] -= 1

        if self.__registers['SP'] < -1:
            self.__status = Status.MEMORY_ERROR

    def _pop(self, args: list[str]) -> None:
        self.__registers['SP'] += 1
        if self.__registers['SP'] >= self.__bus.memory_size:
            self.__status = Status.MEMORY_ERROR
            return

        val = self.__bus.read(self.__registers['SP'])
        if not self._write_operand(args[0], val):
            self.__status = Status.BAD_OPERAND
            return

    def _jmp(self, args: list[str]) -> None:
        address = self._read_operand(args[0])
        if address is None:
            self.__status = Status.BAD_OPERAND
            return

        if not 0 <= address < self.__code_lines:
            self.__status = Status.MEMORY_ERROR
            return

        self.__PC = address

    def _jz(self, args: list[str]) -> None:
        val = self._read_operand(args[0])
        address = self._read_operand(args[1])

        if val is None or address is None:
            self.__status = Status.BAD_OPERAND
            return

        if not 0 <= address < self.__code_lines:
            self.__status = Status.MEMORY_ERROR
            return

        if val == 0:
            self.__PC = address

    def _jnz(self, args: list[str]) -> None:
        val = self._read_operand(args[0])
        address = self._read_operand(args[1])

        if val is None or address is None:
            self.__status = Status.BAD_OPERAND
            return

        if not 0 <= address < self.__code_lines:
            self.__status = Status.MEMORY_ERROR
            return

        if val != 0:
            self.__PC = address

    def _mul(self, args: list[str]) -> None:
        val1 = self._read_operand(args[0])
        val2 = self._read_operand(args[1])
        if val1 is None or val2 is None:
            self.__status = Status.BAD_OPERAND
            return

        if not self._write_operand(args[2], val1 * val2):
            self.__status = Status.BAD_OPERAND

    def _div(self, args: list[str]) -> None:
        val1 = self._read_operand(args[0])
        val2 = self._read_operand(args[1])
        if val1 is None or val2 is None:
            self.__status = Status.BAD_OPERAND
            return

        if val2 == 0:
            self.__status = Status.MATH_ERROR
            return

        if not self._write_operand(args[2], val1 // val2):
            self.__status = Status.BAD_OPERAND

    def _shl(self, args: list[str]) -> None:
        val = self._read_operand(args[0])
        shift_amount = self._read_operand(args[1])
        if val is None or shift_amount is None:
            self.__status = Status.BAD_OPERAND
            return

        if not self._write_operand(args[2], val << shift_amount):
            self.__status = Status.BAD_OPERAND

    def _shr(self, args: list[str]) -> None:
        val = self._read_operand(args[0])
        shift_amount = self._read_operand(args[1])
        if val is None or shift_amount is None:
            self.__status = Status.BAD_OPERAND
            return

        if not self._write_operand(args[2], val >> shift_amount):
            self.__status = Status.BAD_OPERAND

    def _int(self, args: list[str]) -> None:
        vector_index = self._read_operand(args[0])

        if vector_index is None or vector_index < 0 or vector_index >= self.__bus.memory_size:
            self.__status = Status.BAD_OPERAND
            return

        isr_address = self.__bus.read(vector_index)

        if isr_address == 0:
            self.__status = Status.UNHANDLED_INTERRUPT
            return

        self.__bus.write(self.__registers['SP'], self.__PC)
        self.__registers['SP'] -= 1

        if self.__registers['SP'] < -1:
            self.__status = Status.MEMORY_ERROR
            return

        self.__PC = isr_address

    def _iret(self, args: list[str]) -> None:
        self.__registers['SP'] += 1

        if self.__registers['SP'] >= self.__bus.memory_size:
            self.__status = Status.MEMORY_ERROR
            return

        return_address = self.__bus.read(self.__registers['SP'])

        self.__PC = return_address

    def _call(self, args: list[str]) -> None:
        index = self._read_operand(args[0])

        if index is None:
            self.__status = Status.BAD_OPERAND
            return

        if not 0 <= index < self.__code_lines:
            self.__status = Status.MEMORY_ERROR
            return

        self.__bus.write(self.__registers['SP'], self.__PC)
        self.__registers['SP'] -= 1

        if self.__registers['SP'] < -1:
            self.__status = Status.MEMORY_ERROR
            return

        self.__PC = index

    def _ret(self, args: list[str]) -> None:
        self.__registers['SP'] += 1

        if self.__registers['SP'] >= self.__bus.memory_size:
            self.__status = Status.MEMORY_ERROR
            return

        return_address = self.__bus.read(self.__registers['SP'])

        self.__PC = return_address

    def _hlt(self, args: list[str]):
        self.__status = Status.HALTED