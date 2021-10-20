import os
import numpy as np
import torch

from imitation_bot.feature_eng import make_input
from lux.game import Game


path = '/kaggle_simulations/agent' if os.path.exists('/kaggle_simulations') else '.'
model = torch.jit.load(f'{path}/model.pth')
model.eval()

game_state = None
def get_game_state(observation):
    global game_state
    
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation["player"]
    else:
        game_state._update(observation["updates"])
    return game_state


def in_city(pos):    
    try:
        city = game_state.map.get_cell_by_pos(pos).citytile
        return city is not None and city.team == game_state.id
    except:
        return False


def call_func(obj, method, args=[]):
    return getattr(obj, method)(*args)


unit_actions = [('move', 'n'), ('move', 's'), ('move', 'w'), ('move', 'e'), ('build_city',)]
def get_action(policy, unit, dest):
    for label in np.argsort(policy)[::-1]:
        act = unit_actions[label]
        pos = unit.pos.translate(act[-1], 1) or unit.pos
        if pos not in dest or in_city(pos):
            return call_func(unit, *act), pos 
            
    return unit.move('c'), unit.pos


def agent(observation, configuration):
    global game_state
    
    game_state = get_game_state(observation)    
    player = game_state.players[observation.player]
    actions = []
    
    # City Actions
    unit_count = len(player.units)
    for city in player.cities.values():
        for city_tile in city.citytiles:
            if city_tile.can_act():
                if unit_count < player.city_tile_count: 
                    actions.append(city_tile.build_worker())
                    unit_count += 1
                elif not player.researched_uranium():
                    actions.append(city_tile.research())
                    player.research_points += 1
    
    # Worker Actions
    dest = []
    for unit in player.units:
        if unit.can_act() and (game_state.turn % 40 < 30 or not in_city(unit.pos)):
            state = make_input(observation, unit.id)
            with torch.no_grad():
                p = model(torch.from_numpy(state).unsqueeze(0))

            policy = p.squeeze(0).numpy()

            action, pos = get_action(policy, unit, dest)
            actions.append(action)
            dest.append(pos)

    return actions
