import pabutools

from pabutools.rules.cstv import (
    cstv, 
    select_project_gs, 
    select_project_gsc, 
    select_project_ge, 
    CSTV_Combination
)

# Configuration
pabutools.fractions.FRACTION = "float"

ENCODING="utf-8-sig"

SAMPLE_ELECTION_NAMES = [
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

MINIMAL_SAMPLE_ELECTION_NAMES = [
    'poland_katowice_2023_',
    'poland_czestochowa_2024_',
    'poland_swiecie_2023_',
    'poland_warszawa_2024_',
]


def balance_profile(instance, 
                    profile,
                    adjust_cumulative_to_costs = False, 
                    adjust_cardinal_to_costs = False, 
                    adjust_approval_to_costs = False
                    ):
    """
        Turns profile to a cumulative one and adjusts its votes to make them equal to amount of value from budget assosiated with them
        
        Args:
            instance (pabutools.election.instance.Instance): election instance
            profile (pabutools.election.profile.cumulativeprofile.CumulativeProfile): election profile
            adjust_cumulative_to_costs (bool): Scale cumulative ballots by project costs.
            adjust_cardinal_to_costs (bool): Scale cardinal ballots by project costs.
            adjust_approval_to_costs (bool): Scale approval ballots by project costs.
            
        Returns:
            tuple: (instance, balanced_profile)
    """
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
            case _:
                raise TypeError

                
        b = pabutools.election.ballot.CumulativeBallot(b)
        b.meta = ballot.meta
        ballots.append(b)

    profile = pabutools.election.profile.CumulativeProfile(ballots)
    return (instance, profile)

def read_path(path):
    """
        Reads election and returns adjusted election
        
        Args:
            path (str): path to election file 
            
        Returns:
            tuple: (Instance, Profile)
    """
    with open(path, 'r', encoding=ENCODING) as f:
        (instance, profile) = pabutools.election.pabulib.parse_pabulib_from_string(f.read())

    return (instance, profile)

def read_pb(path, 
            adjust_cumulative_to_costs = False, 
            adjust_cardinal_to_costs = False, 
            adjust_approval_to_costs = False
            ):
    """
        Reads election and returns adjusted cumulative election ready to be run by cstv
        
        Args:
            path (str): path to election file 
            adjust_cumulative_to_costs (bool): Scale cumulative ballots by project costs.
            adjust_cardinal_to_costs (bool): Scale cardinal ballots by project costs.
            adjust_approval_to_costs (bool): Scale approval ballots by project costs.
            
        Returns:
            tuple: (Instance, Profile)
    """
    (instance, profile) = read_path(path)

    return balance_profile(
        instance,
        profile,
        adjust_cumulative_to_costs,
        adjust_cardinal_to_costs,
        adjust_approval_to_costs
        )

def greedy_s(instance, profile):
    """
        Calculates set of projects to fill election budget based on greedy by support rule
        
        Args:
            instance (Instance): instance of election to be used
            profile (Profile): profile of election to be used
            
        Returns:
            tuple: set(Project)
    """
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = instance.budget_limit
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
    """
        Calculates set of projects to fill election budget based on greedy by support over cost rule
        
        Args:
            instance (Instance): instance of election to be used
            profile (Profile): profile of election to be used
            
        Returns:
            set(Project)
    """
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = instance.budget_limit
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
    """
        Calculates set of projects to fill election budget based on greedy by excess rule
        
        Args:
            instance (Instance): instance of election to be used
            profile (Profile): profile of election to be used
            
        Returns:
            set(Project)
    """
    remaining_projects = set(instance)
    selected_projects = set()
    donations = [
        {p: ballot[p] * profile.multiplicity(ballot) for p in instance}
        for ballot in profile
    ]
    budget = instance.budget_limit
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

def __cstv_short(combination):
    """
        Creaters shorter version cstv function with combination already chosen
        
        Args:
            combination (CSTV_Combination): version of cstv to use
            
        Returns:
            function: (instance, profile) -> set(Project)
    """
    def tmp(instance, profile):
        return cstv(instance=instance, profile=profile, combination=combination, verbose=False)
    return tmp

rules = [
        ('GE score', False, greedy_e),
        ('GSC score', False, greedy_sc),
        ('GS score', False, greedy_s),
        ('EWT score', False, __cstv_short(CSTV_Combination.EWT)),
        ('EWTC score', False, __cstv_short(CSTV_Combination.EWTC)),
        ('EWTS score', False, __cstv_short(CSTV_Combination.EWTS)),
        ('MT score', False, __cstv_short(CSTV_Combination.MT)),
        ('MTC score', False, __cstv_short(CSTV_Combination.MTC)),
        ('MTS score', False, __cstv_short(CSTV_Combination.MTS)),
        ('GE', True, greedy_e),
        ('GSC', True, greedy_sc),
        ('GS', True, greedy_s),
        ('EWT', True, __cstv_short(CSTV_Combination.EWT)),
        ('EWTC', True, __cstv_short(CSTV_Combination.EWTC)),
        ('EWTS', True, __cstv_short(CSTV_Combination.EWTS)),
        ('MT', True, __cstv_short(CSTV_Combination.MT)),
        ('MTC', True, __cstv_short(CSTV_Combination.MTC)),
        ('MTS', True, __cstv_short(CSTV_Combination.MTS)),
    ]