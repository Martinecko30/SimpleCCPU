from emulator import Emulator

def basic_tests():
    emul = Emulator(2 ** 4)
    debug = False
    print(emul.run_program("tests/test.casm", debug))
    emul.reset()

    print("\n=================")
    print(emul.run_program("tests/factorial.casm", debug))
    emul.reset()

    print("\n=================")
    print(emul.run_program("tests/fibonacci.casm", debug))
    emul.reset()

if __name__ == "__main__":
    emul = Emulator(2 ** 8)
    debug = True
    print(emul.run_program("minilang/minilang_interpreter.casm", debug))
    emul.reset()
