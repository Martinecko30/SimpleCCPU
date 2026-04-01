from typing import Optional

from system_bus import SystemBus


class Peripheral:
    def __init__(self, start_address: int, end_address: int,
                 irq_vector: int = -1):
        self.start_address = start_address
        self.end_address = end_address
        self.irq_vector = irq_vector
        self.bus: Optional[SystemBus] = None

    def connect_to_bus(self, bus: SystemBus) -> None:
        self.bus = bus

    def trigger_irq(self) -> None:
        if self.bus and self.irq_vector != -1:
            self.bus.raise_interrupt(self.irq_vector)

    def read_data(self, address: int) -> int:
        return 0

    def write_data(self, address: int, value: int) -> None:
        pass