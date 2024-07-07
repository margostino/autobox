from typing import Any, Callable, Tuple, Union


def red(text: str):
    return f"\033[1;31m{text}\033[0;0m"


def yellow(text: str):
    return f"\033[1;33m{text}\033[0;0m"


def green(text: str):
    return f"\033[1;32m{text}\033[0;0m"


def blue(text: str):
    return f"\033[1;34m{text}\033[0;0m"


def spin(
    message: str, callable: Callable[[], Tuple[Any, bool, Union[str, None]]]
) -> Any:
    from halo import Halo

    spinner = Halo(text=message, spinner="spinner")
    spinner.start()
    result, success, final_message = callable()
    spinner.stop()
    if success:
        spinner.succeed(final_message or message)
    else:
        spinner.fail(final_message or message)
    return result


def log(colour, text):
    print(f"{colour(text)}")
