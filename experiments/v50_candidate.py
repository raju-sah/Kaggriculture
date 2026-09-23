"""v50 Candidate: Kazuhiro Aggressive Opening + Adaptive Terminal Market Execution."""

import experiments.v48_agent
from v23.planner import build_sparse_planner, PlannerConfig
from scripts.v19_terminal import apply_overlay
from experiments.kazuhiro_agent import ACTIONS

_base_planner = build_sparse_planner(ACTIONS, PlannerConfig())


def agent(obs, configuration=None):
    base_action = _base_planner(obs, configuration)
    return apply_overlay(obs, base_action, "late_collision")


def _kaggle_submission_entrypoint(obs, configuration=None):
    return agent(obs, configuration)
