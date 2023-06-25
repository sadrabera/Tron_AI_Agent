import subprocess
import re
import random


def fitness_function(new_HS):
    print(new_HS)
    input("change gamecfg")
    result = subprocess.run(['python', 'main.py'], stdout=subprocess.PIPE)
    out_result = result.stdout.decode('utf-8')
    find_blue = re.compile(r'Blue -> -?\d+')
    find_yellow = re.compile(r'Yellow -> -?\d+')
    find_number = re.compile(r'-?\d+')
    blue_point = find_blue.findall(out_result)[0]
    yellow_point = find_yellow.findall(out_result)[0]
    return int(find_number.findall(yellow_point)[0]) - int(find_number.findall(blue_point)[0])


def mean_crossover(parent1, parent2):
    alpha = random.random()
    value_per_health = alpha * parent1['value per health'] + (1 - alpha) * parent2['value per health']
    left_and_right = alpha * parent1['left and right'] + (1 - alpha) * parent2['left and right']
    child = [value_per_health, left_and_right]
    return child


def mutation(child, mutation_coefficient):
    mutate_parameter = random.choices(['value per health', 'left and right'])
    mutate_sign = random.choices([1, -1])
    child[mutate_parameter] += mutation_coefficient * mutate_sign
    return child


agent1 = {'value per health': 25, 'left and right': 5}
agent2 = {'value per health': 11, 'left and right': 19}
agent3 = {'value per health': 15, 'left and right': 15}
agent4 = {'value per health': 5, 'left and right': 25}
agent5 = {'value per health': 27, 'left and right': 14}
agent6 = {'value per health': 9, 'left and right': 18}

population = [(agent1, fitness_function(agent1)),
              (agent2, fitness_function(agent2)),
              (agent3, fitness_function(agent3)),
              (agent4, fitness_function(agent4)),
              (agent5, fitness_function(agent5)),
              (agent6, fitness_function(agent6))]

num_generations = 10

crossover_type = mean_crossover
crossover_possibility = 0.9

best_agent = agent1
max_point = float('-inf')
for agent, point in population:
    if point > max_point:
        best_agent = agent
        max_point = point

mutation_possibility = 0.1
mutation_coefficient = 5

for _ in range(num_generations):
    for i in range(3):
        if random.random() < crossover_possibility:
            parent1, parent2 = random.choices([p[0] for p in population], weights=[p[1] for p in population], k=2)
            child = mean_crossover(parent1, parent2)
            if random.random() < mutation_possibility:
                child = mutation(child, mutation_coefficient)
                point = fitness_function(child)
                population.append((child, point))
                if point > max_point:
                    best_agent = child
                    max_point = point
        else:
            i -= 1

    sorted(population, key=lambda p: p[1], reverse=True)
    population.pop(0)
    population.pop(0)
    population.pop(0)

    mutation_coefficient -= 0.5
