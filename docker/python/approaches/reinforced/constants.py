import numpy as np
from ray.rllib.models import MODEL_DEFAULTS

END_ROUND_ACTION = 0
MAX_CONNECTIONS = 11
MAX_CITIES = 5

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

DEFAULT_CONFIG = {
    # -- Rollout-Worker
    'num_gpus': 0,
    'num_workers': 0,
    "num_cpus_per_worker": 1,
    "num_gpus_per_worker": 0,
    "num_envs_per_worker": 1,

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
