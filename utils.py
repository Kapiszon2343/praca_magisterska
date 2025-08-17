import pabutools.fractions
import pabutools

pabutools.fractions.FRACTION = "float"

from cstv2 import *

encoding="utf-8-sig"

all_election_names = [
    'poland_katowice_2023_',
    'poland_czestochowa_2024_',
    'poland_warszawa_2024_',
    'poland_lodz_2023_',
    'france_toulouse_2019_',
    'poland_czestochowa_2020_',
    'poland_gdansk_2020_',
    'switzerland_zurich_d5_',
    'switzerland_zurich_d10_',
    'switzerland_zurich_s5d10_',
    'worldwide_mechanical-turk_utilities-3_',
    'worldwide_mechanical-turk_utilities-6_',
    'worldwide_mechanical-turk_utilities-7_',
    'worldwide_mechanical-turk_utilities-8_',
]

good_election_names = [
    'poland_katowice_2023_',
    'poland_czestochowa_2024_',
    'poland_warszawa_2024_',
    'poland_lodz_2023_',
]

def balance_profile(instance, 
                    profile,
                    adjust_cumulative_to_costs = False, 
                    adjust_cardinal_to_costs = False, 
                    adjust_approval_to_costs = True
                    ):

    budget_per_ballot = instance.budget_limit / len(profile)
    ballots = []
    empty_ballot_dict = {}
    for project in instance:
        empty_ballot_dict[project] = 0
    for ballot in profile:
        b = empty_ballot_dict.copy()
        match ballot:
            case pabutools.election.ballot.CumulativeBallot():
                if adjust_cumulative_to_costs:
                    val = budget_per_ballot / sum(votes * project.cost for project, votes in ballot.items())
                    for project, votes in ballot.items():
                        b[project] = val * votes * project.cost
                else:
                    val = budget_per_ballot / sum(ballot.values())
                    for project, votes in ballot.items():
                        b[project] = val * votes
            case pabutools.election.ballot.CardinalBallot():
                if adjust_cardinal_to_costs:
                    val = budget_per_ballot / sum(votes * project.cost for project, votes in ballot.items())
                    for project, votes in ballot.items():
                        b[project] = val * votes * project.cost
                else:
                    val = budget_per_ballot / sum(ballot.values())
                    for project, votes in ballot.items():
                        b[project] = val * votes
            case pabutools.election.ballot.ApprovalBallot():
                if adjust_approval_to_costs:
                    val = budget_per_ballot / sum(project.cost for project in ballot)
                    for project in ballot:
                        b[project] = val * project.cost
                else:
                    val = budget_per_ballot / len(ballot)
                    for project in ballot:
                        b[project] = val

                
        b = pabutools.election.ballot.CumulativeBallot(b)
        b.meta = ballot.meta
        ballots.append(b)

    profile = pabutools.election.profile.CumulativeProfile(ballots)
    return (instance, profile)

def read_path(path):
    f = open(path, 'r', encoding=encoding)
    (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())
    f.close()

    return (instance, profile)

def read_pb(path, 
            adjust_cumulative_to_costs = False, 
            adjust_cardinal_to_costs = False, 
            adjust_approval_to_costs = True
            ):
    (instance, profile) = read_path(path)

    return balance_profile(
        instance,
        profile,
        adjust_cumulative_to_costs,
        adjust_cardinal_to_costs,
        adjust_approval_to_costs
        )

def greedy_s(instance, profile):
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = sum(sum(donor.values()) for donor in donations)
    while len(remaining_projects) > 0:
        tied_projects = select_project_gs(remaining_projects, donations)
        if not tied_projects:
            return selected_projects
        if len(tied_projects) < 1:
            return selected_projects
        project = tied_projects[0]
        if project.cost <= budget:
            selected_projects.add(project)
            budget -= project.cost
        remaining_projects.remove(project)
    return selected_projects

def greedy_sc(instance, profile):
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = sum(sum(donor.values()) for donor in donations)
    while len(remaining_projects) > 0:
        tied_projects = select_project_gsc(remaining_projects, donations)
        if not tied_projects:
            return selected_projects
        if len(tied_projects) < 1:
            return selected_projects
        project = tied_projects[0]
        if project.cost <= budget:
            selected_projects.add(project)
            budget -= project.cost
        remaining_projects.remove(project)
    return selected_projects

def greedy_e(instance, profile):
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = sum(sum(donor.values()) for donor in donations)
    while len(remaining_projects) > 0:
        tied_projects = select_project_ge(remaining_projects, donations)
        if not tied_projects:
            return selected_projects
        if len(tied_projects) < 1:
            return selected_projects
        project = tied_projects[0]
        if project.cost <= budget:
            selected_projects.add(project)
            budget -= project.cost
        remaining_projects.remove(project)
    return selected_projects