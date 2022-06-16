# 6.009 Lab 2: Snekoban

import json
from tabnanny import check
import typing

# NO ADDITIONAL IMPORTS! bruh

d_v = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return level_description

def player_pos(game):

    '''returns row and column of player in a tuple'''
    for i in range(len(game)):
        for j in range(len(game[i])):
            if 'player' in game[i][j]:
                return (i,j)

def check_cell(game, pos, direction): 
    if game[pos[0]+d_v[direction][0]][pos[1]+d_v[direction][1]] == []:
        return 'empty'
    elif game[pos[0]+d_v[direction][0]][pos[1]+d_v[direction][1]] == ['wall']: 
        return 'no move'
    elif 'computer' in game[pos[0]+d_v[direction][0]][pos[1]+d_v[direction][1]]:
        if game[pos[0]+2*d_v[direction][0]][pos[1]+2*d_v[direction][1]] == []:
            if bad_cell(game, game[pos[0]+2*d_v[direction][0]][pos[1]+2*d_v[direction][1]]):
                return 'no move'
            else:
                return 'move computer'
        elif game[pos[0]+2*d_v[direction][0]][pos[1]+2*d_v[direction][1]] == ['target']:
            return 'move computer' 
        '''if game[int(pos[0]+2*d_v[direction][0])][int(pos[1]+2*d_v[direction][1])] == [] or game[int(pos[0]+2*d_v[direction][0])][int(pos[1]+2*d_v[direction][1])] == ['target']:
                return 'move computer'
        else:
            return 'no move' '''
    else:
        return 'target'

def bad_cell(game, pos): 
    total = 0
    try:
        if game[pos[0]+1][pos[1]] == ['wall']:
            total+=1
        if game[pos[0]][pos[1]+1] == ['wall']:
            total+=1
        if game[pos[0]-1][pos[1]] == ['wall']:
            total+=1
        if game[pos[0]][pos[1]-1] == ['wall']:
            total+=1
        if total >= 2:
            return True
    except IndexError:
        return False
    return False
def deep_copy(game):
    return [[x[:] for x in y] for y in game]

def valid_moves(game, pos):
    out = []
    for each in (d_v):
        if check_cell(game, pos, each) != 'no move':
            out.append(each)
    return out

def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    total = 0
    for _ in (game):
        for i in (_):
            if ('computer' in i)^('target' in i):
                return False
            if 'computer' in i:
                total+=1
    if total == 0:
        return False
    return True


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    game_new = deep_copy(game)
    wya = player_pos(game_new)
    decision = check_cell(game_new, wya, direction)
    if decision == 'empty' or decision == 'target':
        game_new[wya[0]][wya[1]].remove('player')
        game_new[wya[0]+d_v[direction][0]][wya[1]+d_v[direction][1]].append('player')
              
    elif decision == 'move computer':
        game_new[wya[0]][wya[1]].remove('player')
        game_new[wya[0]+d_v[direction][0]][wya[1]+d_v[direction][1]].append('player')
        game_new[wya[0]+d_v[direction][0]][wya[1]+d_v[direction][1]].remove('computer')
        game_new[wya[0]+2*d_v[direction][0]][wya[1]+2*d_v[direction][1]].append('computer')
  
    return game_new

def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game

def simplify(game):
    computer_list = []
    
    for i in range(len(game)):
        for j in range(len(game[i])):
            if 'computer' in game[i][j]:
                computer_list.append((i,j))
    return (player_pos(game)+tuple(computer_list))

def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    if victory_check(game):
        return []
    agenda = [game]
    simplified = simplify(game)
    visited = {simplified: None}
    current_list = []
    while current_list:
        #current_game = agenda.pop(0)
        updated_list = []
        for current_game in (current_list):
            
            simplified_current = simplify(current_game)
            possible_moves = valid_moves(current_game, player_pos(current_game))
            for move in (possible_moves):
                new_game = step_game(current_game, move)

                simplified_new = simplify(new_game)
                if simplified_new not in visited:
                    #agenda.append(new_game)
                    updated_list.append(new_game)
                    visited[simplified_new] = (simplified_current, move)
                    
                    if victory_check(new_game):
                        list_moves = []
                        while visited[simplified_new] != None:
                            list_moves.append(visited[simplified_new][1])
                            
                            simplified_new = visited[simplified_new][0]
                        return list_moves[::-1]
        current_list = updated_list
        


    

if __name__ == "__main__":
    solve_puzzle([
  [
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"]
  ],
  [["wall"], [], [], [], [], [], [], ["wall"]],
  [
    ["wall"],
    [],
    ["target"],
    ["computer"],
    [],
    [],
    ["player"],
    ["wall"]
  ],
  [["wall"], [], [], [], [], [], [], ["wall"]],
  [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], [], [], ["wall"]],
  [[], [], [], [], ["wall"], ["wall"], ["wall"], ["wall"]]
])
    test_case = [
  [
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"]
  ],
  [["wall"], [], [], [], [], [], [], ["wall"]],
  [
    ["wall"],
    [],
    ["target"],
    ["computer"],
    [],
    [],
    ["player"],
    ["wall"]
  ],
  [["wall"], [], [], [], [], [], [], ["wall"]],
  [["wall"], ["wall"], ["wall"], ["wall"], ["wall"], [], [], ["wall"]],
  [[], [], [], [], ["wall"], ["wall"], ["wall"], ["wall"]]
]


