import time

def write_function_results_to_file(func):
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        with open('results.txt', 'a', encoding='UTF-8') as file:
            file.write("_______________\n")
            file.write(f"Название функции: {func.__name__}\n")
            if not isinstance(result, str):
                file.write(f"Результат выполнения функции: \n\n")
                file.write(f"{result}\n\n")
            else:
                file.write(f"Результат выполнения функции: {result}\n")
            file.write(f"Время выполнения функции: {execution_time} секунд\n")
            file.write("_______________\n")
    return wrapper