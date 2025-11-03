import pabutools

def project_ballot_support(ballot, project, use_cost = False):
    """
        get support given by ballot to project
        
        Args:
            ballot (Ballot): ballot making votes
            project (Project): project being voted on
            use_cost (bool): Should votes be multiplied by project cost
            
        Returns:
            float: support
    """
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
            case _:
                raise TypeError('type ' + type(ballot).__name__ + ' is incorrect')
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
            case _:
                raise TypeError('type ' + type(ballot).__name__ + ' is incorrect')

def single_utility(ballot, instance, use_cost = True):
    """
        get support given by ballot to set of projectc
        
        Args:
            ballot (Ballot): ballot making votes
            instance (iterable(Project)): set of projects being voted on
            use_cost (bool): Should votes be multiplied by project cost
            
        Returns:
            float: support
    """
    return sum([project_ballot_support(ballot, project, use_cost) for project in instance])

def avg_utility(instances, profiles, alloc, use_cost = True):
    """
        Calculate combined utility of list of elections
        
        Args:
            instances ([Instance]): list of instances of election
            profiles ([Profile]): list of profile of election
            alloc (set(Project)): set of projects chosen from the elections
            use_cost (bool): Should the cost or score utility be used
            
        Returns:
            float: utility
    """
    sum_u = 0
    max_u = 0
    for ii in range(len(instances)):
        instance = instances[ii]
        profile = profiles[ii]
        trimmed_alloc = [p for p in instance if p in alloc]
        single_u = 0
        single_max_u = 0
        for ballot in profile:
            single_u += single_utility(ballot, trimmed_alloc, use_cost)
            single_max_u += single_utility(ballot, instance, use_cost)
        sum_u += single_u
        max_u += single_max_u
    return sum_u / max_u

def dominance_margin(instance, profile, alloc1, alloc2, use_cost = True):
    """
        Calculate dominance margin of set of projects over other set of projects
        
        Args:
            instances (Instance): instances of election used
            profiles ([Profile]): profile of election used
            alloc1 (set(Project)): set of projects dominating alloc2
            alloc2 (set(Project)): set of projects being dominated
            use_cost (bool): Should the cost or score utility be used internally
            
        Returns:
            float: dominance margin
    """
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

def improvement_margins(instances, profiles, alloc1, alloc2, use_cost = True):
    """
        Calculate improvement margin of set of projects over other set of projects
        
        Args:
            instances ([Instance]): list of instances of election
            profiles ([Profile]): list of profile of election
            alloc1 (set(Project)): set of projects comparing to alloc2
            alloc2 (set(Project)): set of projects being compared to
            use_cost (bool): Should the cost or scre utility be used
            
        Returns:
            float: improvement margin
    """
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
    """
        Calculate combined exclusion ratio of list of elections
        
        Args:
            instances ([Instance]): list of instances of election
            profiles ([Profile]): list of profile of election
            alloc (set(Project)): set of projects chosen from the elections
            use_cost (bool): Should the cost or scre utility be used
            
        Returns:
            float: exclusion ratio
    """
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
    """
        Calculate combined power inequality of list of elections
        
        Args:
            instances ([Instance]): list of instances of election
            profiles ([Profile]): list of profile of election
            alloc (set(Project)): set of projects chosen from the elections
            use_cost (bool): Should the cost or scre utility be used
            
        Returns:
            float: power inequality
    """
    shares = []
    for idx, profile in enumerate(profiles):
        arr = []
        for project in alloc:
            pr_sum = 0.0
            for ballot in profile:
                pr_sum += project_ballot_support(project=project, ballot=ballot, use_cost=False)
            if pr_sum > 0:    
                arr.append((project, pr_sum))
        for ballot in profile:
            share = 0.0
            for (project, pr_sum) in arr:
                if pr_sum > 0:
                    share += \
                        float(project_ballot_support(project=project, ballot=ballot, use_cost=True)) \
                        / pr_sum
            shares.append(share)

    m = sum(shares) / len(shares)
    ineq = 0.0
    for share in shares:
        ineq += (share/m - 1.0)**2
    return ineq / len(shares)

class Election:
    def __init__(self, profile, budget):
        self.profile = profile
        self.budget = budget

def ejr_plus_violations(elections, outcome, up_to_one = True):
    """
        Calculate combined EJR of list of elections
        
        Args:
            elections ([Election]): list of elections
            outcome (set(Project)): set of projects chosen from the elections
            up_to_one (bool): Should the EJR be calculated up to one
            
        Returns:
            [Project]: list of EJR violations
    """
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