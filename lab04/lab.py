#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION


def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    
    return new_game_nd((num_rows, num_cols), bombs)
       


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    return dig_nd(game, (row, col))


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)         



def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    return '\n'.join(''.join(element) for element in render_2d_locations(game, xray))


# N-D IMPLEMENTATION

def get_value(array, coord):
    """
    Get the value of a location specified by coordinates in an array. 

    Args:
        array (list): nd array
        coord (tuple): location
    
    Returns:
        the value

    >>> board = [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 10], [11, 12]]]
    >>> get_value(board, (1, 1, 1))
    10
    """

    if len(coord) == 1:
        return array[coord[0]]
    else:
        return get_value(array[coord[0]], coord[1:])

def set_value(array, coord, value):
    """
    Set the value of a location specified by coordinates in an array. 

    Args:
        array (list): nd array
        coord (tuple): location
        value (int, str): value

    Returns:
        nothing

    >>> board = [[[1,2], [3,4], [5,6]], [[7,8], [9,10], [11,12]]]
    >>> set_value(board, (1, 1, 1), 99)
    >>> board
    [[[1, 2], [3, 4], [5, 6]], [[7, 8], [9, 99], [11, 12]]]
    """

    if len(coord) == 1:
        array[coord[0]] = value
    else:
        set_value(array[coord[0]], coord[1:], value)

def fill_array(dimensions, value):
    """
    Return an nd array filled with entries of the same value

    Args: 
        dimensions (tuple): dimensions of the board
        value (int, str): value to fill the board with

    Returns:
        the filled nd array
    
    >>> board = fill_array((2, 3, 2), 1)
    >>> board
    [[[1, 1], [1, 1], [1, 1]], [[1, 1], [1, 1], [1, 1]]]
    """
    if len(dimensions) == 1:
        return [value for i in range(dimensions[0])]
    else:
        return [fill_array(dimensions[1:], value) for i in range(dimensions[0])]

def get_state(game):
    """
    Return if the game is ongoing, victory, or defeat

    >>> my_game = new_game_nd((2, 3, 2), [(0, 0, 0), (1, 1, 1)])
    >>> get_state(my_game)
    'ongoing'
    >>> dig_nd(my_game, (0,0,0))
    1
    >>> get_state(my_game)
    'defeat'
    """

    for coord in get_all_coords(game['dimensions']):
        if get_value(game['board'], coord) == '.':
            if get_value(game['visible'], coord):
                return 'defeat'
        else:
            if not get_value(game['visible'], coord) and isinstance((get_value(game['board'], coord)), int):
                return 'ongoing'
    return 'victory'

def get_neighbors(dimensions, coord):
    """
    Returns all tuples of coordinates of neigbors given the dimensions
    Generator allows us to loop through and create sets

    Args: 
        dimensions (tuple): dimensions of the board
        coord (tuple): cell to find neighbors of

    Returns:
        generator object with neighbors as tuples

    >>> my_dimensions = (2, 3, 2)
    >>> my_set = set()
    >>> my_set.update(get_neighbors(my_dimensions, (1,2,1)))
    >>> my_set == {(1, 2, 1), (0, 2, 1), (1, 1, 0), (0, 1, 0), (1, 2, 0), (0, 2, 0), (1, 1, 1), (0, 1, 1)}
    True
    """

    pm = [-1, 0, 1] # pm stands for plus minus
    if len(dimensions) == 0:
        yield tuple()
    else:
        for i in range(3):
            if 0 <= coord[0]+pm[i] < dimensions[0]:
                for j in get_neighbors(dimensions[1:], coord[1:]):
                    yield (coord[0]+pm[i],)+j 

def get_all_coords(dimensions):
    """
    Returns all possible tuples of coordinates given the dimensions 
    Generator allows us to loop through and create sets

    >>> my_dimensions = (2, 3, 2)
    >>> my_set = set()
    >>> my_set.update(get_all_coords(my_dimensions))
    >>> my_set == {(0,0,0), (0,0,1), (0,1,0), (0,1,1), (0,2,0), (0,2,1), (1,0,0), (1,0,1), (1,1,0), (1,1,1), (1,2,0), (1,2,1)}
    True
    """

    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            yield (i,)
    else:
        for i in range(dimensions[0]):
            for j in get_all_coords(dimensions[1:]):
                yield (i,)+j

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    board = fill_array(dimensions, 0)
    visible = fill_array(dimensions, False)
    for coord in bombs:
        set_value(board, coord, '.')
        for neighbor in get_neighbors(dimensions, coord):
            try:
                set_value(board, neighbor, get_value(board, neighbor)+1)
            except:
                continue
    return {
    'board': board,
    'dimensions': dimensions,
    'state': 'ongoing',
    'visible': visible,
    }

def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """
    
    if game['state'] != 'ongoing' or get_value(game['visible'], coordinates):
        return 0
    
    value = get_value(game['board'], coordinates)
    set_value(game['visible'], coordinates, True)

    if value == '.':
        game['state'] = 'defeat'
        return 1
    else:
        total = 1
        if value == 0:
            for neighbor in get_neighbors(game['dimensions'], coordinates):
                total += dig_nd(game, neighbor)
        if get_state(game) == 'victory':
            game['state'] = 'victory'
        return total

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """

    rendered = fill_array(game['dimensions'], 'bing chilling')
    if xray:
        for coord in get_all_coords(game['dimensions']):
            value = get_value(game['board'], coord)
            set_value(rendered, coord, ' ' if value ==0 else str(value))
    else:
        for coord in get_all_coords(game['dimensions']):
            value = get_value(game['board'], coord)
            visibility = get_value(game['visible'], coord)
            if visibility:
                set_value(rendered, coord, ' ' if value == 0 else str(value))
            else:
                set_value(rendered, coord, '_')
    return rendered

                

        

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )
    # print(set(get_all_coords((2,3,2))))
    # print(set(get_neighbors((2,3,2),(1,2,1))))
    # doctest.run_docstring_examples(
    #     render_nd,
    #     globals(),
    #     optionflags= _doctest_flags,
    #     verbose = True
    # )