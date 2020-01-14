import numpy as np
from ray.rllib.evaluation import MultiAgentEpisode
from ray.rllib.models import MODEL_DEFAULTS

END_ROUND_ACTION = 0
MAX_CONNECTIONS = 11
MAX_CITIES = 260

# global action-space:
# [end_round[0],
# develop: vaccine[1], vaccine2[2], vaccine3[3], vaccine4[4], vaccine5[5],
# develop: med1[6], med2[7], med3[8], med4[9], med5[10]] -> 11 actions
# city action-space:
# [quarantine[11], close-airport[12], hygienic_measures [13], political-influence[14],
# call-for-elections[15], launch-campaign [16],
# deploy: vaccine[17], vaccine2[18], vaccine3[19], vaccine4[20], vaccine5[21],
# deploy: med1[22], med2[23], med3[24], med4[25], med5[26]] -> 16 actions => 27 Actions in total
GLOBAL_ACTIONSPACE = 11
CITY_ACTIONSPACE = 16
MAX_ACTIONSPACE = GLOBAL_ACTIONSPACE + CITY_ACTIONSPACE * MAX_CITIES
MAX_CITY_ACTIONSPACE = MAX_ACTIONSPACE - 1
MAX_PATHOGENS = 5
END_EPISODE_RESPONSE = "END_EPISODE"
NEUTRAL_REWARD = 0
PATH_TO_IC20 = "./ic20_linux"
INVALID_ACTION = None
UINT32_MAX = np.iinfo(np.uint32).max
INVALID_ACTION_PENALTY = -1


# noinspection PyStatementEffect
def on_episode_end(info):
    episode: MultiAgentEpisode = info['episode']
    info = episode.last_info_for()
    outcome = info['outcome']
    rounds_played = info['rounds_played']
    print(f"episode {episode.episode_id} with: #actions: {episode.length}, "
          f"Rounds: {rounds_played}, "
          f"Outcome: {outcome}, "
          f"Reward: {episode.total_reward}")
    if outcome == 'win':
        episode.custom_metrics["rounds_played_until_win"] = rounds_played
        episode.custom_metrics["round_outcome"] = outcome

    if outcome == 'loss':
        episode.custom_metrics["rounds_played_until_loss"] = rounds_played
        episode.custom_metrics["round_outcome"] = outcome


DEFAULT_CONFIG = {
    # -- Trainer details
    "model": MODEL_DEFAULTS,
    "optimizer": {},

    # -- MDP details
    "clip_rewards": None,
    "clip_actions": True,
    'timesteps_per_iteration': 200,

    # -- Evaluation
    # Number of episodes to run per evaluation period.
    "evaluation_num_episodes": 10,
    "callbacks": {
        "on_episode_end": on_episode_end
    },

    # -- Multiagent
    "multiagent": {
        "policies": {},
        "policy_mapping_fn": None,
        "policies_to_train": None
    },

    # -- Debug
    "log_level": "WARN",
    "eager": False,
    "seed": None,
    "memory": 0,
    "object_store_memory": 0,
    "memory_per_worker": 0,
    "object_store_memory_per_worker": 0
}
