import logging
import employee

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler("test.log")
file_handler.setLevel(logging.ERROR)
formatter = logging.Formatter("%(asctime)s: %(name)s: %(message)s")

file_handler.setFormatter((formatter))
logger.addHandler(file_handler)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def add(x, y):
    return x + y

def substract(x, y):
    return x - y

def multiply(x, y):
    return x * y

def divide(x, y):
    try:
        result = x / y
    except ZeroDivisionError:
        logger.exception("Tried to divide by zero")
    else:
        return result

num_1 = 20
num_2 = 0

add_result = add(num_1, num_2)
logger.debug("{} + {} = {}".format(num_1, num_2, add_result))

substract_result = substract(num_1, num_2)
logger.debug("{} - {} = {}".format(num_1, num_2, substract_result))

multiply_result = multiply(num_1, num_2)
logger.debug("{} * {} = {}".format(num_1, num_2, multiply_result))

divide_result = divide(num_1, num_2)
logger.debug("{} / {} = {}".format(num_1, num_2, divide_result))

