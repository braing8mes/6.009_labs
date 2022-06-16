import random
win = 0
lose = 0
for i in range(100000):
    sequence = []
    while True:
        new = random.randint(0,1)
        sequence.append(new)
        if sequence[-4:] == [0, 0, 0, 0]:
            win+=1
            break;
        elif sequence[-2:] == [1,1]:
            lose+=1
            break;
print(win)
print(lose)