from utils import *
import os

election_names = [
    'poland_czestochowa_2020_',
    'poland_czestochowa_2024_',
    'poland_gdynia_2020_',
    'poland_katowice_2023_',
    'poland_lodz_2020_',
    'poland_lodz_2022_',
    'poland_lodz_2023_',
    'poland_warszawa_2024_',

]

def cstv_short(combination):
    def tmp(instance, profile):
        return cstv(instance=instance, profile=profile, combination=combination, verbose=False)
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
    with open("./district_results/" + election_name + "X.txt", 'w') as f:
        first_line = True
        f.write('{')
        for (name, use_cost, rule) in rules:
            dist_names = os.listdir('./original_districts/' + election_name)
            d_instance = []
            d_profile = []
            res = set()
            for d_name in dist_names:
                (instance, profile) = read_pb("./original_districts/" + election_name + "/" + d_name,
                                              use_cost, use_cost, use_cost)
                alloc = rule(instance=instance, profile=profile)
                res = res.union(alloc)
                print(f'{name}, {d_name} done')
            (instance, profile) = read_pb("./original_elections/" + election_name + ".pb",
                                              use_cost, use_cost, use_cost)
            alloc = rule(instance=instance, profile=profile)
            res = res.union(alloc)
            print(f'{name} result: {res}')
            res = str([str(x).replace("'", '"') for x in res]).replace("'", '"')
            if first_line:
                f.write(f'\n\"{name}\": {res}')
                first_line = False
            else:
                f.write(f',\n\"{name}\": {res}')
        f.write('\n}\n') 