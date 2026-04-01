# Custom Computer Architecture & CASM Emulator

A lightweight, Turing-complete Virtual Machine and Custom Assembly (CASM) emulator written in Python. This project features a completely custom Instruction Set Architecture (ISA), a hardware System Bus, memory-mapped peripherals, a fully functional stack, and a two-pass assembler with label support.

## ✨ Features

* **Custom ISA:** 19 core instructions providing full control over arithmetic, memory, stack manipulation, and control flow.
* **Unified Memory Architecture:** Code and data share the same address space during execution, supporting dynamic read/write operations and pointer arithmetic.
* **Memory-Mapped Peripherals:** Interact with virtual hardware exactly like real early computers. Includes a Graphics Card (GPU) for display output and a Keyboard for asynchronous input.
* **Two-Pass Assembler:** Write clean code using `labels:` instead of raw instruction line numbers.
* **Hardware Stack:** Built-in support for `PUSH`, `POP`, `CALL`, and `RET` operations with dedicated Stack and Base pointers.
* **Interrupt Handling:** Supports hardware and software interrupts (`INT`, `IRET`) via a configurable IRQ vector table.

## 🏗️ Hardware Specifications

* **Registers:** * 8 General-Purpose Registers (`r1` to `r8`)
  * Stack Pointer (`SP`) - Grows downwards from the top of memory.
  * Base Pointer (`BP`) - Used for stack frames and local variables.
  * Program Counter (`PC`) - Tracks execution state.
* **Memory:** Configurable size (e.g., 512 words), 0-initialized.
* **System Bus:** Routes read/write requests between the CPU, RAM, and attached peripherals.

## 📖 CASM Instruction Set Architecture

The emulator uses a specific syntax with the `->` operator to clearly distinguish source and destination operands.

### Addressing Modes
* **Literal:** Integer values (e.g., `5`, `-10`).
* **Register:** CPU registers (e.g., `r1`, `SP`).
* **Direct Memory:** Absolute memory addresses (e.g., `m150`).
* **Indirect (Pointer):** Memory access via register value (e.g., `*r4`).

### Supported Instructions

| Opcode | Syntax | Description |
| :--- | :--- | :--- |
| **PUT** | `PUT src -> dest` | Moves value from `src` to `dest`. |
| **ADD** | `ADD src1, src2 -> dest` | Adds `src1` and `src2`, stores result in `dest`. |
| **SUB** | `SUB src1, src2 -> dest` | Subtracts `src2` from `src1`, stores result in `dest`. |
| **MUL** / **DIV** | `MUL src1, src2 -> dest` | Multiplies/Divides `src1` and `src2`. |
| **SHL** / **SHR** | `SHL src, amount -> dest`| Bitwise shift operations. |
| **INC** / **DEC** | `INC dest` | Increments/Decrements the value in `dest` by 1. |
| **PUSH**| `PUSH src` | Pushes `src` onto the top of the stack. |
| **POP** | `POP dest` | Pops the top value of the stack into `dest`. |
| **JMP** | `JMP target` | Unconditional jump to `target` (Label or line number). |
| **JZ** | `JZ src, target` | Jumps to `target` if `src` is equal to `0`. |
| **JNZ** | `JNZ src, target` | Jumps to `target` if `src` is NOT equal to `0`. |
| **CALL**| `CALL target` | Pushes PC to stack and jumps to `target`. |
| **RET** | `RET` | Pops address from stack into PC. |
| **INT** | `INT vector` | Triggers an interrupt using the vector table. |
| **IRET**| `IRET` | Returns from an interrupt service routine. |
| **HLT** | `HLT` | Halts the emulator execution safely. |

*Note: `dest` cannot be a literal value.*

## 💻 Assembly Syntax Examples

