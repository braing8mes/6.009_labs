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
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    buffer = source.replace('(', ' ( ').replace(')', ' ) ').replace('\n', ' \n ')
    buffer = buffer.split('\n')
    out = []
    for each in buffer:
        if '#' in each:
            print(each)
            out.extend(each.split('#')[0].split())
        else:
            out.extend(each.split())
    return out
    
def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
    """
    counter = 0
    for token in tokens:
        if token == '(':
            counter += 1
        if token == ')':
            counter -= 1
        if counter < 0:
            raise CarlaeSyntaxError
    if counter != 0:
        raise CarlaeSyntaxError
    def parse_expression(i):
        token = tokens[i]
        if token == '(':
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

def mul(args):
    out = 1
    for arg in args:
        out *= arg
    return out

def div(args):
    out = args[0]
    for arg in args[1:]:
        out /= arg
    return out

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul,
    "/": div
}

##############
# Evaluation #
##############

class Environment:
    def __init__(self, parent):
        self.parent = parent
        self.bindings = {}
    """def __getitem__(self, key):
        try:
            return self.bindings[key]
        except KeyError:
            if self.parent:
                return self.parent[key]
            else:
                raise CarlaeNameError
    def __setitem__(self, key, val):
        self.bindings[key] = val
    def __contains__(self, var):
        return var in self.bindings"""

class Function:
    def __init__(self, params, expr, env):
        self.params = params
        self.expr = expr
        self.env = env
    """def __call__(self, my_params):
        if len(my_params) != len(self.params):
            raise CarlaeEvaluationError
        my_env = Environment(self.env)
        for i in range(len(self.params)):
            my_env[self.params[i]] = my_params[i]
        return evaluate(self.expr, my_env)"""

builtins = Environment(None) 
builtins.bindings = carlae_builtins

def evaluate(tree, env = None):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    if env is None:
        env = Environment(builtins)
    if type(tree) in [int, float]:
        return tree
    elif type(tree) == list:
        if tree[0] == ":=":
            if type(tree[1]) == list:
                val = Function(tree[1][1:], tree[2], env)
                env.bindings[tree[1][0]] = val
            else:
                var = tree[1]
                val = evaluate(tree[2], env)
                env.bindings[var] = val
            return val

        elif tree[0] == "function":
            return Function(tree[1], tree[2], env)
        else:
            function = evaluate(tree[0], env)
            if not callable(function) and type(function) != Function:
                raise CarlaeEvaluationError
            func_params = [evaluate(tree[i], env) for i in range(1, len(tree))]
            if type(function) == Function:
                env = Environment(function.env)
                if len(function.params) != len(func_params):
                    raise CarlaeEvaluationError
                for i in range(len(func_params)):
                    env.bindings[function.params[i]] = func_params[i]
                return evaluate(function.expr, env)
            else:
                return function(func_params)
    else:
        while env != None:
            if tree in env.bindings:
                return env.bindings[tree]
            env = env.parent
        raise CarlaeNameError(str(tree), " error")
def result_and_env(tree, env = None):
    if not env:
        env = Environment(builtins)
    out = evaluate(tree, env)
    return out, env

def REPL():
    while True: 
        my_input = input("Input: ")
        if my_input.lower() == "quit":
            break
        try: 
            print("out: ", evaluate(parse(tokenize(my_input))))
        except Exception as e:
            print(e)

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    #REPL()
    #print(parse(['(', '+', '2', '(', '-', '5', '3', ')', '7', '8', ')']))
    print(builtins.bindings)