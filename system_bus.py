from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from peripherals.peripheral import Peripheral


class SystemBus:
    def __init__(self, memory_size: int, memory: list[int] | None = None):
        if memory is None:
            self.ram = [0] * memory_size
        else:
            self.ram = memory
        self.memory_size = memory_size

        self.devices: list[Peripheral] = []

        self.interrupt_line: Optional[int] = None

    def connect_device(self, device: Peripheral):
        self.devices.append(device)
        device.connect_to_bus(self)

    def read(self, address: int) -> int:
        for dev in self.devices:
            if dev.start_address <= address <= dev.end_address:
                return dev.read_data(address)

        if 0 <= address < self.memory_size:
            return self.ram[address]
        return 0

    def write(self, address: int, value: int):
        for dev in self.devices:
            if dev.start_address <= address <= dev.end_address:
                dev.write_data(address, value)
                return

        if 0 <= address < self.memory_size:
            self.ram[address] = value

    def raise_interrupt(self, vector: int):
        self.interrupt_line = vector