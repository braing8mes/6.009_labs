"""6.009 Lab 9: Carlae Interpreter Part 2"""
import sys

sys.setrecursionlimit(10_000)

#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest
from turtle import right

# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Copied from lab 8

    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    buffer = source.replace('(', ' ( ').replace(')', ' ) ').replace('\n', ' \n ')
    buffer = buffer.split('\n')
    out = []
    for each in buffer: # remove comments
        if '#' in each:
            print(each)
            out.extend(each.split('#')[0].split())
        else:
            out.extend(each.split())
    return out
    
def parse(tokens):
    """
    Copied from lab 8

    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    counter = 0
    for token in tokens: # check if parentheses are closed properly
        if token == '(':
            counter += 1
        if token == ')':
            counter -= 1
        if counter < 0:
            raise CarlaeSyntaxError
    if counter != 0:
        raise CarlaeSyntaxError

    def parse_expression(i): # similar to lab 7
        token = tokens[i]
        if token == '(': # append content between parentheses in a list
            out = []
            new_i = i + 1
            while new_i < len(tokens) and tokens[new_i] != ')':
                symbol, new_i = parse_expression(new_i)
                out.append(symbol)
            if new_i >= len(tokens):
                raise CarlaeSyntaxError
            return out, new_i + 1

        else:
            return number_or_symbol(token), i+1
       
    parsed_expression, final_i = parse_expression(0)

    if final_i != len(tokens):
        raise CarlaeSyntaxError
    
    return parsed_expression


######################
# Built-in Functions #
######################

def mul(args): # method for *
    out = 1
    for arg in args:
        out *= arg
    return out

def div(args): # method for /
    out = args[0]
    for arg in args[1:]:
        out /= arg
    return out

def head(args): # return the head of a pair
    if len(args) == 1:
        if isinstance(args[0], Pair):
            return args[0].head
    raise CarlaeEvaluationError

def tail(args): # return the tail of a pair
    if len(args) == 1:
        if isinstance(args[0], Pair):
            return args[0].tail
    raise CarlaeEvaluationError

def build_pair(args): # construct and return a pair
    if len(args) == 2:
        return Pair(args[0], args[1])
    raise CarlaeEvaluationError("build pair error")

def pair_list(args): # construct a linked list of nested pairs
    if not args:
        return ""
    return Pair(args[0], pair_list(args[1:]))

def is_list(args): # return whether input is a list or not
    if args[0] == "":
        return True
    if isinstance(args[0], Pair) and isinstance(args[0].tail, Pair):
        return is_list([args[0].tail])
    elif isinstance(args[0], Pair) and args[0].tail == "":
        return True
    else:
        return False

def length(args): # return length of list
    current = args[0]
    if not is_list(args):
        raise CarlaeEvaluationError("length error")
    if current == "":
        return 0
    else:
        return current.length()

def nth(args): # return the nth element in a list
    try: 
        my_list, i = args[0], args[1]
        return my_list.index(i)
    except:
        raise CarlaeEvaluationError("nth error")
        

def concat(args): # concatenate multiple lists into one big list
    out = ""

    for each in args[::-1]: # loop through the lists
        if not is_list([each]):
            raise CarlaeEvaluationError("concat error")
        i = length([each]) - 1
        while i >= 0:
            out = Pair(nth([each, i]), out) # create list (nested pair structure)
            i -= 1
    return out

def map(args): # call and apply a function on all elements in a list
    func, my_list = args[0], args[1]
    if my_list == "":
        return ""
    out = Pair(func([my_list.head]), "")
    current = out
    while my_list.tail != "": # apply until we reach the end of the list
        my_list = my_list.tail
        current.tail = Pair(func([my_list.head]), "")
        current = current.tail
    return out

def filter(args): # return filtered list, similar to map but uses more conditional statements
    func, my_list = args[0], args[1]
    out = ""
    if len(args) != 2 or not is_list([my_list]):
        raise CarlaeEvaluationError
    i = length([my_list]) - 1
    while i >= 0:
        val = nth([my_list, i])
        if func([val]):
            out = Pair(val, out)
        i -= 1
    return out

def reduce(args): # reduce a list to a value given a function and starting value
    func, my_list, initval = args[0], args[1], args[2]
    if len(args) != 3 or not is_list([my_list]):
        raise CarlaeEvaluationError
    out = initval
    for i in range(length([my_list])):
        out = func([out, nth([my_list, i])])
    return out

def begin(args): # return last element
    return args[-1]


carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div,
    "=?": lambda args: all(args[i] == args[i+1] for i in range(len(args)-1)),
    "<": lambda args: all(args[i] < args[i+1] for i in range(len(args)-1)),
    "<=": lambda args: all(args[i] <= args[i+1] for i in range(len(args)-1)),
    ">": lambda args: all(args[i] > args[i+1] for i in range(len(args)-1)),
    ">=": lambda args: all(args[i] >= args[i+1] for i in range(len(args)-1)),
    "@t": True,
    "@f": False,
    "not": lambda arg: not arg[0],
    "head": head,
    "tail": tail,
    "nil": "",
    "pair": build_pair,
    "list": pair_list,
    "list?": is_list,
    "length": length,
    "nth": nth,
    "concat": concat,
    "map": map,
    "filter": filter,
    "reduce": reduce, 
    "begin": begin,
    }




##############
# Evaluation #
##############

class Environment:
    def __init__(self, parent): 
        self.parent = parent # parent environment
        self.bindings = {} # variable bindings

    def __getitem__(self, key): # dunder method
        try:
            return self.bindings[key]
        except KeyError: # recursively look in parent environment
            if self.parent:
                return self.parent[key]
            else:
                raise CarlaeNameError

    def __setitem__(self, key, val): # dunder method
        self.bindings[key] = val

    def __contains__(self, var): # dunder method
        return var in self.bindings

    def remove(self, key): # remove a binding
        if not key in self.bindings: 
            raise CarlaeNameError("remove")
        temp = self.bindings[key]
        del self.bindings[key]
        return temp

    def sheesh(self, key, val): # set bang function, set value of EXISTING variable
        if key in self.bindings:
            self.bindings[key] = val
            return val
        else:
            if self.parent:
                return self.parent.sheesh(key, val)
            raise CarlaeNameError


class Function:
    def __init__(self, params, expr, env):
        self.params = params
        self.expr = expr
        self.env = env

    def __call__(self, my_params): # dunder method for calling a function
        if len(my_params) != len(self.params):
            raise CarlaeEvaluationError("function call")
        my_env = Environment(self.env)
        for i in range(len(self.params)):
            my_env[self.params[i]] = my_params[i]
        return evaluate(self.expr, my_env)

class Pair:
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def length(self): # helper function for length()
        count = 1
        while self.tail != "":
            count += 1
            self = self.tail
        return count

    def index(self, i): # helper function for nth()
        j = 0
        while j != i:
            self = self.tail
            j += 1
        return self.head
    
    def __str__(self): # for debugging purposes
        out = []
        for i in range(self.length()):
            out.append(self.head)
            self = self.tail
        return str(out)

builtins = Environment(None) # initialize global environment
builtins.bindings = carlae_builtins

def boolean_combinators(comb, args, env = None):
    """
    Helper function that handles and, or, and not statements 
    passed into evaluate.

    Returns True if keyword is used, False if not, and error
    if there is a syntax or evaluation error
    
    """
    if comb == "and":
        for i in args:
            if not evaluate(i, env):
                return False
        return True
    elif comb == "or":
        for i in args:
            if evaluate(i, env):
                return True
        return False
    elif comb == "not":
        if len(args) > 1:
            raise CarlaeEvaluationError
        try:
            return not evaluate(args[0], env)
        except:
            raise CarlaeEvaluationError
    else:
        raise CarlaeEvaluationError

def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if not env: # if not specified, initialize environment with parent builtins
        env = Environment(builtins)

    if type(tree) in [int, float]:
        return tree

    elif type(tree) == list:
        # variable/shortened function definition 
        if not tree:
            raise CarlaeEvaluationError

        if tree[0] == ":=":
            if type(tree[1]) == list:
                val = Function(tree[1][1:], tree[2], env)
                env[tree[1][0]] = val
            else:
                val = evaluate(tree[2], env)
                env[tree[1]] = val
            return val

        # function definition
        elif tree[0] == "function": 
            return Function(tree[1], tree[2], env) # (params, expr, env)

        #conditionals
        elif tree[0] == "if":
            if evaluate(tree[1], env):
                return evaluate(tree[2], env)
            return evaluate(tree[3], env)

        #special keywords

        elif tree[0] in ["and", "or", "not"] and tree[0] not in env:
            return boolean_combinators(tree[0], tree[1:], env)

        elif tree[0] == "del" and tree[0] not in env:
            return env.remove(tree[1])

        elif tree[0] == 'let':
            temp_env = Environment(env)
            for var in tree[1]:
                temp_env[var[0]] = evaluate(var[1], env)
            return evaluate(tree[2], temp_env)

        elif tree[0] == "set!":
            return env.sheesh(tree[1], evaluate(tree[2], env))

        else: # calling functions
            function = evaluate(tree[0], env)
            func_params = [evaluate(tree[i], env) for i in range(1, len(tree))]
            if type(function) != Function:
                try:
                    return function(func_params)
                except:
                    raise CarlaeEvaluationError
            
            elif type(function) == Function:
                env = Environment(function.env) # evaluate in a new environment
                if len(function.params) != len(func_params):
                    raise CarlaeEvaluationError
                for i in range(len(func_params)): # bind params to the environment
                    env[function.params[i]] = func_params[i]
                return evaluate(function.expr, env)        
            else:
               raise CarlaeEvaluationError
                    
    else: # return function object
        if type(tree) == str:
            return env[tree]
        return tree

def result_and_env(tree, env = None):
    """
    Returns both the output generated
    by evaluate and the environment
    in which it was evaluated.
    """
    if not env:
        env = Environment(builtins)
    out = evaluate(tree, env)
    return out, env

def evaluate_file(file_name):
    """
    Run evaluate on a text file and return the result
    """
    file = open(file_name)
    f = file.read()
    file.close()
    return evaluate(parse(tokenize(f)))
    
def REPL():
    """
    Accepts input from user, tokenizes,
    parses, evaluates, and returns the output
    to the user.
    """
    while True: 
        my_input = input("Input: ")
        if my_input.lower() == "quit":
            break
        try: 
            print("out: ", evaluate(parse(tokenize(my_input))))
        except Exception as e:
            print(e)
            print(type(e))

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    #REPL()
    #a = Pair(1, Pair(2, Pair(3, "")))
    #print(a)
    
    if len(sys.argv) > 1:
        for file_name in sys.argv[1:]:
            evaluate_file(file_name, builtins)