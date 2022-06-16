from re import A


a= (1,2)
x,y = a

def all_combinations_helper(source, N):
    if N == 0:
        yield frozenset()
        return
    for c in all_combinations(source, N-1):
        for s in source:
            if s not in c:
                yield c | frozenset([s])
def all_combinations(source, N):
    return set(all_combinations_helper(source, N))


def rule_2(prefs, caps):
    room_pairs = all_combinations(caps, 2)
    return [[('%s_%s' % (s, r), False) for r in p]
            for s in prefs for p in room_pairs]



def rule_3(prefs, caps):
    out = []
    for room, cap in caps.items():
        if cap >= len(prefs):
            continue
        student_combinations = all_combinations(prefs, cap+1)
        for group in student_combinations:
            out.append([('%s_%s' % (s, room), False) for s in group])
    return out

print(rule_3({'Alice': ['basement', 'penthouse'],
                            'Bob': ['kitchen'],
                            'Charles': ['basement', 'kitchen'],
                            'Dana': ['kitchen', 'penthouse', 'basement']},
                           {'basement': 1,
                            'kitchen': 2,
                            'penthouse': 4}))