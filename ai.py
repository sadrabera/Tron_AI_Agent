# -*- coding: utf-8 -*-

# python imports
import json
import random

# chillin imports
from chillin_client import RealtimeAI
from copy import deepcopy

# project imports
from ks.models import ECell, EDirection, Position, World, Agent
from ks.commands import ChangeDirection, ActivateWallBreaker
from queue import Queue


def find_neighbor(x, y):
    return (y, x - 1), (y + 1, x), (y, x + 1), (y - 1, x)


class AI(RealtimeAI):

    def __init__(self, world):
        super(AI, self).__init__(world)

    def initialize(self):
        print('initialize')

    def decide(self):
        print('decide')
        game_state = Game_State(self.world, self.other_side, self.my_side)
        minimax_l = self.minimax(game_state, 6, False)
        next_move = minimax_l[1]
        # print("_-_-_")
        # print(minimax_l[0])
        # print("_-_-_")
        if next_move != None:
            print("--")
            print(next_move.wall_breaker)
            print(next_move.move_left)
            print(next_move.move_right)
            print("--")

            if next_move.wall_breaker:
                self.send_command(ActivateWallBreaker())
            if next_move.move_left:
                if self.world.agents[self.my_side].direction == EDirection.Up:
                    self.send_command(ChangeDirection(EDirection.Left))
                if self.world.agents[self.my_side].direction == EDirection.Left:
                    self.send_command(ChangeDirection(EDirection.Down))
                if self.world.agents[self.my_side].direction == EDirection.Down:
                    self.send_command(ChangeDirection(EDirection.Right))
                if self.world.agents[self.my_side].direction == EDirection.Right:
                    self.send_command(ChangeDirection(EDirection.Up))
            elif next_move.move_right:
                if self.world.agents[self.my_side].direction == EDirection.Up:
                    self.send_command(ChangeDirection(EDirection.Right))
                if self.world.agents[self.my_side].direction == EDirection.Left:
                    self.send_command(ChangeDirection(EDirection.Up))
                if self.world.agents[self.my_side].direction == EDirection.Down:
                    self.send_command(ChangeDirection(EDirection.Left))
                if self.world.agents[self.my_side].direction == EDirection.Right:
                    self.send_command(ChangeDirection(EDirection.Down))

    # self.client1()
    # self.send_command(ChangeDirection(random.choice(list(EDirection))))
    # if self.world.agents[self.my_side].wall_breaker_cooldown == 0:
    #     self.send_command(ActivateWallBreaker())

    # def client1(self):
    #     my_team = self.my_side
    #     empty_neighbors = self._get_our_agent_empty_neighbors()
    #     blue_walls = self._get_our_agent_blue_wall_neighbors()
    #     yellow_walls = self._get_our_agent_yellow_wall_neighbors()
    #     area_walls = self._get_our_agent_Area_wall_neighbors()
    #     # print(self.world.agents)
    #     # print(self.find_distance_from_nearest_Area_wall())
    #     # print(f"empty_neighbors : {empty_neighbors}")
    #     # print(f"blue_walls : {blue_walls}")
    #     # print(f"yellow_walls : {yellow_walls}")
    #     if self.world.agents[self.my_side].wall_breaker_rem_time > 1:
    #         # wall breaker is on
    #         if my_team == "Yellow":
    #             if blue_walls:
    #                 self.send_command(ChangeDirection(random.choice(blue_walls)))
    #             elif empty_neighbors:
    #                 self.send_command(ChangeDirection(random.choice(empty_neighbors)))
    #             elif yellow_walls:
    #                 self.send_command(ChangeDirection(random.choice(yellow_walls)))
    #             else:
    #                 self.send_command(ChangeDirection(random.choice(list(EDirection))))
    #         else:
    #             if yellow_walls:
    #                 self.send_command(ChangeDirection(random.choice(yellow_walls)))
    #             elif empty_neighbors:
    #                 self.send_command(ChangeDirection(random.choice(empty_neighbors)))
    #             elif blue_walls:
    #                 self.send_command(ChangeDirection(random.choice(blue_walls)))
    #             else:
    #                 self.send_command(ChangeDirection(random.choice(list(EDirection))))
    #
    #     else:
    #         # wall breaker is off
    #         if empty_neighbors:
    #             self.send_command(ChangeDirection(random.choice(empty_neighbors)))
    #         else:
    #
    #             if self.world.agents[my_team].wall_breaker_cooldown == 0 and not (
    #                     self.world.agents[my_team].direction in area_walls):
    #                 self.send_command(ActivateWallBreaker())
    #             else:
    #                 if my_team == "Yellow":
    #                     if blue_walls:
    #                         self.send_command(ChangeDirection(random.choice(blue_walls)))
    #                     elif yellow_walls:
    #                         self.send_command(ChangeDirection(random.choice(yellow_walls)))
    #                     else:
    #                         self.send_command(ChangeDirection(random.choice(list(EDirection))))
    #                 else:
    #                     if yellow_walls:
    #                         self.send_command(ChangeDirection(random.choice(yellow_walls)))
    #                     elif blue_walls:
    #                         self.send_command(ChangeDirection(random.choice(blue_walls)))
    #                     else:
    #                         self.send_command(ChangeDirection(random.choice(list(EDirection))))

    def _get_our_agent_empty_neighbors(self):
        empty_neighbors = []

        our_position = self._get_our_agent_position()

        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.Empty and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.Empty and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                empty_neighbors.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                empty_neighbors.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.Empty and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                empty_neighbors.append(EDirection.Up)
        return empty_neighbors

    def _get_our_agent_blue_wall_neighbors(self):
        blue_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.BlueWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.BlueWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                blue_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                blue_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.BlueWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                blue_walls.append(EDirection.Up)
        return blue_walls

    def _get_our_agent_yellow_wall_neighbors(self):
        yellow_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.YellowWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.YellowWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                yellow_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                yellow_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.YellowWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                yellow_walls.append(EDirection.Up)
        return yellow_walls

    def _get_our_agent_Area_wall_neighbors(self):
        area_walls = []
        our_position = self._get_our_agent_position()
        their_position = self._get_their_agent_position()
        if our_position.x + 1 < len(self.world.board[0]):
            if self.world.board[our_position.y][our_position.x + 1] == ECell.AreaWall and \
                    not (our_position.x + 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Right)
        if our_position.x - 1 >= 0:
            if self.world.board[our_position.y][our_position.x - 1] == ECell.AreaWall and \
                    not (our_position.x - 1 == their_position.x and our_position.y == their_position.y):
                area_walls.append(EDirection.Left)
        if our_position.y + 1 < len(self.world.board):
            if self.world.board[our_position.y + 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y + 1 == their_position.y):
                area_walls.append(EDirection.Down)
        if our_position.y - 1 >= 0:
            if self.world.board[our_position.y - 1][our_position.x] == ECell.AreaWall and \
                    not (our_position.x == their_position.x and our_position.y - 1 == their_position.y):
                area_walls.append(EDirection.Up)
        return area_walls

    def _get_our_agent_position(self):
        return self.world.agents[self.my_side].position

    def _get_their_agent_position(self):
        return self.world.agents[self.other_side].position

    # def bfs(self, graph, start_node):
    #     visited = {node: False for node in graph}
    #     q = Queue()
    #     q.put(start_node)
    #     visited[start_node] = True
    #
    #     while not q.empty():
    #         current_node = q.get()
    #         print(current_node)
    #
    #         for neighbor in graph[current_node]:
    #             if not visited[neighbor]:
    #                 visited[neighbor] = True
    #                 q.put(neighbor)

    def minimax(self, game_state, depth: int, maximizingPlayer: bool, alpha=float('-inf'), beta=float('inf')):

        if (depth == 0) or (game_state.is_terminal()):
            return game_state.HS(), None

        if maximizingPlayer:
            value = float('-inf')
            possible_moves = game_state.get_possible_moves(self.my_side)
            for move in possible_moves:
                child = game_state.get_new_state(move)

                tmp = self.minimax(child, depth - 1, False, alpha, beta)[0]
                if tmp > value:
                    value = tmp
                    best_movement = move

                if value >= beta:
                    break
                alpha = max(alpha, value)

        else:
            value = float('inf')
            possible_moves = game_state.get_possible_moves(self.other_side)
            for move in possible_moves:
                child = game_state.get_new_state(move)

                tmp = self.minimax(child, depth - 1, True, alpha, beta)[0]
                if tmp < value:
                    value = tmp
                    best_movement = move

                if value <= alpha:
                    break
                beta = min(beta, value)
        # print(value)
        return value, best_movement


