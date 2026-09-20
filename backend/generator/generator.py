"""
generator.py — generates a valid climbing problem using DFS + backtracking.

THE CORE IDEA:
A climbing problem is just a PATH through the reachability graph, from
a two-hand starting position to a high finishing hold, with a specific
number of moves (e.g. between 6 and 10).

REAL-CLIMBING CORRECTIONS (v2, based on reviewing real Tension/Kilter
Board problems):
1. A climber starts on TWO hands, not one -- you can't hang off a
   single hold before you even begin. So every generated problem now
   starts with a pair of nearby holds, not a single hold.
2. Footholds are excluded from the hand-path graph entirely. A
   foothold is not something you grab with your hand mid-route -- it's
   a place for your feet, tracked separately (see suggest_footholds
   below), not a candidate "next move" in the hand sequence.

We search for the hand path like this:
1. Pick a pair of nearby low holds as the two-hand start.
2. From the second (leading) hand, try moving to a reachable neighbor.
3. Keep extending the path, move by move.
4. If we ever get stuck, BACKTRACK: undo the last move and try a
   different neighbor instead.
5. If the path reaches the target length AND ends near the top of the
   wall, we've generated a valid problem.
"""

import random
import math
from generator.graph import build_graph
from generator.constraints import distance
from models.wall import HoldType


HAND_HOLD_TYPES = (HoldType.JUG, HoldType.CRIMP, HoldType.SLOPER)


def hand_holds(wall):
    """Every hold a climber could actually grab with a hand (excludes footholds)."""
    return [h for h in wall.holds if h.hold_type in HAND_HOLD_TYPES]


def pick_start_pair(wall, low_band_fraction=0.18, max_hand_span_cm=55):
    """
    Picks two distinct, nearby hand holds low on the wall -- a realistic
    two-hand starting position. Returns (hold_a, hold_b) or None if no
    valid pair exists.
    """
    threshold = wall.height_cm * low_band_fraction
    candidates = [h for h in hand_holds(wall) if h.y <= threshold]

    pairs = []
    for a in candidates:
        for b in candidates:
            if a.id >= b.id:
                continue
            if distance(a, b) <= max_hand_span_cm:
                pairs.append((a, b))

    if not pairs:
        return None
    return random.choice(pairs)


def pick_finish_holds(wall, high_band_fraction=0.85):
    """Any hand hold in the top ~15% of the wall is a plausible finish hold."""
    threshold = wall.height_cm * high_band_fraction
    return [h for h in hand_holds(wall) if h.y >= threshold]


def pick_start_feet(wall, start_a, start_b, max_horizontal_cm=30, max_vertical_below_cm=45):
    """
    Finds 1-2 footholds to serve as the REQUIRED starting foot position,
    below and roughly underneath the two starting hand holds -- matching
    real board convention (e.g. Kilter: magenta start feet, green start
    hands). Unlike suggest_footholds (a soft visual aid for mid-route
    moves), this is a hard requirement: a climbing problem without any
    start feet isn't really a valid problem.
    """
    footholds = [h for h in wall.holds if h.hold_type == HoldType.FOOTHOLD]
    start_x = (start_a.x + start_b.x) / 2
    start_y = min(start_a.y, start_b.y)

    candidates = []
    for f in footholds:
        if f.y >= start_y:
            continue  # feet must be below the hands
        if (start_y - f.y) > max_vertical_below_cm:
            continue
        if abs(f.x - start_x) > max_horizontal_cm:
            continue
        candidates.append(f)

    candidates.sort(key=lambda f: distance_point(f.x, f.y, start_x, start_y))
    return [f.id for f in candidates[:2]]  # up to 2 start feet, like the reference board


def distance_point(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)


