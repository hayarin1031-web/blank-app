import streamlit as st
from collections import defaultdict
from itertools import combinations
import random

num = 4
num_people = st.number_input("人数：", min_value=4, max_value=50, value=9)

permit_num = 0 if num_people - 5 <= 1 else 1
people = list(range(1, num_people+1))

enter_count = defaultdict(int, {p: 0 for p in people})
pair_count = defaultdict(int)
rest_count = defaultdict(int, {p: 0 for p in people})
last_rest = set()

def select_members(people, enter_count, num):
    global last_rest
    while True:
        minimum = min(enter_count.values())
        members = []
        candidates = []
        while (len(members) < num):
            candidates = [p for p in people if enter_count[p] == minimum]
            if len(members) + len(candidates) < num:
                members += candidates
            else:
                break
            minimum += 1
        sub = num - len(members)
        members += random.sample(candidates, sub)
        rest_members = [x for x in enter_count.keys() if x not in members]
        min_rest = min(rest_count[p] for p in rest_members)
        rest_candidates = []
        out_flag = False
        while (set(rest_members) <= set(rest_candidates)):
            rest_candidates += [p for p in rest_members if rest_count[p] == min_rest]
            if (not (set(rest_members) <= set(rest_candidates)) and len(rest_candidates) > len(rest_members)):
                out_flag = True
                break
            min_rest += 1
        if out_flag:
            continue
        if len(last_rest & set(rest_members)) <= permit_num:
            last_rest = set(rest_members)
            return members, rest_members
        else:
            continue

def game():
    member, current_rest = select_members(people, enter_count, num)
    for i in member:
        enter_count[i] += 1
    for i in current_rest:
        rest_count[i] += 1
    overlap = 0
    min_overlap = 100
    for p in combinations(member,2):
        team1 = tuple(sorted(p))
        team2 = tuple(sorted(i for i in member if i not in team1))
        overlap += pair_count[team1]
        overlap += pair_count[team2]
        if overlap < min_overlap:
            min_overlap = overlap
            best_team = [team1,team2]
        overlap = 0
    pair_count[best_team[0]] += 1
    pair_count[best_team[1]] += 1
    return best_team, current_rest

if st.button("実行"):
    for _ in range(20):
        team, rest = game()
        st.write(f"チーム: {team}"}