class Moves:
    def __init__(self, wall_breaker=False, move_left=False, move_right=False, side=None):
        self.wall_breaker = wall_breaker
        self.move_left = move_left
        self.move_right = move_right
        self.side = side


class Game_State:
    def __init__(self, world: World, my_side, other_side):
        self.world = world
        self.my_side = my_side
        self.other_side = other_side

    def HS(self):

        # diff_points = self.world.scores[self.my_side] - self.world.scores[self.other_side]
        diff_points = self.world.scores[self.my_side]
        if self.is_terminal():
            return diff_points
        hs_variables = dict()
        with open('HS.json') as json_file:
            hs_variables = json.load(json_file)
        agents = self.world.agents
        print("distance: "+str(self.find_distance_from_nearest_Area_wall()))
        diff_points += self.find_distance_from_nearest_Area_wall()*hs_variables["Distance from nearest Area wall"]
        diff_points -= agents[self.my_side].wall_breaker_cooldown * hs_variables["empty cooldown per second"]
        # diff_points += agents[self.other_side].wall_breaker_cooldown * hs_variables["empty cooldown per second"]

        diff_points += agents[self.my_side].wall_breaker_rem_time * hs_variables["remaning coldown per second"]
        # diff_points -= agents[self.other_side].wall_breaker_rem_time * hs_variables["remaning coldown per second"]

        diff_points += agents[self.my_side].health * hs_variables["value per health"]
        # diff_points -= agents[self.other_side].health * hs_variables["value per health"]

        if agents[self.my_side].wall_breaker_rem_time == 0 and agents[
            self.my_side].wall_breaker_cooldown == 0:
            diff_points += hs_variables["full Cooldown"] * self.world.constants.wall_breaker_duration
        # if agents[self.other_side].wall_breaker_rem_time == 0 and agents[
        #     self.other_side].wall_breaker_cooldown == 0:
        #     diff_points -= hs_variables["full Cooldown"] * self.world.constants.wall_breaker_duration

        return diff_points

    def find_distance_from_nearest_Area_wall(self):  # using bfs
        visited = {}
        q = Queue()
        my_agent_position = self.world.agents[self.my_side].position
        our_position = (my_agent_position.y, my_agent_position.x)
        q.put(our_position)
        visited[our_position] = True
        while not q.empty():
            current_node = q.get()
            for neighbor in find_neighbor(current_node[1], current_node[0]):
                if neighbor not in visited:
                    try:
                        if self.world.board[neighbor[0]][neighbor[1]] == ECell.AreaWall:
                            return abs(neighbor[0] - my_agent_position.y) + abs(neighbor[1] - my_agent_position.x)
                    except:
                        pass
                    visited[neighbor] = True
                    q.put(neighbor)

    def is_terminal(self):
        agents = self.world.agents
        our_position = agents[self.my_side].position
        other_position = agents[self.other_side].position
        board = self.world.board

        if board[our_position.y][our_position.x] == ECell.AreaWall or board[other_position.y][
            other_position.x] == ECell.AreaWall:
            return True

        if agents[self.my_side].health == 0 or agents[self.other_side].health == 0:
            return True

        if our_position.y == other_position.y and our_position.x == other_position.x:
            return True

        return False

    def get_possible_moves(self, side):
        agents = self.world.agents

        possible_moves = [Moves(False, False, False, side), Moves(False, True, False, side),
                          Moves(False, False, True, side)]

        if agents[self.my_side].wall_breaker_rem_time == 0 and agents[self.my_side].wall_breaker_cooldown == 0:
            possible_moves.extend(
                [Moves(True, False, False, side), Moves(True, True, False, side), Moves(True, False, True, side)])

        return possible_moves

    def get_new_state(self, move: Moves):
        new_world = deepcopy(self.world)
        agent = new_world.agents[move.side]

        if move.move_left:
            if agent.direction == EDirection.Up:
                agent.position.x -= 1
                agent.direction = EDirection.Left
            if agent.direction == EDirection.Left:
                agent.position.y -= 1
                agent.direction = EDirection.Down
            if agent.direction == EDirection.Down:
                agent.position.x += 1
                agent.direction = EDirection.Right
            if agent.direction == EDirection.Right:
                agent.position.y += 1
                agent.direction = EDirection.Up

        elif move.move_right:
            if agent.direction == EDirection.Up:
                agent.position.x += 1
                agent.direction = EDirection.Right
            if agent.direction == EDirection.Left:
                agent.position.y += 1
                agent.direction = EDirection.Up
            if agent.direction == EDirection.Down:
                agent.position.x -= 1
                agent.direction = EDirection.Left
            if agent.direction == EDirection.Right:
                agent.position.y -= 1
                agent.direction = EDirection.Down

        else:
            if agent.direction == EDirection.Up:
                agent.position.y += 1
            if agent.direction == EDirection.Left:
                agent.position.x += 1
            if agent.direction == EDirection.Down:
                agent.position.y -= 1
            if agent.direction == EDirection.Right:
                agent.position.x -= 1

        constants = self.world.constants
        if move.wall_breaker:
            agent.wall_breaker_rem_time = constants.wall_breaker_duration
        elif agent.wall_breaker_rem_time > 1:
            agent.wall_breaker_rem_time -= 1
        elif agent.wall_breaker_cooldown > 1:
            agent.wall_breaker_cooldown -= 1

        new_cell = new_world.board[agent.position.y][agent.position.x]
        scores = self.world.scores
        if new_cell == ECell.BlueWall or new_cell == ECell.YellowWall:

            if agent.wall_breaker_rem_time < 1:
                agent.health -= 1
            if new_cell == ECell.BlueWall:
                scores["Blue"] -= constants.wall_score_coefficient
            if new_cell == ECell.YellowWall:
                scores["Yellow"] -= constants.wall_score_coefficient

        scores[move.side] += constants.wall_score_coefficient

        if new_cell == ECell.AreaWall:
            agent.health = 0
        elif move.side == "Blue":
            new_cell = ECell.BlueWall
        elif move.side == "Yellow":
            new_cell = ECell.YellowWall

        if agent.health == 0:
            if new_cell == ECell.AreaWall:
                scores[move.side] -= constants.area_wall_crash_score
            if move.side == "Yellow":
                if new_cell == ECell.YellowWall:
                    scores[move.side] -= constants.my_wall_crash_score
                if new_cell == ECell.BlueWall:
                    scores[move.side] -= constants.enemy_wall_crash_score
            if move.side == "Blue":
                if new_cell == ECell.BlueWall:
                    scores[move.side] -= constants.my_wall_crash_score
                if new_cell == ECell.YellowWall:
                    scores[move.side] -= constants.enemy_wall_crash_score
        return Game_State(new_world, self.other_side, self.my_side)
