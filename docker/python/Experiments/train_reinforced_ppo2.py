import os

import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune import register_env
from ray.tune.logger import pretty_print
from ray.tune.util import merge_dicts

from approaches.reinforced.action_state_processor import SimpleActStateProcessor
from approaches.reinforced.constants import DEFAULT_CONFIG
from approaches.reinforced.environment import SimplifiedIC20Environment, CHECKPOINT_FILE
from approaches.reinforced.observation_state_processor import SimpleObsStateProcessor, prevalence_pathogen_sorting
from approaches.reinforced.reward_function import UnstableReward

if __name__ == "__main__":
    ray.init(address='auto')  # address = None when running locally. address = 'auto' when running on aws.]
    obs_state_processor = SimpleObsStateProcessor(pathogen_sorting_strategy=prevalence_pathogen_sorting)
    act_state_processor = SimpleActStateProcessor(sort_pathogens=obs_state_processor.sort_pathogens)

    # Notice that trial_max will only work for stochastic policies
    register_env("ic20env",
                 lambda _: SimplifiedIC20Environment(obs_state_processor, act_state_processor, UnstableReward(),
                                                     trial_max=10))
    ten_gig = 10737418240

    trainer = PPOTrainer(
        env="ic20env",
        config=merge_dicts(DEFAULT_CONFIG, {
            # -- Rollout-Worker
            'num_gpus': 0,
            'num_workers': 5,
            "num_envs_per_worker": 1,
            "num_cpus_per_worker": 1,
            "memory_per_worker": ten_gig,
            'gamma': 0.99,
        }))

    # Attempt to restore from checkpoint if possible.
    if os.path.exists(CHECKPOINT_FILE):
        checkpoint_path = open(CHECKPOINT_FILE).read()
        print("Restoring from checkpoint path", checkpoint_path)
        trainer.restore(checkpoint_path)

    # Serving and training loop
    while True:
        print(pretty_print(trainer.train()))
        checkpoint_path = trainer.save()
        print("Last checkpoint", checkpoint_path)
        with open(CHECKPOINT_FILE, "w") as f:
            f.write(checkpoint_path)
