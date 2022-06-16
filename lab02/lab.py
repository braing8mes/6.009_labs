# 6.009 Lab 2: Snekoban

from ast import dump
import json
from operator import ne
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

def get_pos(raw_repr, object):
    '''
    get the coordinates of a certain type of object (wall, computer, etc.) 
    returned as a set of tuples
    '''

    object_set = set()
    for i in range(len(raw_repr)):
        for j in range(len(raw_repr[i])):
            if object in raw_repr[i][j]:
                object_set.add((i,j))
    return object_set

def new_game(level_description):
    """
    Returns a dictionary containing sets and tuples with the information from level description. 
    Sets for each object contain location coordinates as tuples.
    Dimension and player are stored as tuples
    """

    dimensions = (len(level_description), len(level_description[0]))
    targets = get_pos(level_description, 'target')
    computers = get_pos(level_description, 'computer')
    walls = get_pos(level_description, 'wall')
    player = tuple()
    for i in range(dimensions[0]):
        for j in range(dimensions[1]):
            if 'player' in level_description[i][j]:
                player = (i,j)

    return {'dimensions': dimensions,
    'targets': targets,
    'computers': computers,
    'walls': walls,
    'player': player,
    }

def player_pos(game):
    '''
    returns row and column of player in a tuple
    '''
    return game['player']

def next_pos(pos, direction):
    '''
    returns row and column of cell adjacent to the parameter cell in the direction called
    '''
    return (pos[0]+d_v[direction][0], pos[1]+d_v[direction][1])
    
def check_cell(game, pos, direction): 
    '''
    Given a game state and possible direction for a move, 
    return information about the move that will be used in subsequent functions
    '''
    cell = next_pos(pos, direction)
    if cell in game['walls']:
        return 'no_move'
    elif cell in game['computers']:
        second_cell = next_pos(cell, direction)
        if second_cell in game['walls'] or second_cell in game['computers']:
            return 'no move'
        #elif bad_cell(game, second_cell) and second_cell not in game['targets']:
         #   return 'no move'
        else:
            return 'move computer'
    else:
        return 'move player'

'''def bad_cell(game, pos): 
    total = 0
    for neighbor in neighbors(pos):
        if neighbor in game['walls']:
            total+=1
    if total>=2:
        return True
    return False'''
    
def neighbors(pos):
    '''
    get neighbor positions to a cell
    '''
    return [(pos[0]-1,pos[1]),
    (pos[0]+1,pos[1]),
    (pos[0], pos[1]+1),
    (pos[0], pos[1]-1)
    ]   

def valid_moves(game, pos):
    '''
    get the valid moves from a game state and position, hopefully speeding up our bfs
    '''
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
    if len(game['computers']) == 0:
        return False
    return game['computers'] == game['targets']


def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    game_new = {'dimensions': game['dimensions']+tuple(),
    'targets': game['targets'].copy(),
    'computers': game['computers'].copy(),
    'walls': game['walls'].copy(),
    'player': game['player']+tuple(),
    }
    wya = player_pos(game_new)
    decision = check_cell(game_new, wya, direction)
    
    cell = next_pos(wya, direction)
    if decision == 'empty' or decision == 'move player':
        game_new['player']=cell
              
    elif decision == 'move computer':
        game_new['player']=cell
        second_cell = next_pos(cell, direction)
        game_new['computers'].remove(cell)
        game_new['computers'].add(second_cell)
  
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
    out = [[[] for _ in range(game['dimensions'][1])] for _ in range(game['dimensions'][0])]
    string_list = ['computers', 'targets', 'walls']
    out[game['player'][0]][game['player'][1]].append('player')
    
    for key in (string_list):
        for coord in (game[key]):
            
            out[coord[0]][coord[1]].append(key[:-1])
    
    return out
def simplify(game):
    '''
    simplified information storage of the game that can be stored in the visited set during bfs. 
    Since the player and computers are the only objects that change location,
    we only need to store their locations.
    '''
    return (game['player'] + tuple(game['computers']))

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
        new_agenda = []
        for current_game in (agenda):
            simplified_current = simplify(current_game)
            possible_moves = valid_moves(current_game, player_pos(current_game))
            for move in (possible_moves):
                new_game = step_game(current_game, move)

                simplified_new = simplify(new_game)
                if simplified_new not in visited:
                    new_agenda.append(new_game)
                    visited[simplified_new] = (simplified_current, move)
                    
                    if victory_check(new_game):
                        list_moves = []
                        while visited[simplified_new] != None:
                            list_moves.append(visited[simplified_new][1])
                            
                            simplified_new = visited[simplified_new][0]
                        return list_moves[::-1]
        agenda = new_agenda
    


    

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


    
