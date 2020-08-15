DEBUG = False


def debug_output(func):
    def func_wrapper(*args, **kwargs):
        value = func(*args, **kwargs)
        if DEBUG:
            output = f"{func.__qualname__} | {args} | {kwargs}"
            if value is not None:
                output += f" | {value}"
            print(output)
        return value

    return func_wrapper
