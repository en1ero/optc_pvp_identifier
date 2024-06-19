from collections import Counter
import itertools,os

def get_ids(matches):
    id_raw = [os.path.basename(s)[:-4] for s in matches]
    counted = Counter(id_raw)
    return id_raw, counted

def make_teams(id_raw, matches):
        teams = []
        for i in range(int(len(matches)/8)):
            teams.append(sorted(id_raw[i*8:i*8+8]))
            teams[i] = [s for s in teams[i] if s != 'null']
        return teams

def make_counter(teams, num):
    counter = []
    for i in range(len(teams)):
        combinations = list(itertools.combinations(teams[i], num))
        counter.extend(combinations)

    return Counter(counter)


