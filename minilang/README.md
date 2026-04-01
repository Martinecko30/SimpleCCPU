# 🚀 Minilang

Minilang is a lightweight, C-style compiled programming language built from the ground up for custom 8-bit and 16-bit virtual machine architectures. 

Instead of manually managing registers, pushing/popping from the stack, and tracking memory addresses, Minilang provides a high-level abstraction. It features an Abstract Syntax Tree (AST) based compiler that handles complex pointer arithmetic, scoped local variables via Stack Frames, and nested control flow, compiling directly down to machine-readable Custom Assembly (CASM).

## ✨ Key Features

* **Turing-Complete Abstraction:** Write complex algorithms without touching a single CPU register.
* **True Local Scope:** Every `FUNC` automatically generates a secure Stack Frame using a Base Pointer (`BP`). Local variables (`LET`) are isolated and recursion is fully supported.
* **Advanced Pointer Logic:** Native support for memory addressing (`&`) and dereferencing (`*`), allowing you to write heap allocators and interact directly with memory-mapped hardware.
* **First-Class Arrays:** Global contiguous memory blocks for buffers, strings, and data structures.
* **Bootstrapping Capable:** The language is powerful enough to be self-hosted (compiling itself) and to write foundational software like a "MiniOS" kernel.

---

## 📖 Language Syntax & Reference

### 1. Variables and Data Structures
Minilang operates on a single primitive data type (integers/machine words). 

```minilang
// Declare a global array of 256 words
ARRAY heap[256]

FUNC example()
    // Declare a scoped local variable
    LET a = 5
    LET b = 10
    
    // Mathematical assignment
    LET c = a + b
    
    // Array indexing
    heap[0] = c
    LET first_item = heap[0]
ENDFUNC
```

### 2. Control Flow

Minilang supports conditional branching and loops. Conditions evaluate to true if they are non-zero.
Code snippet

```minilang
FUNC logic_example(x, y)
    LET diff = x - y
    
    // IF / ELSE
    IF diff
        // Executes if x != y (diff is non-zero)
        PUTC 65 // Print 'A'
    ELSE
        // Executes if x == y (diff is 0)
        PUTC 66 // Print 'B'
    END
    
    // WHILE loops
    LET counter = 5
    WHILE counter
        counter = counter - 1
    END
ENDFUNC
```

### 3. Functions and Scope

Functions are declared with FUNC and ENDFUNC. The compiler automatically injects prologues and epilogues to safely preserve the call stack.
Code snippet

```minilang
FUNC add_numbers(x, y)
    LET result = x + y
    RETURN result
ENDFUNC

FUNC main()
    LET sum = CALL add_numbers(10, 20)
ENDFUNC
```

### 4. Pointers and Hardware Interfacing

Minilang excels at low-level memory manipulation, making it ideal for writing Operating Systems and hardware drivers.
Code snippet

```minilang
FUNC hardware_polling()
    // 10 is the memory-mapped address of the Keyboard buffer
    LET kbd_addr = 10 
    LET key = 0
    
    WHILE 1
        // Pointer Dereference: Read the value AT address 10
        key = *kbd_addr 
        
        IF key
            RETURN key
        END
    END
ENDFUNC

FUNC pointer_math()
    ARRAY source[5]
    // Address-Of operator: Pass the memory address of the array
    CALL process_data(&source) 
ENDFUNC
```

### 🛠️ The Compiler Pipeline

When you run the Minilang Compiler, your code undergoes several transformations:

1. Lexical Analysis: The source .mini file is stripped of comments (//) and broken down into recognizable tokens.

2. AST Generation (Parsing): The tokens are parsed recursively into an Abstract Syntax Tree. WHILE loops and IF blocks swallow their internal statements into nested node structures, ensuring mathematical order of operations is strictly respected.

3. Code Generation (Visitor): The compiler visits each node in the AST.

   - LET triggers stack allocations (PUSH 0).

   - Mathematics (BinOp) safely resolve to temporary hardware registers.

   - Pointers (Dereference / AddressOf) are calculated dynamically.

4. Output: Clean, optimized .casm (Custom Assembly) is generated, ready to be executed by the CPU emulator.

### 🌟 Example: A Custom Memory Allocator (MiniOS)

Because Minilang supports pointers and arrays, you can write foundational OS systems like a Heap Allocator directly in the language:

```miniliang
ARRAY heap_map[256]

// Scans the heap_map for the first available free block
FUNC memalloc(size)
    LET i = 0
    LET free_count = 0
    LET start_idx = 0
    LET cond = 256 - i
    
    WHILE cond
        IF heap_map[i]
            free_count = 0 // Block is used, reset counter
        ELSE
            IF free_count
            ELSE
                start_idx = i // Mark potential start
            END
            
            free_count = free_count + 1
            LET diff = size - free_count
            
            IF diff
                // Still counting
            ELSE
                // Found enough space! Return the memory pointer.
                RETURN start_idx
            END
        END
        i = i + 1
        cond = 256 - i
    END
    RETURN -1 // Out of Memory
ENDFUNC
```