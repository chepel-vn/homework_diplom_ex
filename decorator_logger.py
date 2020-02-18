from os import path
import datetime


def get_name_module(file_path):
    """

    (string) -> string

    Function get name of file from path without file extension

    """
    file_name = path.basename(file_path)
    idx = file_name.index('.')
    return file_name[:idx]


def logger_path_decorator(file_path='file1.log'):
    def logger_decorator(function):
        """

        (address of function) -> address of function

        Function-decorator which logging to text file about input and output data and start time of execute of function


        """

        def wrapper(*args, **kwargs):

            # If file exists then create file
            if not path.exists(file_path):
                with open(file_path, 'w', encoding='utf-8'):
                    pass

            with open(file_path, 'a', encoding='utf-8') as file:
                lines = f"{datetime.datetime.now()}: Вызов функции \"{function.__name__}\":\n"
                lines += f"Аргументы функции \"{function.__name__}\":\n"
                for number, argument in enumerate(args, 1):
                    lines += f"аргумент №{number}: {argument}\n"
                for key, value in kwargs.items():
                    lines += f"аргумент \"{key}\": {value}\n"
                return_value = function(*args, **kwargs)
                lines += f"Возвращаемое значение функции равно: {return_value}\n"
                file.writelines(lines)
            return return_value
        return wrapper
    return logger_decorator


# Example 1
@logger_path_decorator()
def function1_to_decorate(**kwargs):
    summa = 0
    for key, value in kwargs.items():
        summa += value
    return str(summa)

# Example 2
@logger_path_decorator()
def function2_to_decorate(*args):
    summa = 0
    for argument in args:
        summa += argument
    return str(summa)


if __name__ == "__main__":
    function1_to_decorate(a=1, b=2, c=3)
    function2_to_decorate(1, 2, 3)



