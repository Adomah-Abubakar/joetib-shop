# This file contains two implementations of the factorial calculation.
# One implemented with regular recursion and the other with tail-call optimization


def factorial(number: int) -> int:
    """This is the regular implementation of factorial with recursion"""

    if number == 0:
        return 1

    # Here the runtime needs to keep track of the current number until
    # the recursive call to factorial returns in other to do the last computation (the multiplication)
    # This means the current stack needs to be kept in memory until the last recursive call 
    # completes. For large values of number, this may result in a stack overflow.
    return factorial(number - 1)  * number



def factorial_with_tail_call(number: int, accumulator=1):
    """ This implements `factorial` with tail call optimization.

    The notable difference is the fact that the last executable statment is a recursive call to this
    same function. Giving way for the interpreter to optimize by clearing our memory or reusing the current
    stack as it is no longer needed.

    Unfortunately python does not internally implement `tail call` recursion.
    """
    if number == 0: 
        return accumulator

    # The earlier variables in this function are no longer needed as all required data will 
    # now be passed to the recursive call.
    return factorial_with_tail_call(number-1, accumulator * number)