### Variables, Pointers, and Subroutines
```assembly
; Direct memory access
PUT 42 -> m0

; Pointer usage (Indirect addressing)
PUT 100 -> r1    ; Set r1 as a pointer to memory address 100
PUT 5 -> *r1     ; Write value 5 to memory address 100
PUT *r1 -> r2    ; Read from memory address 100 into r2

; Function Call and Stack Frame
CALL my_func
HLT

my_func:
PUSH BP          ; Save old Base Pointer
PUT SP -> BP     ; Establish new stack frame
; ... subroutine logic ...
PUT BP -> SP     ; Clean up local variables
POP BP           ; Restore old Base Pointer
RET              ; Return to caller
```

## 🌍 Ecosystem & Capabilities

This architecture is robust enough to support higher-level abstractions. As a proof of concept, this system supports Minilang a custom, C-style compiled programming language built specifically for this VM. The architecture handles Minilang's AST-compiled bytecode, supporting complex features like:

    A heap memory allocator (memalloc / free).

    Hardware polling for standard I/O.

    A bootstrapped "MiniOS" kernel running in user-space.

### Operand Types
* `lit` (Literal): Integer values (e.g., `5`, `-10`).
* `reg` (Register): General-purpose registers (e.g., `r1`).
* `mem` (Memory): Direct memory access (e.g., `m15`).
* `ptr` (Pointer): Indirect memory access via register (e.g., `*r1`).

### Supported Instructions

| Opcode | Syntax | Description |
| :--- | :--- | :--- |
| **ADD** | `ADD src1, src2 -> dest` | Adds `src1` and `src2`, stores result in `dest`. |
| **SUB** | `SUB src1, src2 -> dest` | Subtracts `src2` from `src1`, stores result in `dest`. |
| **INC** | `INC dest` | Increments the value in `dest` by 1. |
| **DEC** | `DEC dest` | Decrements the value in `dest` by 1. |
| **MUL** | `MUL src1, src2 -> dest` | Multiplies `src1` and `src2`, stores result in `dest`. |
| **DIV** | `DIV src1, src2 -> dest` | Divides `src1` by `src2`, stores integer result in `dest`. |
| **SHL** | `SHL src, amount -> dest` | Shifts the bits of `src` left by `amount`, stores result in `dest`. |
| **SHR** | `SHR src, amount -> dest` | Shifts the bits of `src` right by `amount`, stores result in `dest`. |
| **PUT** | `PUT src -> dest` | Moves value from `src` to `dest`. |
| **PUSH** | `PUSH src` | Pushes `src` onto the top of the stack. |
| **POP** | `POP dest` | Pops the top value of the stack into `dest`. |
| **JMP** | `JMP target` | Unconditional jump to `target` (Label or line number). |
| **JZ** | `JZ src, target` | Jumps to `target` if `src` is equal to `0`. |
| **JNZ** | `JNZ src, target` | Jumps to `target` if `src` is NOT equal to `0`. |
| **INT** | `INT vector` | Triggers a software interrupt using the specified `vector` index. |
| **IRET** | `IRET` | Returns from an interrupt service routine. |
| **CALL** | `CALL target` | Pushes the current PC to the stack and jumps to `target`. |
| **RET** | `RET` | Pops the return address from the stack into the PC. |
| **HLT** | `HLT` | Halts the emulator execution safely. |

*Note: `dest` cannot be a literal value.*

## 💻 Assembly Syntax Examples

### Variables, Pointers, and Subroutines
```assembly
; Direct memory access
PUT 42 -> m0

; Pointer usage (Indirect addressing)
PUT 100 -> r1    ; Set r1 as a pointer to memory address 100
PUT 5 -> *r1     ; Write value 5 to memory address 100
PUT *r1 -> r2    ; Read from memory address 100 into r2

; Function Call and Stack Frame
CALL my_func
HLT

my_func:
PUSH BP          ; Save old Base Pointer
PUT SP -> BP     ; Establish new stack frame
; ... subroutine logic ...
PUT BP -> SP     ; Clean up local variables
POP BP           ; Restore old Base Pointer
RET              ; Return to caller
```