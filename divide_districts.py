import pabutools
from utils import *
from pabutools.election.instance import Instance, Project
from pabutools.election import Instance, Project, CumulativeProfile, CumulativeBallot
from cstv2 import *

d_category_names = ['', 'neighborhood', 'district']
citywide_district_name = 'general'

def split_districts(instance, profile):
    d_profile = {citywide_district_name: []}
    d_name_profile = ''
    for name in d_category_names[1:]:
        for ballot in profile:
            if name in ballot.meta:
                d_name_profile = name
                break
    for ballot in profile:
        distr = ballot.meta[d_name_profile]
        d_profile[citywide_district_name].append(ballot)
        if distr in d_category_names:
            for key, val in ballot.items():
                ballot[key] = val * 0.2
        else:
            distr_ballot = CumulativeBallot(ballot)
            for key, val in ballot.items():
                distr_ballot[key] = val * 0.8
                ballot[key] = val * 0.2
            if distr in d_profile:
                d_profile[distr].append(distr_ballot)
            else:
                d_profile[distr] = [distr_ballot]

    d_profile = {distr: CumulativeProfile(ballots) for distr, ballots in d_profile.items()}
    return d_profile



election_names = [
    'poland_czestochowa_2020_', 
    'poland_czestochowa_2024_',
    'poland_katowice_2023_',
    'poland_warszawa_2023_',
    ]

rules = [
    ('GE', greedy_e),
    ('GSC', greedy_sc),
    ('GS', greedy_s),
    #('EWT', cstv_short(CSTV_Combination.EWT)),
    #('EWTC', cstv_short(CSTV_Combination.EWTC)),
    #('EWTS', cstv_short(CSTV_Combination.EWTS)),
    #('MT', cstv_short(CSTV_Combination.MT)),
    #('MTC', cstv_short(CSTV_Combination.MTC)),
    #('MTS', cstv_short(CSTV_Combination.MTS)),
]
for election_name in election_names:
    with open("./election_results_d/" + election_name + "X.txt", 'w', encoding=encoding) as f:
        print(f"Running {election_name}")
        first_line = True
        f.write('{')
        (instance, profile) = read_pb("./original_elections/" + election_name + ".pb")
        split_profiles = split_districts(instance, profile)
        for (name, rule) in rules:
            res = set()
            for distr in split_profiles.keys():
                res_d = rule(instance=instance, profile=split_profiles[distr])
                print(f'{name} in {distr} result: {res_d}')
                for project in res_d: 
                    res.add(str(project).replace("'", '"'))
            if first_line:
                f.write(f'\n\t\"{name}\": {res}')
                first_line = False
            else:
                f.write(f',\n\t\"{name}\": {res}')
        f.write('\n}\n')
