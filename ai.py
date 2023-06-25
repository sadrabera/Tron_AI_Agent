# -*- coding: utf-8 -*-

# python imports
import json
import random
import time

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
        self.prev_decision = Moves(False, False, False, "Yellow")
        self.left_right = 0

    
    hs_variables=dict()
    
    def initialize(self):
        print('initialize')
        print(str(self.world.agents[self.my_side].position) + "first step")
        print(str(self.world.constants.area_wall_crash_score))
        print(str(self.world.constants.my_wall_crash_score))
        print(str(self.world.constants.enemy_wall_crash_score))
        with open('HS.json') as json_file:
            hs_variables = json.load(json_file)


    def decide(self):
        print('decide')
        game_state = Game_State(self.world, self.my_side, self.other_side, self.left_right)
        start = time.time()
        minimax_l = self.minimax(game_state, 8, True)
        end = time.time()
        print(self.left_right)
        print("time: " + str((end - start)))
        if end - start > 8:
            print('wtf')
        next_move = minimax_l[1]
        self.prev_decision = next_move
        if next_move is not None:

            if next_move.wall_breaker:
                self.send_command(ActivateWallBreaker())
            if next_move.move_left:
                if self.left_right > 0:
                    self.left_right = 0
                self.left_right -= 1
                if self.world.agents[self.my_side].direction == EDirection.Up:
                    self.send_command(ChangeDirection(EDirection.Left))
                if self.world.agents[self.my_side].direction == EDirection.Left:
                    self.send_command(ChangeDirection(EDirection.Down))
                if self.world.agents[self.my_side].direction == EDirection.Down:
                    self.send_command(ChangeDirection(EDirection.Right))
                if self.world.agents[self.my_side].direction == EDirection.Right:
                    self.send_command(ChangeDirection(EDirection.Up))
            elif next_move.move_right:
                if self.left_right < 0:
                    self.left_right = 0
                self.left_right += 1
                if self.world.agents[self.my_side].direction == EDirection.Up:
                    self.send_command(ChangeDirection(EDirection.Right))
                if self.world.agents[self.my_side].direction == EDirection.Left:
                    self.send_command(ChangeDirection(EDirection.Up))
                if self.world.agents[self.my_side].direction == EDirection.Down:
                    self.send_command(ChangeDirection(EDirection.Left))
                if self.world.agents[self.my_side].direction == EDirection.Right:
                    self.send_command(ChangeDirection(EDirection.Down))

    def minimax(self, game_state, depth: int, maximizingPlayer: bool, alpha=float('-inf'), beta=float('inf')):
        if (depth == 0) or (game_state.is_terminal()):
            return game_state.HS(self.my_side, self.other_side), None

        if maximizingPlayer:
            value = float('-inf')
            possible_moves = game_state.get_possible_moves(self.my_side, self.prev_decision)
            for move in possible_moves:
                child = game_state.get_new_state(move, self.my_side)
                tmp = self.minimax(child, depth - 1, False, alpha, beta)[0]
                if tmp > value:
                    value = tmp
                    best_movement = move
                    best_state = child

                if value >= beta:
                    break
                alpha = max(alpha, value)

        else:
            value = float('inf')
            possible_moves = game_state.get_possible_moves(self.other_side, self.prev_decision)
            for move in possible_moves:

                child = game_state.get_new_state(move, self.my_side)

                tmp = self.minimax(child, depth - 1, True, alpha, beta)[0]
                if tmp < value:
                    value = tmp
                    best_movement = move
                    best_state = child

                if value <= alpha:
                    break
                beta = min(beta, value)

        return value, best_movement


class Moves:
    def __init__(self, wall_breaker=False, move_left=False, move_right=False, side=None):
        self.wall_breaker = wall_breaker
        self.move_left = move_left
        self.move_right = move_right
        self.side = side


