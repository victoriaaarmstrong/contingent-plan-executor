import json
import ast
import os
import csv

POLICY_FILE_PATH = "/Users/victoriaarmstrong/Desktop/contingent-plan-executor/local_data/bank_bot/data.json"
## vibe coded this, might need to change
def count_conversation_length(file_path):
    """
    Counts the number of USER + AGENT conversation pairs in a text file.
    Multiple consecutive AGENT lines before a USER counts as one pair.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    conversation_length = 0

    for line in lines:
        if line.startswith("USER:"):
            conversation_length += 1

    return conversation_length

def count_redundant_actions(policy, data, domain):

    actions = policy["actions"]
    state_data = data["stats"]["complete_state"]

    ## clean the state_data so it looks nicer
    cleaned = [{k: list(v)} for d in state_data for k, v in d.items()]

    ## go through all of the items (i.e. time steps
    redundant_count = 0
    for item in cleaned:
        for key, values in item.items():
            ## if we have a get action (i.e. requesting to acquire data)
            if "get-" in key:
                conditions = actions[key]["condition"]
                value_desired = key.replace("get-", "")
                value_desired = value_desired.replace("slot-fill__", "")

                to_check = []
                if domain == "updated-gold-standard-bot":
                    ## filter conditions for unknown values that match our desired one
                    for condition in conditions:
                        if (condition[0] == value_desired) and ((condition[1] == 'Unknown') or (condition[1] == None)):
                            to_check.append(condition[0])

                    ## if we have our desired_value in our known values and we also have it in our unknown valus, we have a redundant question
                    if (value_desired in values) and (value_desired in set(to_check)):
                        #print(f"\tRedundant action found: {key}, {value_desired}, {values}, {conditions}")
                        redundant_count += 1

                elif domain == "bank-bot":
                    for condition in conditions:
                        if ((condition[1] == 'Unknown') or (condition[1] == None)):
                            to_check.append(condition[0])

                    for t_c in to_check:
                        if (t_c in set(values)):
                            redundant_count += 1

    return redundant_count

def average_time(data):
    times_str = data.get("stats", {}).get("times", "[]")

    try:
        times_list = ast.literal_eval(times_str)
        if not times_list:
            return "0.000 s"

        avg = sum(times_list) / len(times_list)

        # Format depending on size
        if avg < 1:
            # milliseconds
            formatted = f"{avg * 1e3:.2f} ms"
        else:
            # seconds
            formatted = f"{avg:.3f} s"

        return formatted

    except (SyntaxError, ValueError, TypeError):
        return "0.000 s"

def number_jumps(data):
    # Handle missing metadata or jumps key
    jumps_str = data.get("stats", {}).get("jumps", "[]")

    try:
        jumps_list = ast.literal_eval(jumps_str)
        return len(jumps_list)
    except (SyntaxError, ValueError):
        # If parsing fails, treat as empty
        return 0

def goal_check(data):
    # Safety checks
    if "messages" not in data or not data["messages"]:
        return False

    last_action = data["messages"][-1].get("action")
    return last_action == "complete"


def pair_results(folder_path):
    """
    Iterate through all files in a folder and pair up matching .txt and .json files.
    Returns a list of tuples like: [(txt_path, json_path), ...]
    """
    txt_files = {}
    json_files = {}

    # Loop through all files in the directory
    for filename in os.listdir(folder_path):
        base, ext = os.path.splitext(filename)
        if ext == '.txt':
            txt_files[base] = os.path.join(folder_path, filename)
        elif ext == '.json':
            json_files[base] = os.path.join(folder_path, filename)

    # Match .txt and .json files with the same base name
    paired = []
    for base in txt_files:
        if base in json_files:
            paired.append((txt_files[base], json_files[base]))

    return paired

def main(folder_path):

    paired_result_files = pair_results(folder_path)

    with open("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/local_data/bank_bot/data.json", "r", encoding="utf-8") as f:
        policy_data = json.load(f)

    lines = []
    for pair in paired_result_files:
        #print(pair[0].replace("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/simulation_test/testing-october-23/", ""))
        with open(pair[1], "r", encoding="utf-8") as f:
            json_data = json.load(f)

        lines.append(str(goal_check(json_data)) + "," + str(count_conversation_length(pair[0])) + "," + str(average_time(json_data)) + "," + str(number_jumps(json_data)) + "," + str(count_redundant_actions(policy_data, json_data, "bank-bot")))
    
    
    # Write to CSV
    with open("./experiments/results-static-none.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["goal_reached", "convo_length", "average_search_time", "number_jumps", "number_redundant"])  # header row (optional)

        for line in lines:
            # Split by comma and strip spaces
            row = [x.strip() for x in line.split(",")]
            writer.writerow(row)

    return

#main("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/simulation_test/creating_redundant_function_test/")
main("/Users/victoriaarmstrong/Desktop/contingent-plan-executor/simulation_test/testing-october-23/static/none/")