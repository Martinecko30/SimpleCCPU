# CASM (Custom Assembly) Emulator

A lightweight, Turing-complete Virtual Machine and Custom Assembly (CASM) emulator written in Python. This project features a custom Instruction Set Architecture (ISA), a two-pass parser with label support, indirect memory addressing (pointers), and a fully functional stack.

## ✨ Features

* **Custom ISA:** 11 core instructions providing full control over arithmetic, memory, and control flow.
* **Harvard-like parsing / Von Neumann-like memory:** Code and data are conceptually separated during execution, but memory fully supports dynamic read/write operations.
* **Two-Pass Assembler:** Write clean code using `labels:` instead of raw instruction line numbers.
* **Indirect Addressing (Pointers):** Access memory dynamically using pointers stored in registers (e.g., `*r1`).
* **Hardware Stack:** Built-in support for `PUSH` and `POP` operations (stack grows downwards from the top of memory).
* **Inline Comments:** Fully supports assembly comments using `;`.

## 🏗️ Architecture Specs

* **Registers:** 6 general-purpose registers (`r1`, `r2`, `r3`, `r4`, `r5`, `r6`).
* **Memory:** Configurable size (e.g., 256 bytes), initialized to `0`.
* **Program Counter (PC):** Tracks the current instruction.
* **Stack Pointer (SP):** Starts at `memory_size - 1` and grows downwards towards `0`.

## 📖 Instruction Set Architecture (ISA)

The emulator uses a specific syntax with the `->` operator to clearly distinguish source and destination operands.

### Operand Types
* `lit` (Literal): Integer values (e.g., `5`, `-10`).
* `reg` (Register): General-purpose registers (e.g., `r1`).
* `mem` (Memory): Direct memory access (e.g., `m15`).
* `ptr` (Pointer): Indirect memory access via register (e.g., `*r1`).

### Supported Instructions

| Opcode | Syntax | Description |
| :--- | :--- | :--- |
| **PUT** | `PUT src -> dest` | Moves value from `src` to `dest`. |
| **ADD** | `ADD src1, src2 -> dest` | Adds `src1` and `src2`, stores result in `dest`. |
| **SUB** | `SUB src1, src2 -> dest` | Subtracts `src2` from `src1`, stores result in `dest`. |
| **INC** | `INC dest` | Increments the value in `dest` by 1. |
| **DEC** | `DEC dest` | Decrements the value in `dest` by 1. |
| **PUSH**| `PUSH src` | Pushes `src` onto the top of the stack. |
| **POP** | `POP dest` | Pops the top value of the stack into `dest`. |
| **JMP** | `JMP target` | Unconditional jump to `target` (Label or line number). |
| **JZ** | `JZ src, target` | Jumps to `target` if `src` is equal to `0`. |
| **JNZ** | `JNZ src, target` | Jumps to `target` if `src` is NOT equal to `0`. |
| **HLT** | `HLT` | Halts the emulator execution safely. |

*Note: `dest` cannot be a literal value.*

## 💻 Assembly Syntax Examples

### Variables & Pointers
```assembly
; Direct memory access
PUT 42 -> m0

; Pointer usage (Indirect addressing)
PUT 100 -> r1    ; Set r1 as a pointer to memory address 100
PUT 5 -> *r1     ; Write value 5 to memory address 100
PUT *r1 -> r2    ; Read from memory address 100 into r2