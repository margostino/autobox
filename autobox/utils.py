from typing import Any, Callable, Tuple, Union

from openai.types.chat import ChatCompletion


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


def spin_with_handler(
    message: str,
    fn_state_handler: Callable[[ChatCompletion], str],
    callable: Callable[[], Tuple[Any, bool, Union[str, None]]],
) -> Any:
    from halo import Halo

    spinner = Halo(text=message, spinner="spinner")
    spinner.start()
    result, success, final_message = callable()
    spinner.stop()
    if success:
        log_result = fn_state_handler(result)
        spinner.succeed(log_result or final_message or message)
    else:
        spinner.fail(final_message or message)
    return result


def handle(fn: Callable[[str], str]) -> Callable[[str], str]:
    def inner(text: str) -> str:
        return fn(text)

    return inner


def extract_chat_completion(completion: ChatCompletion):
    tool_calls = completion.choices[0].message.tool_calls
    extracted_tool_calls = []
    if tool_calls is not None and len(tool_calls):
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            arguments = tool_call.function.arguments
            extracted_tool_calls.append(
                {"function_name": function_name, "arguments": arguments}
            )
    else:
        return completion.choices[0].message.content, False

    return extracted_tool_calls, True
