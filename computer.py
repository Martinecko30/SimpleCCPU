from emulator import Emulator, Status
from peripherals.peripheral import Peripheral
from system_bus import SystemBus

class Computer:
    def __init__(self, memory_size: int, *peripherals: Peripheral, memory=None):
        self.__bus = SystemBus(memory_size, memory)
        self.__cpu = Emulator(self.__bus)
        self.__peripherals: list[Peripheral] = list(peripherals)

        for p in self.__peripherals:
            self.__bus.connect_device(p)

    def start(self, program: str, debug: bool, should_reset: bool) -> Status:
        result = self.__cpu.run_program(program, debug)

        if should_reset:
            self.__cpu.reset()

        return result[0]