import json
import multiprocessing
import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pabutools
from matplotlib.patches import Patch

from analisis import avg_utility, power_inequality, improvement_margins, Election, ejr_plus_violations, exclusion_ratio
from utils import ENCODING


def visualize(measure_id):
    """
        Calculate metric using all results in ./election_results and save it as a graph
        
        Args:
            measure_id (id): which metric should be calculated
            
        Returns:
            None
    """

    colors = [
        'gold', 
        'khaki', 
        'goldenrod', 
        'rosybrown', 
        'salmon', 
        'indianred', 
        'palegreen', 
        'mediumseagreen', 
        'turquoise'
    ]
    results_names = [
        'GE', 
        'GSC', 
        'GS', 
        'EWT', 
        'EWTC', 
        'EWTS', 
        'MT', 
        'MTC', 
        'MTS'
    ]
    measure_names = [
        'utility cost score', 
        'power inequality', 
        'improvement margin', 
        'ejr', 
        'exclusion ratio', 
        'utility score', 
        'ejr scaled'
    ]
    group_id = -1
    labels = [
        'cumulative small', 
        'cummulative large', 
        'approval small', 
        'approval large'
    ]
    print(f'Starting {measure_names[measure_id]}')
    measure = []
    for _ in range(len(results_names)):
        emp = [[] for _ in labels]
        measure.append(emp)
    for instance_path in pathlib.Path('../instances_all').glob('*.pb'):
        with instance_path.open(encoding=ENCODING) as f:
            (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())
        instances = [instance]
        profiles = [profile]
        match profile[0]:
            case pabutools.election.ballot.CumulativeBallot():
                group_id = 0
            case pabutools.election.ballot.CardinalBallot():
                group_id = 0
            case pabutools.election.ballot.ApprovalBallot():
                group_id = 2
            case _:
                group_id = 69
                continue
        project_count = 0
        for instance in instances:
            project_count += len(instance)
        if project_count >= 50:
            group_id += 1
        i = 0
        allocG = [[], [], []]
        for results_name in results_names:
            results_path = pathlib.Path('..').joinpath('election_results')
            results_path = results_path.joinpath(results_name)
            results_path = results_path.joinpath(instance_path.stem + '.json')
            with results_path.open(encoding=ENCODING) as f:
                results_strings = json.load(f)
            results = []
            for pr_name in results_strings:
                for instance in instances:
                    for project in instance:
                        if str(project.name) == str(pr_name):
                            results.append(project)
            if i < 3:
                allocG[i] = results
            try:
                match measure_id:
                    case 0:
                        measure[i][group_id].append(avg_utility(instances, profiles, results, use_cost=True))
                    case 1:
                            meas = power_inequality(instances, profiles, results)
                            if meas > 200:
                                print(f'------ Instance {instance_path.name} - {results_name} for {measure_names[measure_id]} has power inequality of {meas}')
                            else:
                                measure[i][group_id].append(meas)
                    case 2:
                        measure[i][group_id].append(improvement_margins(instances, profiles, results, allocG[i%3]))
                    case 3:
                        elections = []
                        projects_n = 0
                        for ii in range(len(instances)):
                            instance = instances[ii]
                            profile = profiles[ii]
                            election = dict()
                            projects_n += len(instance)
                            for h in range(len(profile)):
                                match profile[h]:
                                    case pabutools.election.ballot.CumulativeBallot():
                                        for p, u in profile[h].items():
                                            if u > 0:
                                                if p not in election:
                                                    election[p] = dict()
                                                election[p][h] = u * p.cost
                                    case pabutools.election.ballot.ApprovalBallot():
                                        for p in profile[h]:
                                            if p not in election:
                                                election[p] = dict()
                                            election[p][h] = p.cost
                            elections.append(Election(election, instance.budget_limit))
                        measure[i][group_id].append(len(ejr_plus_violations(elections, results)))
                    case 4:
                        measure[i][group_id].append(exclusion_ratio(instances, profiles, results))
                    case 5:
                        measure[i][group_id].append(avg_utility(instances, profiles, results, use_cost=False))
                    case 6:
                        elections = []
                        projects_n = 0
                        for ii in range(len(instances)):
                            instance = instances[ii]
                            profile = profiles[ii]
                            election = dict()
                            projects_n += len(instance)
                            for h in range(len(profile)):
                                match profile[h]:
                                    case pabutools.election.ballot.CumulativeBallot():
                                        for p, u in profile[h].items():
                                            if u > 0:
                                                if p not in election:
                                                    election[p] = dict()
                                                election[p][h] = u * p.cost
                                    case pabutools.election.ballot.ApprovalBallot():
                                        for p in profile[h]:
                                            if p not in election:
                                                election[p] = dict()
                                            election[p][h] = p.cost
                            elections.append(Election(election, instance.budget_limit))
                        measure[i][group_id].append(len(ejr_plus_violations(elections, results)) / projects_n)
            except Exception as e:
                print(f'Instance {instance_path.name} - {results_name} for {measure_names[measure_id]}:\n  {e}')
            i += 1

    br_n = len(results_names)
    barWidth = 1 / (br_n+1)
    br = [np.arange(len(measure[0]))]
    for i in range(br_n-1):
        br.append([x+barWidth for x in br[i]])

    fig = plt.subplots(figsize=(12, 8))
    for i in range(br_n):
        bp = plt.boxplot(measure[i], widths=barWidth, positions=br[i], patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor(colors[i])

    plt.ylabel(measure_names[measure_id])
    plt.xticks(br[br_n//2], labels)

    artists = [Patch(facecolor=color, edgecolor='grey') for color in colors]
    plt.legend(artists, results_names)
    plt.savefig(f'plots_box/{measure_names[measure_id]}.png')

    fig = plt.subplots(figsize=(12, 8))
    for i in range(br_n):
        vp = plt.violinplot(measure[i], positions=br[i], widths=barWidth, showmeans=False, showmedians=True)
        for body in vp['bodies']:
            body.set_facecolor(colors[i])
            body.set_edgecolor('black')
            body.set_alpha(0.8)
    plt.ylabel(measure_names[measure_id])
    plt.xticks(br[br_n//2], labels)

    artists = [Patch(facecolor=color, edgecolor='grey') for color in colors]
    plt.legend(artists, results_names)
    plt.savefig(f'plots_violin/{measure_names[measure_id]}.png')

    with open(f'plots_box/{measure_names[measure_id]}.txt', "w") as f:
        for result_id, results in enumerate(measure):
            for group_id, res in enumerate(results):
                if len(res) > 0: 
                    f.write(f":{results_names[result_id]} - {labels[group_id]}:\n  mean: {sum(res)/len(res)}\n  min: {min(res)}\n  max: {max(res)}\n")
                else:
                    f.write(f":{results_names[result_id]} - {labels[group_id]}:\n  no results\n")

if __name__ == '__main__':
    processes = []
    measure_ids = [0, 1, 2, 3, 4, 5, 6]
    for measure_id in measure_ids:
        p = multiprocessing.Process(target=visualize, args=(measure_id,)) 
        p.start()
        processes.append(p)

    for p in processes:
        p.join()