# solves a sudoku with a recursive backtracking algorithm
import time, random


def find_empty_location(sudoku: list) -> [bool, int]:
    for pos in range(81):
        if sudoku[pos] == 0:
            return [True, pos]
    return [False, -1]


def is_in_row(sudoku: list, loc: int, num: int) -> bool:
    row = int(loc / 9)
    for digit in sudoku[row*9: row*9 + 9]:
        if digit == num:
            return True
    return False


def is_in_col(sudoku: list, loc: int, num: int) -> bool:
    col_num = loc % 9
    for i in range(9):
        if sudoku[col_num + 9*i] == num:
            return True
    return False


def is_in_group(sudoku: list, loc: int, num: int) -> bool:
    row = int(loc / 9)
    col = loc % 9
    group_top_left = (row - row % 3)*9 + (col - col % 3)
    for i in range(3):
        for j in range(3):
            if sudoku[group_top_left + i*9 + j] == num:
                return True
    return False


def location_is_valid(sudoku: list, loc: int, num: int) -> bool:
    return not is_in_row(sudoku, loc, num) and not is_in_col(sudoku, loc, num) and not is_in_group(sudoku, loc, num)


# Returns true if the sudoku is finished
def solve(sudoku: list, cells: list) -> bool:
    empty_loc = find_empty_location(sudoku)
    time.sleep(0.1)
    if not empty_loc[0]:
        return True

    loc = empty_loc[1]

    # Go through 1 to 9 in a random order, this has two reasons:
    # 1. Randomisation in constraint satisfaction usually speeds up solutions
    # 2. In case I want to add random generation of valid boards, this can be used to generate finished board
    order = list(range(1, 10))
    random.shuffle(order)
    for digit in order:
        if location_is_valid(sudoku, loc, digit):

            # Assign guess
            cells[loc].set_mode('entry')
            cells[loc].set_value(digit)
            cells[loc].repaint()
            sudoku[loc] = digit

            # Because this will search for the next empty location, this recursion is enough
            if solve(sudoku, cells):
                return True

            # If this number is invalid, try again with the next number
            sudoku[loc] = 0
            cells[loc].set_mode('failure')
            cells[loc].set_value(0)
            cells[loc].repaint()

    # In case no number is fitting for this it will backtrack
    return False
