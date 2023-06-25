import subprocess
import re
import random
import threading
import json


def fitness_function(new_HS):
    with open('HS.json', 'w') as file:
        json.dump(new_HS, file)
    result = subprocess.run(['python', 'main.py'], stdout=subprocess.PIPE)
    out_result = result.stdout.decode('utf-8')
    find_blue = re.compile(r'Blue -> -?\d+')
    find_yellow = re.compile(r'Yellow -> -?\d+')
    find_number = re.compile(r'-?\d+')
    blue_point = find_blue.findall(out_result)[0]
    yellow_point = find_yellow.findall(out_result)[0]
    population.append(new_HS, int(find_number.findall(yellow_point)[0]) - int(find_number.findall(blue_point)[0]))


def mean_crossover(parent1, parent2):
    alpha = random.random()
    value_per_health = alpha * parent1['value per health'] + (1 - alpha) * parent2['value per health']
    child = {'value per health': value_per_health}
    return child


def mutation(child, mutation_coefficient):
    mutate_sign = random.choices([1, -1])
    child['value per health'] += mutation_coefficient * mutate_sign
    return child


population = []

agent1 = {'value per health': 25}
agent2 = {'value per health': 10}
agent3 = {'value per health': 12}
agent4 = {'value per health': 15}
agent5 = {'value per health': 13}
agent6 = {'value per health': 14}

threads = [threading.Thread(target=fitness_function, args=(agent1,)),
           threading.Thread(target=fitness_function, args=(agent2,)),
           threading.Thread(target=fitness_function, args=(agent3,)),
           threading.Thread(target=fitness_function, args=(agent4,)),
           threading.Thread(target=fitness_function, args=(agent5,)),
           threading.Thread(target=fitness_function, args=(agent6,))]
for thread in threads:
    input('input gamecfg\n')
    thread.start()
    input('confirm\n')
for thread in threads:
    thread.join()

num_generations = 5

crossover_type = mean_crossover
crossover_possibility = 0.9

mutation_possibility = 0.1
mutation_coefficient = 5

for _ in range(num_generations):
    children = []
    for i in range(3):
        if random.random() < crossover_possibility:
            parent1, parent2 = random.choices([p[0] for p in population], weights=[p[1] for p in population], k=2)
            child = mean_crossover(parent1, parent2)
            if random.random() < mutation_possibility:
                child = mutation(child, mutation_coefficient)
            children.append(child)
        else:
            i -= 1

    threads = [threading.Thread(target=fitness_function, args=(children[0],)),
               threading.Thread(target=fitness_function, args=(children[1],)),
               threading.Thread(target=fitness_function, args=(children[2],))]
    for thread in threads:
        input('input gamecfg\n')
        thread.start()
        input('confirm\n')
    for thread in threads:
        thread.join()

    sorted(population, key=lambda p: p[1], reverse=True)
    population.pop(0)
    population.pop(0)
    population.pop(0)

    mutation_coefficient -= 1

print(population[0])
print(population)
