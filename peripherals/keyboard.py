from collections import deque
from typing import Deque

from pynput import keyboard
from pynput.keyboard import KeyCode

from peripherals.peripheral import Peripheral


class Keyboard(Peripheral):
    def __init__(self, start_address: int, irq_vector: int) -> None:
        super().__init__(
            start_address=start_address,
            end_address=start_address,
            irq_vector=irq_vector
        )

        self.__buffer: Deque[int] = deque()

        self.pressed_keys = set()

        self.listener = keyboard.Listener(
            on_press=self._on_physical_key_press,
            on_release=self._on_physical_key_release
        )
        self.listener.start()

    def _on_physical_key_press(self, key: KeyCode | None) -> None:
        if key is None:
            return

        try:
            char = key.char
            if char is not None and len(char) == 1:
                if char not in self.pressed_keys:
                    self.pressed_keys.add(char)
                    self.press_key(char)
        except AttributeError:
            pass

    def _on_physical_key_release(self, key: KeyCode | None) -> None:
        if key is None:
            return
        try:
            char = key.char
            if char in self.pressed_keys:
                self.pressed_keys.remove(char)
        except AttributeError:
            pass

    def press_key(self, char: str | None) -> None:
        if char is not None and len(char) == 1:
            self.__buffer.append(ord(char))
            self.trigger_irq()

    def read_data(self, address: int) -> int:
        if address == self.start_address:
            if self.__buffer:
                return self.__buffer.popleft()
        return 0

    def write_data(self, address: int, value: int) -> None:
        """You cannot write to a basic keyboard data register."""
        pass