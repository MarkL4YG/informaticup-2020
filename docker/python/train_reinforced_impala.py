import os

import ray
from ray.rllib.agents.impala import ImpalaTrainer
from ray.tune import register_env
from ray.tune.logger import pretty_print
from ray.tune.util import merge_dicts

from approaches.reinforced.action_state_processor import SimpleActStateProcessor
from approaches.reinforced.constants import DEFAULT_CONFIG
from approaches.reinforced.environment import SimplifiedIC20Environment, CHECKPOINT_FILE
from approaches.reinforced.observation_state_processor import SimpleObsStateProcessor, prevalence_pathogen_sorting

if __name__ == "__main__":
    ray.init(address=None)  # address = None when running locally. address = 'auto' when running on aws.]
    obs_state_processor = SimpleObsStateProcessor(pathogen_sorting_strategy=prevalence_pathogen_sorting)
    act_state_processor = SimpleActStateProcessor(sort_pathogens=obs_state_processor.sort_pathogens)

    # Notice that trial_max will only work for stochastic policies
    register_env("ic20env", lambda _: SimplifiedIC20Environment(obs_state_processor, act_state_processor, trial_max=10))

    trainer = ImpalaTrainer(
        env="ic20env",
        config=merge_dicts(DEFAULT_CONFIG, {
            # -- Specific parameters
            "vtrace": True,

            # Max global norm for each worker gradient
            'grad_clip': 40.0,
            'lr': 0.0005,
            'lr_schedule': [[0, 0.0007], [20000000, 0.000000000001]],
            'vf_loss_coeff': 0.5,
            'entropy_coeff': 0.01,
            'microbatch_size': None,
            # MDP
            'gamma': 0.99,
            "clip_rewards": True,  # std: True

            # -- Replay
            "replay_proportion": 0.3,

            # -- Batches
            "sample_batch_size": 50,  # std: 50
            "train_batch_size": 500,
            'batch_mode': 'complete_episodes',
            "min_iter_time_s": 10,
            "num_workers": 32,
            "num_gpus": 1,
            # load data into gpu in parallel -> increases vram usage
            "num_data_loader_buffers": 4,
            "replay_buffer_num_slots": 5,
            "learner_queue_timeout": 300,
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
