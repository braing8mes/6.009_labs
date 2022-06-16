# 6.009 Lab 2: Snekoban

from ast import dump
import json
import string
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
    dimensions = (len(level_description), len(level_description[0]))
    targets = get_pos(level_description, 'target')
    computers = get_pos(level_description, 'computer')
    walls = get_pos(level_description, 'wall')
    player = get_pos(level_description, 'player')
    for each in (player):
        player = each
    empty_set = set()
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            if level_description[i][j] == []:
                empty_set.add((i,j))

    return [player, computers, targets, walls, empty_set, dimensions]
    
def get_pos(raw_repr, object):
    object_set = set()
    for i in range(len(raw_repr)):
        for j in range(len(raw_repr[i])):
            if object in raw_repr[i][j]:
                object_set.add((i,j))
    return object_set

def player_pos(game):
    '''returns row and column of player in a tuple'''
    return game[0]

def check_cell(game, pos, direction): 
    if (pos[0]+d_v[direction][0],pos[1]+d_v[direction][1]) in game[4]:
        return 'empty'
    elif (pos[0]+d_v[direction][0],pos[1]+d_v[direction][1]) in game[3]: 
        return 'no move'
    elif (pos[0]+d_v[direction][0],pos[1]+d_v[direction][1]) in game[1]:
        if (pos[0]+2*d_v[direction][0],pos[1]+2*d_v[direction][1]) in game[4]:
            if bad_cell(game, (pos[0]+2*d_v[direction][0],pos[1]+2*d_v[direction][1])):
                return 'no move'
            else:
                return 'move computer'
        elif (pos[0]+2*d_v[direction][0],pos[1]+2*d_v[direction][1]) in game[2]:
            return 'move computer' 

        else:
            return 'no move' 
    else:
        return 'target'

def bad_cell(game, pos): 
    total = 0
    for neighbor in neighbors(game, pos):
        if neighbor in game[3]:
            total+=1
    if total>=2:
        return True
    return False
    
def neighbors(game, pos):
    return [(pos[0]-1,pos[1]),
    (pos[0]+1,pos[1]),
    (pos[0], pos[1]+1),
    (pos[0], pos[1]-1)
    ]   
    


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
    return game[1] == game[2]


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    game_new = game.copy()
    wya = player_pos(game_new)
    decision = check_cell(game_new, wya, direction)
    print(decision)
    if decision == 'empty' or decision == 'target':
        game_new[0]=(wya[0]+d_v[direction][0], wya[1]+d_v[direction][1])
              
    elif decision == 'move computer':
        game_new[0]=(wya[0]+d_v[direction][0], wya[1]+d_v[direction][1])
        game_new[1].remove((wya[0]+d_v[direction][0], wya[1]+d_v[direction][1]))
        game_new[1].add((wya[0]+2*d_v[direction][0], wya[1]+2*d_v[direction][1]))
  
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
    out = [[[] for _ in range(game[5][1])] for _ in range(game[5][0])]
    string_list = ['player', 'computer', 'target', 'wall']
    for i in range(game[5][0]):
        for j in range(game[5][1]):
            for k in range(1,4):
                if (i,j) in game[k]:
                    out[i][j].append(string_list[k])
            if (i,j) == game[0]:
                out[i][j].append('player')
    return out

'''def simplify(game):
    computer_list = []
    
    for i in range(len(game)):
        for j in range(len(game[i])):
            if 'computer' in game[i][j]:
                computer_list.append((i,j))
    return (player_pos(game)+tuple(computer_list))'''

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
    
    while agenda:
        current_game = agenda.pop(0)
        simplified_current = simplify(current_game)
        possible_moves = valid_moves(current_game, player_pos(current_game))
        for move in (possible_moves):
            new_game = step_game(current_game, move)

            simplified_new = simplify(new_game)
            if simplified_new not in visited:
                agenda.append(new_game)
                visited[simplified_new] = (simplified_current, move)
                
                if victory_check(new_game):
                    list_moves = []
                    while visited[simplified_new] != None:
                        list_moves.append(visited[simplified_new][1])
                        
                        simplified_new = visited[simplified_new][0]
                    return list_moves[::-1]
    


    

if __name__ == "__main__":
    '''solve_puzzle([
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
])'''
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

    my_game = new_game(test_case)
    print(my_game)
    print(dump_game(my_game))
    step_game(my_game, 'left')
    print(dump_game(my_game))
    
