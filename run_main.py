from utils import *
import time

election_names = [
    #'france_toulouse_2019_',
    #'poland_czestochowa_2020_',
    #'poland_czestochowa_2024_',
    #'poland_gdansk_2020_',
    #'poland_gdynia_2020_',
    #'poland_katowice_2022_',
    #'poland_katowice_2023_',
    'poland_katowice_2024_',
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

# election_names = all_election_names

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
    with open("./election_results/" + election_name + "X.txt", 'w') as f:
        first_line = True
        f.write('{')
        for (name, use_cost, rule) in rules:

            (instance, profile) = read_pb("./original_elections/" + election_name + ".pb",
                                          use_cost, use_cost, use_cost)
            start_time = time.time()
            res = rule(instance=instance, profile=profile)
            # print(f'{name} result: {res}')
            print(f'{name} runtime: {time.time() - start_time}')
            res = str([str(x).replace("'", '"') for x in res]).replace("'", '"')
            if first_line:
                f.write(f'\n\"{name}\": {res}')
                first_line = False
            else:
                f.write(f',\n\"{name}\": {res}')
        f.write('\n}\n') 