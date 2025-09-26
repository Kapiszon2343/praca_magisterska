import pabutools
import json
from pabutools.analysis.votersatisfaction import *
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import os

from analisis import *

#election_names = all_election_names
#'''
district_names = [
    'poland_katowice_2023_',
    'poland_czestochowa_2020_',
    'poland_czestochowa_2024_',
    'poland_lodz_2020_',
    'poland_lodz_2022_',
    'poland_lodz_2023_',
    'poland_warszawa_2024_',
    'poland_gdynia_2020_',

]

election_names = [
    'france_toulouse_2019_',
    'poland_czestochowa_2020_',
    'poland_czestochowa_2024_',
    'poland_gdansk_2020_',
    'poland_gdynia_2020_',
    'poland_katowice_2022_',
    'poland_katowice_2023_',
    'poland_warszawa_2024_',
    'poland_lodz_2020_',
    'poland_lodz_2022_',
    'poland_lodz_2023_',
    'poland_swiecie_2023_',
    'poland_warszawa_2023_',
    'poland_warszawa_2024_',
    'poland_wroclaw_2016_',
    'poland_wroclaw_2017_',
    'poland_wroclaw_2018_',
    'switzerland_zurich_d5_',
    'switzerland_zurich_d10_',
    'switzerland_zurich_s5d10_',
    'worldwide_mechanical-turk_utilities-3_',
    'worldwide_mechanical-turk_utilities-6_',
    'worldwide_mechanical-turk_utilities-7_',
    'worldwide_mechanical-turk_utilities-8_',
]

# '''
colors = ['gold', 'khaki', 'goldenrod', 'rosybrown', 'salmon', 'indianred', 'palegreen', 'mediumseagreen', 'turquoise']
alloc_names = ['GE', 'GSC', 'GS', 'EWT', 'EWTC', 'EWTS', 'MT', 'MTC', 'MTS']
election_categories = ['group_results']
measure_names = ['utility cost score', 'power inequality', 'improvement margin', 'ejr', 'exclusion ratio', 'utility score']
#measure_id = 5
group_id = -1
labels = ['cumulative single', 'cummulative districts', 'approval single', 'approval districts']
for measure_id in [1]:
    measure = []
    for _ in range(len(alloc_names)):
        measure.append([[],[],[],[]])
    fig = plt.subplots(figsize=(12, 8))
    for fol in election_categories:
        for election_name in election_names:
            if election_name in district_names:
                f = open('./district_results/' + election_name + '.txt', 'r', encoding=encoding)
            else:
                f = open('./election_results/' + election_name + '.txt', 'r', encoding=encoding)
            data = f.read()
            allocation = json.loads(data)
            f.close()

            f = open('./original_elections/' + election_name + '.pb', 'r', encoding=encoding)
            (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())
            f.close()
            instances = [instance]
            profiles = [profile]
            match profile[0]:
                case pabutools.election.ballot.CumulativeBallot():
                    group_id = 0
                case _:
                    group_id = 2
            if election_name in district_names:
                group_id += 1
                dist_names = os.listdir('./original_districts/' + election_name)
                for d_name in dist_names:
                    f = open("./original_districts/" + election_name + "/" + d_name, 'r', encoding=encoding)
                    (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())
                    f.close()
                    instances.append(instance)
                    profiles.append(profile)
            i = 0
            allocG = [[], [], []]
            for alloc_name, alloc in allocation.items():
                alloc2 = []
                for pr_name in allocation[alloc_name]:
                    do_break = False
                    for instance in instances:
                        for project in instance:
                            if str(project.name) == str(pr_name):
                                alloc2.append(project)
                                do_break = True
                                break
                        if do_break:
                            break
                if i < 3:
                    allocG[i] = alloc
                match measure_id:
                    case 0:
                        measure[i][group_id].append(avg_utility(instances, profiles, alloc2, use_cost=True))
                    case 1:
                        meas = power_inequality(instances, profiles, alloc2)
                        if meas < 10:
                            measure[i][group_id].append(meas)
                        else:
                            print('Outlier in power inequality: ', election_name, ' with ', meas)
                    case 2:
                        measure[i][group_id].append(improvement_margins(instances, profiles, alloc2, allocG[i%3]))
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
                                                election[p][h] = u
                                                sm += u
                                    case pabutools.election.ballot.ApprovalBallot():
                                        for p in profile[h]:
                                            if p not in election:
                                                election[p] = dict()
                                            election[p][h] = 1
                                            sm += 1
                                total_u += sm
                            elections.append(Election(election, instance.budget_limit))
                        ejr_val = ejr_plus_violations(elections, alloc2)
                        # measure[i].append(len(ejr_val) / len(instance))
                        # print(f'{election_name} + {alloc_name} EJR: {ejr_val}')
                        ejr_sum = 0
                        for project in ejr_val:
                            for election in elections:
                                if project in election.profile:
                                    ejr_sum += sum(election.profile[project].values())
                        #print(f'{election_name} + {alloc_name} EJR: {ejr_sum} / {instance.budget_limit}')
                        measure[i][group_id].append(ejr_sum / total_u)
                    case 4:
                        measure[i][group_id].append(exclusion_ratio(instances, profiles, alloc2))
                    case 5:
                        measure[i][group_id].append(avg_utility(instances, profiles, alloc2, use_cost=False))
                i += 1

    br_n = len(alloc_names)
    barWidth = 1 / (br_n+1)
    br = [np.arange(len(measure[0]))]
    for i in range(br_n-1):
        br.append([x+barWidth for x in br[i]])

    for i in range(br_n):
        #plt.boxplot(br[i], measure[i], color=colors[i], width=barWidth, edgecolor='grey', label='avg ut')
        bp = plt.boxplot(measure[i], widths=barWidth, positions=br[i], patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor(colors[i])


    #plt.xlabel('czestochowa 2020')
    plt.ylabel(measure_names[measure_id])
    plt.xticks(br[br_n//2], labels)

    artists = [Patch(facecolor=color, edgecolor='grey') for color in colors]
    plt.legend(artists, alloc_names)
    plt.savefig(f'plots_group/{measure_names[measure_id]}.png')

    with open(f'plots_group/{measure_names[measure_id]}.txt', "w") as f:
        for idx, res in enumerate(measure):
            f.write(f":{alloc_names[idx]} {res}\n")
