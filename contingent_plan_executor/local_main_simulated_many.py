from hovor.core import simulate_interaction
from local_run_utils import *
import time
import os
from glob import glob


def run_local_conversation(output_files_path):
    simulate_interaction(initialize_local_run(output_files_path))


def simulate_local_conversation(output_files_path, sample_convos_out):
    simulate_interaction(initialize_local_run_simulated(output_files_path), sample_convos_out)


if __name__ == "__main__":
    out = "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/simulation_test/"
    for i in range(1):#20):
        print(i)
        simulate_local_conversation(
            "./local_data/bartender_bot",
            out
            )
        time.sleep(1)
    for idx, f in enumerate(glob(os.path.join(out, "*.json"))):
        os.replace(f"{f.split('.json')[0]}.txt", os.path.join(out, f"convo_{idx + 1}.txt"))
        os.replace(f, os.path.join(out, f"convo_{idx + 1}.json"))
