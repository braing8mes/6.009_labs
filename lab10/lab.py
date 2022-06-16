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
        [[], ["snek"], []],
        [["SNEK"], ["IS"], ["YOU"]],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    return level_description

def next_pos(row, col, direction, rev = False): # return the position of the cell in a direction or its reverse
    return (row+d_v[direction][0], col+d_v[direction][1]) if rev == False else (row-d_v[direction][0], col-d_v[direction][1])

def get_rules(game):
    """
    Compute the rules in the current game state.
    Handles both NOUN is PREDICATE and NOUN is NOUN.
    Handles AND conjunctive.
    
    Returns a dictionary of rules, with predicates as keys
    and a special "SAME" to handle NOUN is NOUN cases.
    """
    rules = {"SAME": []}
    for word in PROPERTIES:
        rules[word] = []
    rules["PUSH"] = list(WORDS)

    def rule_helper(left, right): # helper function to add rules to the dictionary
        for i in left:
            i = i.lower()
            for j in right:
                if j in PROPERTIES:
                    rules[j].append(i)
                else:
                    j = j.lower()
                    rules["SAME"].append((i,j))

    for i in range(len(game)):
        for j in range(len(game[i])):
            if "IS" in game[i][j]:
                # compute horizontal rules
                hor_left = []
                count = 1
                while j-count >= 0:
                    stuff = [word for word in game[i][j-count] if word in NOUNS]
                    if stuff == []:
                        break
                    hor_left.extend(stuff)
                    if j-count-2 < 0 or "AND" not in game[i][j-count-1]: 
                        break
                    count += 2
                hor_right = []
                count = 1
                while j+count < len(game[i]):
                    stuff = [word for word in game[i][j+count] if word in NOUNS or word in PROPERTIES]
                    if not stuff: 
                        break
                    hor_right.extend(stuff)
                    if j+count+2 >= len(game[i]) or "AND" not in game[i][j+count+1]: 
                        break
                    count += 2
                rule_helper(hor_left, hor_right)

                # compute vertical rules
                ver_up = []
                count = 1
                while i-count >= 0:
                    stuff = [word for word in game[i-count][j] if word in NOUNS]
                    if not stuff: break
                    ver_up.extend(stuff)
                    if i-count-2 < 0 or "AND" not in game[i-count-1][j]: break
                    count += 2
                ver_down = []
                count = 1
                while i+count < len(game):
                    stuff = [word for word in game[i+count][j] if word in NOUNS or word in PROPERTIES]
                    if not stuff: break
                    ver_down += stuff
                    if i+count+2 >= len(game) or "AND" not in game[i+count+1][j]: break
                    count += 2
                rule_helper(ver_up, ver_down)

    rules["STOP"] = [word for word in rules["STOP"] if word not in rules["PUSH"] and word not in rules["YOU"]]
    # only stop if the word is not pushable or movable
    return rules


def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user"s
    input is given by direction, which is one of the following:
    {"up", "down", "left", "right"}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    rules = get_rules(game)

    def move(thing, r, c):
        """
        helper function to determine if object can be interacted with
        handles push and pull
        """
        new_r, new_c = next_pos(r, c, direction)[0], next_pos(r, c, direction)[1] 
        if 0 <= new_r < len(game) and 0 <= new_c < len(game[0]) and not any(word in rules["STOP"] for word in game[new_r][new_c]):
            stuff = [i for i in game[new_r][new_c] if i in rules["PUSH"]]

            pushable = True
            for obj in stuff:
                pushable = move(obj, new_r, new_c)

            if pushable: # move object
                # make sure object is moved correctly
                game[new_r][new_c] += [thing+"@"] * game[r][c].count(thing)
                game[r][c] = [i for i in game[r][c] if i != thing]

                # if the object is pulled instead 
                pull_r, pull_c = next_pos(r, c, direction, True)[0], next_pos(r, c, direction, True)[-1]
                if 0 <= pull_r < len(game) and 0 <= pull_c < len(game[0]):
                    stuff = [i for i in game[pull_r][pull_c] if i in rules["PULL"]]
                    for i in stuff:
                        move(i, pull_r, pull_c)
                return True
        return False

    # parse the board and try to move all the objects with "PUSH"
    for i in range(len(game)):
        for j in range(len(game[i])):
            for obj in game[i][j]:
                if obj in rules["YOU"]:
                    move(obj, i, j)

    # remove our @ so the representation can be analyzed by tester
    for i in game:
        for j in i:
            for word in range(len(j)):
                if j[word][-1] == "@":
                    j[word] = j[word][:-1]


    rules = get_rules(game)

    # parse for NOUN is NOUN and replace objects
    for i in game:
        for j in i:
            for k in range(len(j)):
                for r in rules["SAME"]:
                    if j[k] == r[0]:
                        j[k] = r[1]
                        break
    
    rules = get_rules(game)
    
    # parse and handle defeat
    win = False
    for i in game:
        for j in range(len(i)):
            if any(word in rules["DEFEAT"] for word in i[j]):
                i[j] = [word for word in i[j] if word not in rules["YOU"]]
            if any(word in rules["WIN"] for word in i[j]) and any(obj in rules["YOU"] for obj in i[j]):
                # then we win
                win = True
    
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
    return game