def suggest_footholds(wall, hand_path, max_horizontal_cm=35, max_vertical_below_cm=60):
    """
    For each hand hold in the path, suggest the nearest foothold that's
    below it and roughly underneath it -- a simple, honest visual aid for
    "where feet might go", NOT a claim about real biomechanics (out of
    scope, per project constraints). Returns a list the same length as
    hand_path: foothold id or None per hand hold.
    """
    footholds = [h for h in wall.holds if h.hold_type == HoldType.FOOTHOLD]
    suggestions = []

    for hand_id in hand_path:
        hand = wall.get_hold(hand_id)
        best = None
        best_dist = None
        for f in footholds:
            if f.y >= hand.y or (hand.y - f.y) > max_vertical_below_cm:
                continue  # must be below the hand hold, within a plausible range
            if abs(f.x - hand.x) > max_horizontal_cm:
                continue  # must be roughly underneath
            d = distance(hand, f)
            if best is None or d < best_dist:
                best, best_dist = f.id, d
        suggestions.append(best)

    return suggestions


def _count_direction_changes(wall, path):
    """How many times the path's left/right direction flips -- a proxy for
    how zigzaggy vs. dead-straight the problem is. Local to this file to
    avoid a circular import with features.py (which imports FROM here)."""
    holds = [wall.get_hold(hid) for hid in path]
    changes = 0
    prev_sign = None
    for a, b in zip(holds[1:], holds[2:]):  # skip the start-pair span
        dx = b.x - a.x
        sign = 1 if dx > 0 else (-1 if dx < 0 else 0)
        if prev_sign is not None and sign != 0 and sign != prev_sign:
            changes += 1
        if sign != 0:
            prev_sign = sign
    return changes


def generate_problem(wall, min_moves=6, max_moves=10, max_attempts=300,
                      min_reach_cm=15, max_reach_cm=90, min_direction_changes=2):
    """
    Returns a dict: {"hand_path": [...], "start_feet": [...]}, or None if
    no valid problem could be found after max_attempts tries.

    Two realism requirements enforced here (added after reviewing a real
    Kilter Board problem):
    1. The problem must have real starting footholds (not just hand
       holds floating with no feet) -- pick_start_feet is REQUIRED to
       find at least one, or that start position is rejected and retried.
    2. The path must zigzag at least a little (min_direction_changes) --
       otherwise backtracking search tends to just grab the nearest
       upward hold every time, producing an unrealistic dead-straight line.
    """
    graph = build_graph(wall, min_reach_cm, max_reach_cm, holds=hand_holds(wall))
    finish_ids = {h.id for h in pick_finish_holds(wall)}

    if not finish_ids:
        return None

    for _attempt in range(max_attempts):
        start_pair = pick_start_pair(wall)
        if start_pair is None:
            return None
        start_a, start_b = start_pair

        start_feet = pick_start_feet(wall, start_a, start_b)
        if not start_feet:
            continue  # no real feet available here -- this start position isn't valid, try another

        initial_path = [start_a.id, start_b.id]
        initial_visited = {start_a.id, start_b.id}

        path = _backtrack_search(
            graph, start_b.id, finish_ids, min_moves, max_moves,
            path=initial_path, visited=initial_visited,
        )
        if path is None:
            continue

        if _count_direction_changes(wall, path) < min_direction_changes:
            continue  # too straight/linear -- reject and try a different start/path

        return {"hand_path": path, "start_feet": start_feet}

    return None  # honestly report failure rather than returning a bad result


def _backtrack_search(graph, current_id, finish_ids, min_moves, max_moves,
                       path=None, visited=None):
    """
    The recursive backtracking step. `path` is the sequence of hold ids
    built so far (including the 2-hold start); `visited` prevents
    revisiting the same hold twice. Move count is measured AFTER the
    starting pair, so a min_moves=6 problem has 2 start holds + 6 more.
    """
    if path is None:
        path = [current_id]
        visited = {current_id}

    moves_so_far = len(path) - 2  # subtract the 2-hold start position

    if moves_so_far >= min_moves and current_id in finish_ids:
        return path

    if moves_so_far >= max_moves:
        return None

    neighbors = graph[current_id][:]
    random.shuffle(neighbors)  # try neighbors in random order -- gives varied problems

    for next_id in neighbors:
        if next_id in visited:
            continue

        path.append(next_id)
        visited.add(next_id)

        result = _backtrack_search(graph, next_id, finish_ids, min_moves, max_moves, path, visited)
        if result is not None:
            return result  # a full valid path was found further down -- bubble it up

        # BACKTRACK: this branch didn't work out, undo the move and try the next neighbor
        path.pop()
        visited.remove(next_id)

    return None  # every neighbor from here was a dead end
