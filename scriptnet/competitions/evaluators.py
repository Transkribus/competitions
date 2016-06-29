# This file contains all functions available to compute numerical results
# for user uploaded method results.

from random import random
from time import sleep

def random_integer_slow():
    print('random_integer_slow has been called!')
    sleep(20)
    return int(random()*100)

def random_scalar():
    print('random_scalar has been called!')
    return random()