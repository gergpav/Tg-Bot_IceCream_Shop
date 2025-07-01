def deserialize_callback_data(data: str):
    # Преобразует строку обратно в кортеж
    return tuple(data.split("|"))