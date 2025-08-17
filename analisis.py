import pabutools
from pabutools.analysis.votersatisfaction import *
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from utils import *

def project_ballot_support(ballot, project, use_cost = False):
    if use_cost:
        match ballot:
            case pabutools.election.ballot.CumulativeBallot():
                return ballot.get(project, 0) * project.cost
            case pabutools.election.ballot.CardinalBallot():
                return ballot.get(project, 0) * project.cost
            case pabutools.election.ballot.ApprovalBallot():
                if project in ballot:
                    return project.cost
                else:
                    return 0
    else:
        match ballot:
            case pabutools.election.ballot.CumulativeBallot():
                return ballot.get(project, 0)
            case pabutools.election.ballot.CardinalBallot():
                return ballot.get(project, 0)
            case pabutools.election.ballot.ApprovalBallot():
                if project in ballot:
                    return 1
                else:
                    return 0

def single_utility(ballot, instance, use_cost = True):
    utility = 0
    for project in instance:
        utility += project_ballot_support(ballot, project, use_cost)
    return utility

def avg_utility(instances, profiles, alloc, use_cost = True):
    avg_u = 0
    max_u = 0
    for ii in range(len(instances)):
        instance = instances[ii]
        profile = profiles[ii]
        single_avg_u = 0
        single_max_u = 0
        for ballot in profile:        
            single_avg_u += single_utility(ballot, alloc, use_cost)
            single_max_u += single_utility(ballot, instance, use_cost)
        avg_u += single_avg_u
        max_u += single_max_u
    return avg_u / max_u

def dominance_margin(instance, profile, alloc1, alloc2, use_cost = False):
    margin1 = 0
    margin2 = 0
    for ballot in profile:
        utility1 = single_utility(ballot, alloc1, use_cost)
        utility2 = single_utility(ballot, alloc2, use_cost)
        if utility1 > utility2:
            margin1 += 1
        if utility2 > utility1:
            margin2 += 1
    return (margin1 / len(profile), margin2 / len(profile))

def improvement_margins(instances, profiles, alloc1, alloc2, use_cost = False):
    sum1 = 0
    sum2 = 0
    voters_count = 0
    for ii in range(len(instances)):
        profile = profiles[ii]
        voters_count += len(profile)
        margin1 = 0
        margin2 = 0
        for ballot in profile:
            utility1 = single_utility(ballot, alloc1, use_cost)
            utility2 = single_utility(ballot, alloc2, use_cost)
            if utility1 > utility2:
                margin1 += 1
            if utility2 > utility1:
                margin2 += 1
        sum1 += margin1
        sum2 += margin2
    return (sum1 - sum2) / voters_count

def exclusion_ratio(instances, profiles, alloc):
    exclusion = 0
    voter_count = 0
    for profile in profiles:
        for ballot in profile:
            supp = 1
            match ballot:
                case pabutools.election.ballot.CumulativeBallot():
                    for project in alloc:
                        if ballot.get(project, 0) > 0:
                            supp = 0
                            break
                case pabutools.election.ballot.CardinalBallot():
                    for project in alloc:
                        if ballot.get(project, 0) > 0:
                            supp = 0
                            break
                case pabutools.election.ballot.ApprovalBallot():
                    for project in alloc:
                        if project in ballot:                        
                            supp = 0
                            break
            exclusion += supp
        voter_count += len(profile)
        
    return exclusion / voter_count

def power_inequality(instances, profiles, alloc):
    sm = 0.
    voter_count = 0
    for ii in range(len(instances)):
        instance = instances[ii]
        profile = profiles[ii]
        voter_count += len(profile)
        n = len(profile)
        b = instance.budget_limit
        arr = []
        for project in alloc:
            pr_sum = 0
            for ballot in profile:
                pr_sum += project_ballot_support(project=project, ballot=ballot)
            arr.append((project, pr_sum))
        for ballot in profile:
            share = 0
            for (project, pr_sum) in arr:
                if pr_sum > 0:
                    share += \
                        project_ballot_support(project=project, ballot=ballot) \
                        / pr_sum * project.cost
            sm += abs(share - b/n) * n/b
    return sm / voter_count

class Election:
    def __init__(self, profile, budget):
        self.profile = profile
        self.budget = budget

def ejr_plus_violations(elections, outcome, up_to_one = True):
    utility = {}
    budget_limit = sum([e.budget for e in elections])
    for e in elections:
        for p in e.profile.keys():
            for v in e.profile[p].keys():
                utility[v] = 0

    for p in outcome:
        for e in elections:
            if p in e.profile.keys():
                for v in e.profile[p].keys():
                    utility[v] += e.profile[p][v]

    sorted_voters = sorted(utility.items(), key=lambda item : item[1])

    failures = []
    for e in elections:
        for not_elected in e.profile.keys():
            if not_elected in outcome:
                continue
            coalition_size = 0
            for vot, sat in sorted_voters:
                if vot in e.profile[not_elected].keys():
                    coalition_size += 1
                    if up_to_one:
                        ejr_satisfied = sat >= (coalition_size / len(sorted_voters)) * budget_limit - not_elected.cost
                    else:
                        ejr_satisfied = sat >= (coalition_size / len(sorted_voters)) * budget_limit
                    if not ejr_satisfied:
                        failures.append(not_elected.name)
                        break
    return failures