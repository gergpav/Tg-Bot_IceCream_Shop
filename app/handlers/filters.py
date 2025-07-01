from typing import Callable
from app.handlers.deserializator import deserialize_callback_data


def filter_for_command(command: str) -> Callable[[tuple[str]], bool]:
    return lambda callback_data: deserialize_callback_data(callback_data)[0] == command