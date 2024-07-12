import subprocess
import argparse

# Define the defense strategies including the option for no defenses
defense_strategies = [
    "none",
    "differential_privacy",
    "regularization",
    "adversarial_training",
    "model_pruning",
    "all"
]

# Define the datasets and poisoned variants
datasets = ["IOTBOTNET", "CICIOT"]
poisoned_variants = ["LF33", "LF66", "FN33", "FN66"]

# Define the IP addresses for each node
node_ips = {
    1: "192.168.129.1",
    2: "192.168.129.3",
    3: "192.168.129.4",
    4: "192.168.129.5",
    5: "192.168.129.9",
    6: "192.168.129.10",
    "server": "192.168.129.2"
}

def run_command(command):
    print(f"Executing: {command}")
    process = subprocess.Popen(command, shell=True)
    process.communicate()

def run_server():
    print("Starting the server node")
    command = "python3 server.py"
    while True:
        run_command(command)

def run_client(node, dataset, poisoned_data, strategy, log_file):
    reg_flag = "--reg" if strategy in ["regularization", "all"] else ""
    dp_flag = "--dp" if strategy in ["differential_privacy", "all"] else ""
    prune_flag = "--prune" if strategy in ["model_pruning", "all"] else ""
    adv_flag = "--adversarial" if strategy in ["adversarial_training", "all"] else ""

    p_data_flag = f"--pData {poisoned_data}" if poisoned_data else ""

    command = (
        f"python3 clientExperiment.py --dataset {dataset} --node {node} {p_data_flag} --evalLog eval_{log_file} --trainLog train_{log_file} {reg_flag} {dp_flag} {prune_flag} {adv_flag}"
    )
    
    run_command(command)

def main():
    parser = argparse.ArgumentParser(description="Federated Learning Training Script Automation")
    parser.add_argument("--role", type=str, choices=["server", "client"], required=True, help="Role of the node: server or client")
    parser.add_argument("--node", type=int, choices=list(node_ips.keys())[:-1], help="Node number (required for clients)")
    parser.add_argument("--datasets", type=str, nargs='+', choices=datasets, required=True, help="List of datasets to use")
    parser.add_argument("--pvar", type=str, nargs='+', choices=poisoned_variants, required=True, help="List of poisoned variants to use")
    parser.add_argument("--defense_strat", type=str, nargs='+', choices=defense_strategies, required=True, help="List of defense strategies to use")
    parser.add_argument("--cleannodes", type=int, nargs='+', required=True, help="List of numbers of clean nodes to use in each experiment")

    args = parser.parse_args()

    compromised_node = 1  # Always set node 1 as the compromised node
    num_clean_nodes_list = args.cleannodes
    selected_datasets = args.datasets
    selected_poisoned_variants = args.pvar
    selected_defense_strategies = args.defense_strat

    print(f"Role: {args.role}")
    print(f"Node: {args.node if args.role == 'client' else 'N/A'}")
    print(f"Datasets: {selected_datasets}")
    print(f"Poisoned Variants: {selected_poisoned_variants}")
    print(f"Defense Strategies: {selected_defense_strategies}")
    print(f"Clean Nodes: {num_clean_nodes_list}")

    if args.role == "server":
        run_server()
    else:
        current_node = args.node
        if current_node is None:
            print("Node number must be specified for client role.")
            return

        for dataset in selected_datasets:
            for poisoned_variant in selected_poisoned_variants:
                for strategy in selected_defense_strategies:
                    for num_nodes in num_clean_nodes_list:
                        nodes_to_use = [compromised_node] + [i for i in range(2, 7)][:num_nodes]  # Select clean nodes from 2 to 6
                        if current_node in nodes_to_use:
                            poisoned_data = poisoned_variant if current_node == compromised_node else None
                            log_file = f"log_node{current_node}_dataset{dataset}_poisoned{poisoned_data}_strategy{strategy}_clean{num_nodes}.txt"
                            run_client(current_node, dataset, poisoned_data, strategy, log_file)

if __name__ == "__main__":
    main()

#exmaple usage
#python3 experimentAutomation3.py --datasets IOTBOTNET CICIOT --role client --node 1 --pvar LF33 LF66 FN33 FN66 --defense_strat none --cleannodes 1 2 4

