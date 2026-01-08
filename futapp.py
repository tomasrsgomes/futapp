import sys
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
    t_games_count = sum(1 for (i, j) in games if i == t or j == t)
    max_possible_t = points[t] + 3 * t_games_count
    
    for k in range(n):
        if k != t and max_possible_t < points[k]:
            return -1

    prob = pulp.LpProblem(f"Team_{t}", pulp.LpMinimize)
    
    u = {}
    v = {}
    
    obj_terms = []

    points_from_games = [0] * n
    
    for (i, j) in games:
        if i == t:
            u_var = pulp.LpVariable(f"u_{i}_{j}", cat='Binary')
            u[(i, j)] = u_var
            obj_terms.append(u_var)
            
            points_from_games[i] += 2 * u_var + 1
            points_from_games[j] += 1 - u_var
            
        elif j == t:
            v_var = pulp.LpVariable(f"v_{i}_{j}", cat='Binary')
            v[(i, j)] = v_var
            obj_terms.append(v_var)
            
            points_from_games[j] += 2 * v_var + 1
            points_from_games[i] += 1 - v_var
            
        else:
            u_var = pulp.LpVariable(f"u_{i}_{j}", cat='Binary')
            v_var = pulp.LpVariable(f"v_{i}_{j}", cat='Binary')
            u[(i, j)] = u_var
            v[(i, j)] = v_var
            
            prob += u_var + v_var <= 1
            
            points_from_games[i] += 2 * u_var - v_var + 1
            points_from_games[j] += 2 * v_var - u_var + 1

    prob += pulp.lpSum(obj_terms)
    
    final_t = points[t] + points_from_games[t]
    
    for k in range(n):
        if k != t:
            rhs = points[k] + points_from_games[k]
            if isinstance(final_t, (int, float)) and isinstance(rhs, (int, float)):
                continue
            prob += final_t >= rhs

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
