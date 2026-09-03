"""
graph.py — turns a Wall's holds into a graph of possible moves.

Each hold is a node. An edge A -> B exists if is_valid_move(A, B) says
a climber could plausibly make that move (see constraints.py).

We represent the graph as an "adjacency list": a dictionary mapping each
hold's id to a list of hold ids it can reach. This is the standard,
simplest way to represent a graph in code.
"""

from generator.constraints import is_valid_move


def build_graph(wall, min_reach_cm=15, max_reach_cm=90, holds=None):
    """
    O(n^2) over all hold pairs -- fine for ~100-300 holds (a real board's
    scale). Returns: {hold_id: [reachable_hold_id, ...], ...}

    `holds`: optionally restrict which holds are included as graph nodes
    (e.g. hand holds only, excluding footholds). Defaults to every hold
    on the wall.
    """
    if holds is None:
        holds = wall.holds

    graph = {h.id: [] for h in holds}

    for a in holds:
        for b in holds:
            if a.id == b.id:
                continue
            if is_valid_move(a, b, min_reach_cm, max_reach_cm):
                graph[a.id].append(b.id)

    return graph
