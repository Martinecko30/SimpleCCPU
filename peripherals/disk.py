from peripherals.peripheral import Peripheral


class Disk(Peripheral):
    def __init__(self, start_address: int):
        super().__init__(start_address, start_address, irq_vector=-1)

    def write_data(self, address: int, value: int) -> bool:
        """The CPU calls this when writing to the GPU's VRAM addresses."""

    def read_data(self, address: int) -> int:
        """Allows the CPU to read what is currently on the screen."""
