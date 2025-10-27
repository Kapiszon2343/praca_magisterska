import pabutools
import json
import statistics
from pabutools.analysis.votersatisfaction import *
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from analisis import *

#election_names = all_election_names
#'''
election_names = [
    'france_toulouse_2019_',
    'poland_czestochowa_2020_',
    'poland_czestochowa_2024_',
    'poland_gdansk_2020_',
    'poland_gdynia_2020_',
    'poland_katowice_2022_',
    'poland_katowice_2023_',
    'poland_katowice_2024_',
    #'poland_warszawa_2024_',
    #'poland_lodz_2020_',
    #'poland_lodz_2022_',
    #'poland_lodz_2023_',
    #'poland_swiecie_2023_',
    #'poland_warszawa_2023_',
    #'poland_warszawa_2024_',
    #'poland_wroclaw_2016_',
    #'poland_wroclaw_2017_',
    #'poland_wroclaw_2018_',
    #'switzerland_zurich_d5_',
    #'switzerland_zurich_d10_',
    #'switzerland_zurich_s5d10_',
    #'worldwide_mechanical-turk_utilities-3_',
    #'worldwide_mechanical-turk_utilities-6_',
    #'worldwide_mechanical-turk_utilities-7_',
    #'worldwide_mechanical-turk_utilities-8_',
    ]
# '''
colors = ['gold', 'khaki', 'goldenrod', 'rosybrown', 'salmon', 'indianred', 'palegreen', 'mediumseagreen', 'turquoise']
alloc_names = ['GE', 'GSC', 'GS', 'EWT', 'EWTC', 'EWTS', 'MT', 'MTC', 'MTS']
election_categories = ['election_results', 'district_results']
measure_names = ['utility cost score', 'power inequality', 'improvement margin', 'ejr', 'exclusion ratio']
for measure_id in [0, 1, 2, 3, 4]:
    labels = []
    measure = []
    for _ in range(len(alloc_names)):
        measure.append([])
    fig = plt.subplots(figsize=(12, 8))
    for fol in election_categories[0:1]:
        for election_name in election_names:
            labels.append(election_name.replace('_', ' ').strip())
            f = open('./' + fol + '/' + election_name + '.txt', 'r', encoding=encoding)
            data = f.read()
            allocation = json.loads(data)
            f.close()

            f = open('./original_elections/' + election_name + '.pb', 'r', encoding=encoding)
            (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())
            f.close()

            i = 0
            allocG = [[], [], []]
            for alloc_name_tmp in alloc_names:
                alloc_name = alloc_name_tmp + ' score'
                alloc2 = []
                for pr_name in allocation[alloc_name]:
                    for project in instance:
                        if str(project.name) == str(pr_name):
                            alloc2.append(project)
                            break
                if i < 3:
                    allocG[i] = allocation[alloc_name]
                instances = [instance]
                profiles = [profile]
                match measure_id:
                    case 0:
                        measure[i].append(avg_utility(instances, profiles, alloc2, use_cost=True))
                    case 1:
                        measure[i].append(power_inequality(instances, profiles, alloc2))
                    case 2:
                        measure[i].append(improvement_margins(instances, profiles, alloc2, allocG[i%3]))
                    case 3:
                        elections = []
                        total_u = 0
                        for ii in range(len(instances)):
                            instance = instances[ii]
                            profile = profiles[ii]
                            election = dict()
                            for h in range(len(profile)):
                                sm = 0
                                match profile[h]:
                                    case pabutools.election.ballot.CumulativeBallot():
                                        for p, u in profile[h].items():
                                            if u > 0:
                                                if p not in election:
                                                    election[p] = dict()
                                                election[p][h] = u * p.cost
                                                sm += u * p.cost
                                    case pabutools.election.ballot.ApprovalBallot():
                                        for p in profile[h]:
                                            if p not in election:
                                                election[p] = dict()
                                            election[p][h] = p.cost
                                            sm += p.cost
                                total_u += sm
                            elections.append(Election(election, instance.budget_limit))
                        ejr_val = ejr_plus_violations(elections, alloc2)
                        print(f'{election_name} + {alloc_name} EJR: {ejr_val}')
                        ejr_sum = 0
                        for project in ejr_val:
                            for election in elections:
                                if project in election.profile:
                                    ejr_sum += sum(election.profile[project].values())
                        #print(f'{election_name} + {alloc_name} EJR: {ejr_sum} / {instance.budget_limit}')
                        measure[i].append(ejr_sum / total_u)
                    case 4:
                            measure[i].append(exclusion_ratio(instances, profiles, alloc2))
                    case 5:
                        measure[i].append(avg_utility(instances, profiles, alloc2, use_cost=False))
                i += 1

    br_n = len(alloc_names)
    barWidth = 1 / (br_n+1)
    br = [np.arange(len(measure[0]))]
    for i in range(br_n-1):
        br.append([x+barWidth for x in br[i]])

    for i in range(br_n):
        plt.bar(br[i], measure[i], color=colors[i], width=barWidth,
                edgecolor='grey', label='avg ut')

    #plt.xlabel('czestochowa 2020')
    plt.ylabel(measure_names[measure_id])
    plt.xticks(br[br_n//2], labels)

    artists = [Patch(facecolor=color, edgecolor='grey') for color in colors]
    plt.legend(artists, alloc_names)
    plt.savefig(f'plots/{measure_names[measure_id]}.png')

    with open(f'plots/{measure_names[measure_id]}.txt', "w") as f:
        for idx, res in enumerate(measure):
            f.write(f":{alloc_names[idx]} {res}\n")
