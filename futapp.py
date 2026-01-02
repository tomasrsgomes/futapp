import sys
import math
import pulp


def read_input():
    data = sys.stdin.read().strip().split()
    it = iter(data)

    n = int(next(it))
    m = int(next(it))

    played = set()
    points = [0] * n

    for _ in range(m):
        i = int(next(it)) - 1
        j = int(next(it)) - 1
        r = int(next(it))

        played.add((i, j))

        if r == 0:
            points[i] += 1
            points[j] += 1
        else:
            winner = r - 1
            points[winner] += 3

    return n, points, played


def remaining_games(n, played):
    games = []
    for i in range(n):
        for j in range(n):
            if i != j and (i, j) not in played:
                games.append((i, j))
    return games


def solve_for_team(t, n, points, games):
    prob = pulp.LpProblem(f"Team_{t}", pulp.LpMinimize)

    # Variables for each game: i wins (u), j wins (v), draw (z)
    u = {}
    v = {}
    z = {}
    
    for (i, j) in games:
        u[(i, j)] = pulp.LpVariable(f"u_{i}_{j}", cat='Binary')
        v[(i, j)] = pulp.LpVariable(f"v_{i}_{j}", cat='Binary')
        z[(i, j)] = pulp.LpVariable(f"z_{i}_{j}", cat='Binary')
        
        # Constraint: exactly one outcome per game
        prob += u[(i, j)] + v[(i, j)] + z[(i, j)] == 1

    # objective: minimize wins of team t
    obj_terms = []
    for (i, j) in games:
        if i == t:
            obj_terms.append(u[(i, j)])
        elif j == t:
            obj_terms.append(v[(i, j)])
    
    prob += pulp.lpSum(obj_terms)

    # final points of each team
    final_points = [points[k] for k in range(n)]

    for (i, j) in games:
        final_points[i] += 3 * u[(i, j)] + 1 * z[(i, j)]
        final_points[j] += 3 * v[(i, j)] + 1 * z[(i, j)]
    


    # championship constraints
    for i in range(n):
        if i != t:
            if isinstance(final_points[t], (int, float)) and isinstance(final_points[i], (int, float)):
                if final_points[t] < final_points[i]:
                    return -1
            else:
                prob += final_points[t] >= final_points[i]


    status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

    if status != pulp.LpStatusOptimal:
        return -1

    val = pulp.value(prob.objective)
    if val is None:
        return 0

    return round(val)


def main():
    n, points, played = read_input()
    games = remaining_games(n, played)

    for t in range(n):
        print(solve_for_team(t, n, points, games))


if __name__ == "__main__":
    main()
