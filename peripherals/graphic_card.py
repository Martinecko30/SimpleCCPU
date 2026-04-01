import os

from peripherals.peripheral import Peripheral


class GraphicsCard(Peripheral):
    def __init__(self, start_address: int, width: int = 20, height: int = 5):
        self.width = width
        self.height = height
        self.__vram_size = width * height

        # The GPU claims memory from start_address to (start_address + vram_size - 1)
        end_address = start_address + self.__vram_size - 1
        super().__init__(start_address, end_address,
                         irq_vector=-1)  # GPU doesn't interrupt here

        # Initialize VRAM with spaces (ASCII 32)
        self.__vram = [32] * self.__vram_size

        self.render()

    def write_data(self, address: int, value: int) -> None:
        """The CPU calls this when writing to the GPU's VRAM addresses."""
        # Calculate which pixel/character the CPU is trying to change
        local_index = address - self.start_address

        if 0 <= local_index < self.__vram_size:
            self.__vram[local_index] = value

            self.render()

    def read_data(self, address: int) -> int:
        """Allows the CPU to read what is currently on the screen."""
        local_index = address - self.start_address
        if 0 <= local_index < self.__vram_size:
            return self.__vram[local_index]
        return 0

    def render(self):
        """Physically draws the VRAM to your Python terminal."""
        os.system('cls' if os.name == 'nt' else 'clear')

        print("+" + "-" * self.width + "+")

        for y in range(self.height):
            row = ""
            for x in range(self.width):
                idx = y * self.width + x
                # Only print valid printable ASCII characters, otherwise print '?'
                char = chr(self.__vram[idx]) if 32 <= self.__vram[idx] <= 126 else '?'
                row += char
            print("|" + row + "|")

        print("+" + "-" * self.width + "+")