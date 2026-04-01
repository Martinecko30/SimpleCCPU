from computer import Computer
from peripherals.graphic_card import GraphicsCard
from peripherals.keyboard import Keyboard

if __name__ == "__main__":
    debug = False
    keyboard = Keyboard(start_address=10, irq_vector=1)
    gpu = GraphicsCard(start_address=100, width=40, height=1)

    computer = Computer(1024 * 8, keyboard, gpu)
    result = computer.start("program.casm", debug, False)
    print(result)