class Game_State:
    def __init__(self, world: World, my_side, other_side, left_right):
        self.world = world
        self.my_side = my_side
        self.other_side = other_side
        self.left_right = left_right

    def HS(self, my_side, other_side):

        diff_points = self.world.scores[my_side] - self.world.scores[other_side]
        if self.is_terminal():
            return diff_points
        
        agents = self.world.agents

        diff_points += agents[my_side].health * hs_variables["value per health"]
        diff_points -= agents[other_side].health * hs_variables["value per health"]

        # if abs(self.left_right) > 2:
        #     diff_points -= (abs(self.left_right) - 2) * hs_variables["left and right"]

        return diff_points

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

    def get_possible_moves(self, side, prev_decision: Moves):
        agents = self.world.agents

        if self.left_right == 2:
            possible_moves = [Moves(False, False, False, side), Moves(False, True, False, side),
                              Moves(False, False, True, side)]
        elif self.left_right == -2:
            possible_moves = [Moves(False, False, False, side), Moves(False, False, True, side),
                              Moves(False, False, False, side)]
        elif self.left_right > 2 or (prev_decision.move_left and self.left_right > -2):
            possible_moves = [Moves(False, True, False, side), Moves(False, False, False, side),
                              Moves(False, False, True, side)]
        elif self.left_right < -2 or (prev_decision.move_right and self.left_right < 2):
            possible_moves = [Moves(False, False, True, side), Moves(False, False, False, side),
                              Moves(False, True, False, side)]
        else:
            possible_moves = [Moves(False, False, False, side), Moves(False, True, False, side),
                              Moves(False, False, True, side)]

        if agents[side].wall_breaker_rem_time == 0 and agents[side].wall_breaker_cooldown == 0:
            if self.left_right > 2 or (prev_decision.move_left and self.left_right > -2):
                possible_moves.extend([Moves(True, True, False, side), Moves(True, False, False, side),
                                       Moves(True, False, True, side)])
            elif self.left_right < -2 or (prev_decision.move_right and self.left_right < 2):
                possible_moves.extend([Moves(True, False, True, side), Moves(True, False, False, side),
                                       Moves(True, True, False, side)])
            else:
                possible_moves.extend([Moves(True, False, False, side), Moves(True, True, False, side),
                                       Moves(True, False, True, side)])

        return possible_moves

    def get_new_state(self, move: Moves, actual_my_side):

        new_world = deepcopy(self.world)

        agent = new_world.agents[move.side]
        new_left_right = self.left_right
        # print(self.left_right)

        if move.move_left:
            if actual_my_side == move.side:
                if new_left_right > 0:
                    new_left_right = 0
                new_left_right -= 1
            if agent.direction == EDirection.Up:
                agent.position.x -= 1
                agent.direction = EDirection.Left
            elif agent.direction == EDirection.Left:
                agent.position.y += 1
                agent.direction = EDirection.Down
            elif agent.direction == EDirection.Down:
                agent.position.x += 1
                agent.direction = EDirection.Right
            elif agent.direction == EDirection.Right:
                agent.position.y -= 1
                agent.direction = EDirection.Up

        elif move.move_right:
            if actual_my_side == move.side:
                if new_left_right < 0:
                    new_left_right = 0
                new_left_right += 1
            if agent.direction == EDirection.Up:
                agent.position.x += 1
                agent.direction = EDirection.Right
            elif agent.direction == EDirection.Left:
                agent.position.y -= 1
                agent.direction = EDirection.Up
            elif agent.direction == EDirection.Down:
                agent.position.x -= 1
                agent.direction = EDirection.Left
            elif agent.direction == EDirection.Right:
                agent.position.y += 1
                agent.direction = EDirection.Down

        else:
            if agent.direction == EDirection.Up:
                agent.position.y -= 1
            elif agent.direction == EDirection.Left:
                agent.position.x -= 1
            elif agent.direction == EDirection.Down:
                agent.position.y += 1
            elif agent.direction == EDirection.Right:
                agent.position.x += 1

        constants = self.world.constants
        if move.wall_breaker:
            agent.wall_breaker_rem_time = constants.wall_breaker_duration
        elif agent.wall_breaker_rem_time > 1:
            agent.wall_breaker_rem_time -= 1
        elif agent.wall_breaker_cooldown > 1:
            agent.wall_breaker_cooldown -= 1

        new_cell = new_world.board[agent.position.y][agent.position.x]
        scores = new_world.scores
        if new_cell == ECell.BlueWall or new_cell == ECell.YellowWall:
            if agent.wall_breaker_rem_time < 2:
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
                scores[move.side] += constants.area_wall_crash_score
            elif move.side == "Yellow":
                if new_cell == ECell.YellowWall:
                    scores[move.side] += constants.my_wall_crash_score
                if new_cell == ECell.BlueWall:
                    scores[move.side] += constants.enemy_wall_crash_score
            elif move.side == "Blue":
                if new_cell == ECell.BlueWall:
                    scores[move.side] += constants.my_wall_crash_score
                if new_cell == ECell.YellowWall:
                    scores[move.side] += constants.enemy_wall_crash_score
        new_game_state = Game_State(new_world, self.other_side, self.my_side, new_left_right)
        return new_game_state
