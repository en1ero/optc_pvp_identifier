from collections import Counter
import itertools
import os

def get_ids(matches):
    id_raw = [os.path.basename(s)[:-4] for s in matches]
    counted = Counter(id_raw)
    print(f'Number of individual units: {len(counted)-1}')
    percent = 5
    single_count_elements = [element for element, count in counted.most_common() if count < percent]
    single_count_count = len(single_count_elements)
    print(f'{100-percent}% of teams use the same set of {len(counted)-1-single_count_count} units.')
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
    if num == 1:
        print(f'Number of units per Team: {len(counter)/99:.2f}')
    return Counter(counter)


def sort_by_similarity(teams):
    entries_dict = {str(i).zfill(2): entry for i, entry in enumerate(teams)}

    def jaccard_similarity(list1, list2):
        set1, set2 = set(list1), set(list2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union

    # Calculate similarities
    similarities = {}
    for (key1, list1), (key2, list2) in itertools.combinations(entries_dict.items(), 2):
        similarity = jaccard_similarity(list1, list2)
        similarities[(key1, key2)] = similarity

    # Sort pairs by similarity
    sorted_similarities = sorted(similarities.items(), key=lambda item: item[1], reverse=True)

    # Create groups of similar entries
    groups = []
    visited = set()

    for (key1, key2), similarity in sorted_similarities:
        if key1 not in visited and key2 not in visited:
            # Create a new group
            groups.append([key1, key2])
            visited.update([key1, key2])
        elif key1 not in visited:
            # Find the group containing key2 and add key1 to it
            for group in groups:
                if key2 in group:
                    group.append(key1)
                    visited.add(key1)
                    break
        elif key2 not in visited:
            # Find the group containing key1 and add key2 to it
            for group in groups:
                if key1 in group:
                    group.append(key2)
                    visited.add(key2)
                    break

    # Add remaining ungrouped entries to groups
    for key in entries_dict.keys():
        if key not in visited:
            groups.append([key])

    # Print the groups
    print("\nGroups of similar entries:")
    reordered_ids = []
    for group in groups:
        print(group)  # Print each group
        for i in range(len(group)):
            reordered_ids.append(int(group[i]))  # Collect the indices
    
    return reordered_ids