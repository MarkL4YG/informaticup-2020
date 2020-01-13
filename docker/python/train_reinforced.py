import os

import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune import register_env
from ray.tune.logger import pretty_print

from approaches.reinforced.action_state_processor import SimpleActStateProcessor
from approaches.reinforced.environment import SimplifiedIC20Environment, CHECKPOINT_FILE
from approaches.reinforced.observation_state_processor import SimpleObsStateProcessor, prevalence_pathogen_sorting

if __name__ == "__main__":
    ray.init(address=None)  # address = None when running locally. address = 'auto' when running on aws.]
    obs_state_processor = SimpleObsStateProcessor(pathogen_sorting_strategy=prevalence_pathogen_sorting)
    act_state_processor = SimpleActStateProcessor(sort_pathogens=obs_state_processor.sort_pathogens)

    # Notice that trial_max will only work for stochastic policies
    register_env("ic20env", lambda _: SimplifiedIC20Environment(obs_state_processor, act_state_processor, trial_max=10))

    trainer = PPOTrainer(
        env="ic20env",
        config={
            "num_gpus": 0,
            "gamma": 0.99,
            "lr": 0.0001,
            "sgd_minibatch_size": 1000,
            "batch_mode": "complete_episodes",
            "num_workers": 0,
            "timesteps_per_iteration": 200,
        })

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
