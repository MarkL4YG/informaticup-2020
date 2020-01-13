import os

import ray
from ray.rllib.agents.dqn import ApexTrainer
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
    register_env('ic20env', lambda _: SimplifiedIC20Environment(obs_state_processor, act_state_processor, trial_max=10))

    trainer = ApexTrainer(
        env="ic20env",
        config=merge_dicts(DEFAULT_CONFIG, {
            "per_worker_exploration": True,
            "worker_side_prioritization": True,
            "min_iter_time_s": 30,
            "timesteps_per_iteration": 25000,

            # -- Specific parameters
            'num_gpus': 1,
            'num_workers': 32,
            "num_atoms": 4,  # std: 1
            "v_min": -10.0,
            "v_max": 10.0,

            # noise-net
            "noisy": False,
            "sigma0": 0.5,

            "hiddens": [256],


            "dueling": True,
            "double_q": True,
            "target_network_update_freq": 500000,

            "n_step": 3,

            # exploration
            "schedule_max_timesteps": 100000,

            # replay buffer
            "buffer_size": 2000000,
            "learning_starts": 50000,
            "prioritized_replay": True,

            # GAE(gamma) parameter
            'lambda': 1.0,
            # Max global norm for each worker gradient
            'grad_clip': 40.0,
            'lr': 0.0005,
            "adam_epsilon": 0.000001,
            'vf_loss_coeff': 0.5,
            'entropy_coeff': 0.01,
            'microbatch_size': None,

            'optimizer': {
                "max_weight_sync_delay": 400,
                "num_replay_buffer_shards": 4,
                "debug": False
            },

            # MDP
            'gamma': 0.99,
            "clip_rewards": False,  # apex_std: False

            # -- Batches
            "sample_batch_size": 50,
            "train_batch_size": 512,
            'batch_mode': 'complete_episodes',
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
