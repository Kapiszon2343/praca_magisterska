from utils import *
import time
import json
import os
import multiprocessing
import pathlib

def __res_path(rule_name, election_name):
    return pathlib.Path("./election_results/" + rule_name + "/" + election_name + ".json")

def __recalculate_election(election_name, rule_id):
    (name, use_cost, rule) = rules[rule_id]
    try:
        (instance, profile) = read_pb("./instances_all/" + election_name + ".pb",
                                        use_cost, use_cost, use_cost)
    except TypeError as e:
        return
    print(f'{election_name} {name}\n  started at: {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}')
    start_time = time.time()
    res = rule(instance=instance, profile=profile)
    print(f'{election_name} {name}\n  finished at: {time.localtime().tm_hour}:{time.localtime().tm_min}:{time.localtime().tm_sec}\n  runtime: {time.time() - start_time}')
    res = [str(x).replace("'", '"') for x in res]

    with __res_path(name, election_name).open('w', encoding=encoding) as f:
        json.dump(res, f, indent=2)

def __calculate_election(election_name, rule_id, force_recalculate=False):
    if force_recalculate:
        __recalculate_election(election_name, rule_id)
        return
    (name, use_cost, rule) = rules[rule_id]
    if __res_path(name, election_name).exists():
        with __res_path(name, election_name).open('r', encoding=encoding) as f:
            try:
                arr = json.load(f)
                if not arr:
                    __recalculate_election(election_name, rule_id)
            except ValueError as e:
                __recalculate_election(election_name, rule_id)
        return
    else:
        __recalculate_election(election_name, rule_id)
        return


if __name__ == '__main__':
    force_recalculate = False
    instances_path = pathlib.Path('./instances_all')
    instaces_names = [p.stem for p in list(instances_path.glob('*.pb'))]
    pool = multiprocessing.Pool(12)
    args = []
    for instance_name in instaces_names:
        for rule_id in range(len(rules)):
            args.append((instance_name, rule_id ,force_recalculate))
    pool.starmap(__calculate_election, args, chunksize=1)
