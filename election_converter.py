
from natsort import natsorted
from copy import deepcopy

from pabutools.fractions import str_as_frac
from pabutools.election.instance import Instance, Project
from pabutools.election.ballot import (
    ApprovalBallot,
    CardinalBallot,
    OrdinalBallot,
    CumulativeBallot,
    AbstractCardinalBallot,
)
from pabutools.election.profile import (
    AbstractProfile,
    Profile,
    ApprovalProfile,
    AbstractApprovalProfile,
    CardinalProfile,
    AbstractCardinalProfile,
    CumulativeProfile,
    AbstractCumulativeProfile,
    OrdinalProfile,
    AbstractOrdinalProfile,
)

import urllib.request
import csv
import os
import pabutools

def convert_election(file_name):
    in_file_path = './original_elections/' + file_name
    out_file_path = './cumulative_elections/' + file_name

    with open(in_file_path, "r", newline="", encoding="utf-8-sig") as csvfile:
        file_content = csvfile.read()
        instance = Instance()
        ballots = []
        optional_sets = {"categories": set(), "targets": set()}

        lines = file_content.splitlines()
        section = ""
        header = []
        reader = csv.reader(lines, delimiter=";")
        for row in reader:
            if len(row) == 0 or (len(row) == 1 and len(row[0].strip()) == 0):
                continue
            if str(row[0]).strip().lower() in ["meta", "projects", "votes"]:
                section = str(row[0]).strip().lower()
                header = next(reader)
            elif section == "meta":
                instance.meta[row[0].strip()] = row[1].strip()
            elif section == "projects":
                p = Project()
                project_meta = dict()
                for i in range(len(row)):
                    key = header[i].strip()
                    p.name = row[0].strip()
                    if row[i].strip().lower() != "none":
                        if key in ["category", "categories"]:
                            project_meta["categories"] = {
                                entry.strip() for entry in row[i].split(",")
                            }
                            p.categories = set(project_meta["categories"])
                            optional_sets["categories"].update(project_meta["categories"])
                        elif key in ["target", "targets"]:
                            project_meta["targets"] = {
                                entry.strip() for entry in row[i].split(",")
                            }
                            p.targets = set(project_meta["targets"])
                            optional_sets["targets"].update(project_meta["targets"])
                        else:
                            project_meta[key] = row[i].strip()
                p.cost = str_as_frac(project_meta["cost"].replace(",", "."))
                instance.add(p)
                instance.project_meta[p] = project_meta
            elif section == "votes":
                ballot_meta = dict()
                for i in range(len(row)):
                    if row[i].strip().lower() != "none":
                        ballot_meta[header[i].strip()] = row[i].strip()
                vote_type = instance.meta["vote_type"]
                if vote_type == "approval":
                    ballot = ApprovalBallot()
                    for project_name in ballot_meta["vote"].split(","):
                        if project_name:
                            ballot.add(instance.get_project(project_name))
                    ballot_meta.pop("vote")
                elif vote_type in ["scoring", "cumulative"]:
                    if vote_type == "scoring":
                        ballot = CardinalBallot()
                    else:
                        ballot = CumulativeBallot()
                    if "points" in ballot_meta:  # if not, the ballot should be empty
                        points = ballot_meta["points"].split(",")
                        for index, project_name in enumerate(
                            ballot_meta["vote"].split(",")
                        ):
                            ballot[instance.get_project(project_name)] = str_as_frac(
                                points[index].strip()
                            )
                        ballot_meta.pop("vote")
                        ballot_meta.pop("points")
                elif vote_type == "ordinal":
                    ballot = OrdinalBallot()
                    for project_name in ballot_meta["vote"].split(","):
                        if project_name:
                            ballot.append(instance.get_project(project_name))
                    ballot_meta.pop("vote")
                else:
                    raise NotImplementedError(
                        "The PaBuLib parser cannot parse {} profiles for now.".format(
                            instance.meta["vote_type"]
                        )
                    )
                ballot.meta = ballot_meta
                ballots.append(ballot)

        legal_min_length = instance.meta.get("min_length", None)
        if legal_min_length is not None:
            legal_min_length = int(legal_min_length)
            if legal_min_length == 1:
                legal_min_length = None
        legal_max_length = instance.meta.get("max_length", None)
        if legal_max_length is not None:
            legal_max_length = int(legal_max_length)
            if legal_max_length >= len(instance):
                legal_max_length = None
        legal_min_cost = instance.meta.get("min_sum_cost", None)
        if legal_min_cost is not None:
            legal_min_cost = str_as_frac(legal_min_cost)
            if legal_min_cost == 0:
                legal_min_cost = None
        legal_max_cost = instance.meta.get("max_sum_cost", None)
        if legal_max_cost is not None:
            legal_max_cost = str_as_frac(legal_max_cost)
            if legal_max_cost >= instance.budget_limit:
                legal_max_cost = None
        legal_min_total_score = instance.meta.get("min_sum_points", None)
        if legal_min_total_score is not None:
            legal_min_total_score = str_as_frac(legal_min_total_score)
            if legal_min_total_score == 0:
                legal_min_total_score = None
        legal_max_total_score = instance.meta.get("max_sum_points", None)
        if legal_max_total_score is not None:
            legal_max_total_score = str_as_frac(legal_max_total_score)
        legal_min_score = instance.meta.get("min_points", None)
        if legal_min_score is not None:
            legal_min_score = str_as_frac(legal_min_score)
            if legal_min_score == 0:
                legal_min_score = None
        legal_max_score = instance.meta.get("max_points", None)
        if legal_max_score is not None:
            legal_max_score = str_as_frac(legal_max_score)
            if legal_max_score == legal_max_total_score:
                legal_max_score = None

        profile = None
        if instance.meta["vote_type"] == "approval":
            profile = ApprovalProfile(
                deepcopy(ballots),
                legal_min_length=legal_min_length,
                legal_max_length=legal_max_length,
                legal_min_cost=legal_min_cost,
                legal_max_cost=legal_max_cost,
            )
        elif instance.meta["vote_type"] == "scoring":
            profile = CardinalProfile(
                deepcopy(ballots),
                legal_min_length=legal_min_length,
                legal_max_length=legal_max_length,
                legal_min_score=legal_min_score,
                legal_max_score=legal_max_score,
            )
        elif instance.meta["vote_type"] == "cumulative":
            profile = CumulativeProfile(
                deepcopy(ballots),
                legal_min_length=legal_min_length,
                legal_max_length=legal_max_length,
                legal_min_score=legal_min_score,
                legal_max_score=legal_max_score,
                legal_min_total_score=legal_min_total_score,
                legal_max_total_score=legal_max_total_score,
            )
        elif instance.meta["vote_type"] == "ordinal":
            profile = OrdinalProfile(
                deepcopy(ballots),
                legal_min_length=legal_min_length,
                legal_max_length=legal_max_length,
            )

        # We retrieve the budget limit from the meta information
        instance.budget_limit = str_as_frac(instance.meta["budget"].replace(",", "."))

        # We add the category and target information that we collected from the projects
        instance.categories = optional_sets["categories"]
        instance.targets = optional_sets["targets"]

        pabutools.election.pabulib.write_pabulib(instance, profile, out_file_path)
