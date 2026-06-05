from computer import Computer
from peripherals.graphic_card import GraphicsCard
from peripherals.keyboard import Keyboard

if __name__ == "__main__":
    debug = False
    keyboard = Keyboard(start_address=10, irq_vector=1)
    gpu = GraphicsCard(start_address=100, width=20, height=3)

    computer = Computer(512 * 8, keyboard, gpu)
    status, memory = computer.start("compiler/program.casm", debug, False)
    print(status)

    if debug:
        for i in range(len(memory)):
            if i % 10 == 0:
                print()
            print(f"m{i}: {memory[i]} | ", end="")
