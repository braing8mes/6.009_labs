"""6.009 Lab 10: Snek Is You Video Game"""

import doctest


# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
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

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    out = {"board": level_description}
    dimensions = (len(level_description), len(level_description[0]))
    out["dimensions"] = dimensions
    for word in ["AND", "IS"]:
        positions = get_pos(level_description, word)
        out[word] = positions

    return out

def get_pos(raw_repr, object):
    '''
    get the coordinates of a certain type of object
    returned as a set of tuples
    '''

    object_set = set()
    for i in range(len(raw_repr)):
        for j in range(len(raw_repr[i])):
            if object in raw_repr[i][j]:
                object_set.add((i,j))
    return object_set

def next_pos(pos, direction, n = 1):
    '''
    returns row and column of cell n steps adjacent to 
    the parameter cell in the direction called.
    '''
    return (pos[0]+n*d_v[direction][0], pos[1]+n*d_v[direction][1])

def check_inbound(game, pos):
    height, width = game["dimensions"][0], game["dimensions"][1]
    return (0 <= pos[0] < height) and (0 <= pos[1] < width)


def get_rules(game):
    rules = {"SAME": []}
    for word in PROPERTIES:
        rules[word] = []
    rules['PUSH'] = list(WORDS)

    # update the rules dictionary based on our input lists
    board = game["board"]
    def rule_helper(left, right):
        for i in left:
            i = i.lower()
            for j in right:
                if j in PROPERTIES:
                    rules[j].append(i)
                else:
                    j = j.lower()
                    rules["SAME"].append((i,j))

    for loc in game["IS"]:
        i, j = loc[0], loc[1]
        horizontal_left, horizontal_right = [], []
        count = 1
        while check_inbound(game, (i, j-count)):
            potential_loc = next_pos(loc, "left", count)
            new_i, new_j = potential_loc[0], potential_loc[1]
            stuff = [word for word in board[new_i][new_j] if word in NOUNS]
            if stuff == []:
                break
            horizontal_left.extend(stuff)
            if j-count-2 < 0 or "AND" not in board[i][j-count-1]:
                break
            count += 2
        count = 1
        while check_inbound(game, (i, j+count)):
            potential_loc = next_pos(loc, "right", count)
            new_i, new_j = potential_loc[0], potential_loc[1]
            stuff = [word for word in board[new_i][new_j] if word in NOUNS or PROPERTIES]
            if stuff == []:
                break
            horizontal_right.extend(stuff)
            if j+count+2 >= len(board[0]) or "AND" not in board[i][j+count+1]:
                break
            count += 2
        rule_helper(horizontal_left, horizontal_right)
    
    for loc in game["IS"]:
        i, j = loc[0], loc[1]
        vertical_left, vertical_right = [], []
        count = 1
        while check_inbound(game, (i-count, j)):
            potential_loc = next_pos(loc, "up", count)
            new_i, new_j = potential_loc[0], potential_loc[1]
            stuff = [word for word in board[new_i][new_j] if word in NOUNS]
            if stuff == []:
                break
            vertical_left.extend(stuff)
            if i-count-2 < 0 or "AND" not in board[i-count-1][j]:
                break
            count += 2
        count = 1
        while check_inbound(game, (i+count, j)):
            potential_loc = next_pos(loc, "down", count)
            new_i, new_j = potential_loc[0], potential_loc[1]
            stuff = [word for word in board[new_i][new_j] if word in NOUNS or PROPERTIES]
            if stuff == []:
                break
            vertical_right.extend(stuff)
            if i+count+2 >= len(board) or "AND" not in board[i+count+1][j]:
                break
            count += 2
        rule_helper(vertical_left, vertical_right)
    rules['STOP'] = [word for word in rules['STOP'] if word not in rules['PUSH'] and word not in rules['YOU']]
    return rules
  
def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """

    rules = get_rules(game)
    """def move(obj, pos):
        new_pos = next_pos(pos, direction)
        if check_inbound(game, new_pos):
            pushed = [word for word in board[new_pos[0], new_pos[1]] if word in rules["PUSH"]]
            var = True
            for object in pushed:
                var = move(object, new_pos)"""
            
    board = game['board']
    h, v = d_v[direction]

    # move returns True if we can move the thing at (r, c)
    def move(thing, r, c):
        nr, nc = r+h, c+v
        if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and not any(x in rules['STOP'] for x in board[nr][nc]):
            t = [i for i in board[nr][nc] if i in rules['PUSH']]

            # check if we can push
            can_push = True
            for i in t:
                can_push = move(i, nr, nc)

            # move thing
            if can_push:
                # edited the moved object string so that we don't move it multiple times
                board[nr][nc] += [thing+'*'] * board[r][c].count(thing)
                board[r][c] = [i for i in board[r][c] if i != thing]

                # handling the pulling cases
                # yank :D
                pr, pc = r-h, c-v
                if 0 <= pr < len(board) and 0 <= pc < len(board[0]):
                    t = [i for i in board[pr][pc] if i in rules['PULL']]
                    for i in t:
                        move(i, pr, pc)
                return True
        return False


    # go thruogh the board and move each 'YOU' object
    for i in range(len(board)):
        for j in range(len(board[i])):
            for k in board[i][j]:
                if k in rules['YOU']:
                    move(k, i, j)

    # change our edited string back
    for i in board:
        for j in i:
            for k in range(len(j)):
                if j[k][-1] == '*':
                    j[k] = j[k][:-1]

    game['board'] = board
    rules = get_rules(game)
    
    # update the board if there is any NOUN is NOUN rule
    for i in board:
        for j in i:
            for k in range(len(j)):
                for r in rules['SAME']:
                    if j[k] == r[0]:
                        j[k] = r[1]
                        break
    game['board'] = board        
    rules = get_rules(game)
    # check win and update defeat
    win = False
    for i in board:
        for j in range(len(i)):
            if any(x in rules['DEFEAT'] for x in i[j]):
                i[j] = [x for x in i[j] if x not in rules['YOU']]
            if any(x in rules['WIN'] for x in i[j]) and any(y in rules['YOU'] for y in i[j]):
                win = True
    game['board'] = board  
 
    return win


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game["board"]

if __name__ == "__main__":
    my_game = new_game([
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
        [['FLAG'], ['IS'], ['BUG']]
    ])
    print(my_game)
    print(get_rules(my_game))