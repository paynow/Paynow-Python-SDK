items = [['a',1.03],['b',2],['b',2],['b',2],['b',2]]

print(float(sum([items[index][1] for index in range(len(items))])))