from utils import *
import os

election_names = [
    'poland_katowice_2023_',
    'poland_czestochowa_2024_',
    'poland_warszawa_2024_',
    'poland_lodz_2023_',
]

def cstv_short(combination):
    def tmp(instance, profile):
        return cstv(instance=instance, profile=profile, combination=combination)
    return tmp

rules = [
    ('GE score', False, greedy_e),
    ('GSC score', False, greedy_sc),
    ('GS score', False, greedy_s),
    ('EWT score', False, cstv_short(CSTV_Combination.EWT)),
    ('EWTC score', False, cstv_short(CSTV_Combination.EWTC)),
    ('EWTS score', False, cstv_short(CSTV_Combination.EWTS)),
    ('MT score', False, cstv_short(CSTV_Combination.MT)),
    ('MTC score', False, cstv_short(CSTV_Combination.MTC)),
    ('MTS score', False, cstv_short(CSTV_Combination.MTS)),
    ('GE', True, greedy_e),
    ('GSC', True, greedy_sc),
    ('GS', True, greedy_s),
    ('EWT', True, cstv_short(CSTV_Combination.EWT)),
    ('EWTC', True, cstv_short(CSTV_Combination.EWTC)),
    ('EWTS', True, cstv_short(CSTV_Combination.EWTS)),
    ('MT', True, cstv_short(CSTV_Combination.MT)),
    ('MTC', True, cstv_short(CSTV_Combination.MTC)),
    ('MTS', True, cstv_short(CSTV_Combination.MTS)),
]
for election_name in election_names:
    with open("./full_results/" + election_name + "X.txt", 'w') as f:
        first_line = True
        f.write('{')
        for (name, use_cost, rule) in rules:
            (instance, profile) = read_pb("./original_elections/" + election_name + ".pb",
                                          use_cost, use_cost, use_cost)
            ids = dict()
            match profile[0]:
                case pabutools.election.ballot.ApprovalBallot():
                    is_cumulative = False
                case _:
                    is_cumulative = True
            for idx, ballot in enumerate(profile):
                ids[ballot.meta['voter_id']] = idx
            dist_names = os.listdir('./original_districts/' + election_name)
            for d_name in dist_names:
                (d_instance, d_profile) = read_pb("./original_districts/" + election_name + "/" + d_name,
                                                  use_cost, use_cost, use_cost)
                instance = instance.union(d_instance)
                instance.budget_limit += d_instance.budget_limit
                for ballot in d_profile:
                    if ballot.meta['voter_id'] in ids:
                        profile[ids[ballot.meta['voter_id']]] |= ballot
                    else:
                        ids[ballot.meta['voter_id']] = len(profile)
                        profile.append(ballot)
            (instance, profile) = balance_profile(instance=instance, profile=profile)
            res = rule(instance=instance, profile=profile)
            print(f'{name} result: {res}')
            res = str([str(x).replace("'", '"') for x in res]).replace("'", '"')
            if first_line:
                f.write(f'\n\"{name}\": {res}')
                first_line = False
            else:
                f.write(f',\n\"{name}\": {res}')
        f.write('\n}\n') 