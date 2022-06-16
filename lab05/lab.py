#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    assignments = {}
    problem = convert_formula(formula)
    while True:
        problem, var, lit = sad_single(problem)
        if var != None:
            assignments[var] = lit
        else:
            break
    
    if not problem: # if list is empty then we are done
        return assignments

    if not all(problem): # if list has empty clauses then there must be a contradiction 
                         # update() will remove tuples from the clause but the clause
                         # itself will never be removed. 
        return None
        
    recursion_v, recursion_l = get_tuple(problem[0])
    for assignment in [recursion_l, not recursion_l]:
        answer = satisfying_assignment(update(problem, recursion_v, assignment))
        if answer != None:
            assignments[recursion_v] = assignment
            assignments.update(answer)
            return assignments
    return None

def get_tuple(clause):
    """
    Get a tuple from a clause (represented as a set)
    """
    for var in clause:
        return var

def sad_single(set_formula):
    """
    Scans through formula to find a clause with a single variable. 
    This can easily be updated to reduce the complexity of the formula.
    Returns reduced formula and variable assignments
    """

    for clause in (set_formula):
        if len(clause) == 1:
            var, lit = list(clause)[0] #note to self - can't use pop because it mutates clause
            return update(set_formula, var, lit), var, lit
    return set_formula, None, None
                
def convert_formula(formula):
    """
    Convert base formula representation so clauses are sets. This makes runtime faster because
    we are constantly checking if tuples are in clauses as well as removing tuples from clauses.

    >>> convert_formula([[('a', True), ('b', False), ('c', True)]])
    [{('c', True), ('b', False), ('a', True)}]
    """

    return [ set(clause) for clause in formula]

def update(set_formula, variable, literal):
    """
    Reduce the SAT problem by updating the formula assuming a literal is assigned a given value
    All clauses with (literal, value) are satisfied and thus deleted.
    All clauses with (literal, not value) have that tuple deleted. 
    """

    out = []
    for clause in (set_formula):
        if (variable, literal) not in clause:
            out.append(clause - {(variable, not literal)})
    return out

def rule_1(s_p, r_c): 
    out = []
    for student in (s_p):
        clause = [(student+'_'+room, True) for room in s_p[student]]
        out.append(clause)
    return out

def rule_2(s_p, r_c): 
    out = []
    for student in (s_p):
        if len(s_p[student]) > 1:
            pairs = [[(student+'_'+room, False), (student+'_'+room2, False)] for i, room in  enumerate(s_p[student]) for room2 in s_p[student][i+1:]]
            out.extend(pairs)
    return out

def get_all_combos(s_p, r_c):
    students = list(s_p)
    out = []
    def get_combos(student_combo, students, room, cap, i):
        if len(student_combo) - 1 == cap:   
                
            out.append(list(set([(student+'_'+room, False) for student in student_combo])))
            
        if i < len(students):
            get_combos(student_combo, students, room, cap, i+1)
            get_combos(student_combo+[students[i]], students, room, cap, i+1)
    for room in (r_c):
        cap = r_c[room]
        get_combos([], students, room, cap, 0)    
    return out

def rule_3(s_p, r_c): 
    return get_all_combos(s_p, r_c)

def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    out = []
    for rule in rule_1, rule_2, rule_3:
        out.extend(rule(student_preferences, room_capacities))
    
    return out

if __name__ == '__main__':
    import doctest
    #_doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags)
    print(boolify_scheduling_problem({'Alice': ['basement', 'penthouse'],
                            'Bob': ['kitchen'],
                            'Charles': ['basement', 'kitchen'],
                            'Dana': ['kitchen', 'penthouse', 'basement']},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4}))