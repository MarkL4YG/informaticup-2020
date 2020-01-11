import os

import ray
from ray.rllib.agents.ppo import PPOTrainer
from ray.tune import register_env
from ray.tune.logger import pretty_print

from approaches.reinforced.environment import SimplifiedIC20Environment, CHECKPOINT_FILE

if __name__ == "__main__":
    ray.init()  # address = None when running locally. address = 'auto' when running on aws.
    register_env("srv", lambda _: SimplifiedIC20Environment())

    trainer = PPOTrainer(
        env="srv",
        config={
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
