
import streamlit as st
from collections import defaultdict
from itertools import combinations
import random

# =========================
# 基本設定
# =========================

num = 4  # 1試合の参加人数

num_people = st.number_input(
    "人数：",
    min_value=4,
    max_value=50,
    value=9
)

people = list(range(1, num_people + 1))

# 1試合あたりの候補探索回数
SEARCH_COUNT = 500


# =========================
# 履歴の初期化
# =========================

def initialize():
    st.session_state.enter_count = defaultdict(
        int, {p: 0 for p in people}
    )

    st.session_state.rest_count = defaultdict(
        int, {p: 0 for p in people}
    )

    st.session_state.pair_count = defaultdict(int)
    st.session_state.opponent_count = defaultdict(int)
    st.session_state.last_rest = set()
    st.session_state.history = []


# 初回実行時・人数変更時に初期化
if (
    "saved_num_people" not in st.session_state
    or st.session_state.saved_num_people != num_people
):
    st.session_state.saved_num_people = num_people
    initialize()

enter_count = st.session_state.enter_count
rest_count = st.session_state.rest_count
pair_count = st.session_state.pair_count
opponent_count = st.session_state.opponent_count


# =========================
# 出場者の選択
# =========================

def select_members(people, enter_count, num):

    # 出場回数の少ない順に並べる
    sorted_people = sorted(
        people,
        key=lambda p: enter_count[p]
    )

    # 4番目に少ない人の出場回数
    threshold = enter_count[sorted_people[num - 1]]

    # 必ず出場する人
    fixed_members = [
        p for p in people
        if enter_count[p] < threshold
    ]

    # 同じ出場回数の候補者
    candidates = [
        p for p in people
        if enter_count[p] == threshold
    ]

    remaining = num - len(fixed_members)

    best_members = None
    best_rest = None
    best_score = float("inf")

    # 候補をランダムに探索
    for _ in range(SEARCH_COUNT):

        selected = random.sample(
            candidates, remaining
        )

        members = fixed_members + selected

        rest_members = [
            p for p in people
            if p not in members
        ]

        # 前回から連続して休憩する人数
        overlap = len(
            st.session_state.last_rest
            & set(rest_members)
        )

        # 休憩回数の偏り
        rest_values = [
            rest_count[p] + (p in rest_members)
            for p in people
        ]

        rest_balance = (
            max(rest_values) - min(rest_values)
        )

        # 評価値（小さいほど良い）
        score = (
            overlap * 10
            + rest_balance * 3
        )

        if score < best_score:
            best_score = score
            best_members = members
            best_rest = rest_members

    return best_members, best_rest


# =========================
# チーム分け
# =========================

def select_teams(members):

    best_score = float("inf")
    best_teams = []

    # 4人から2人を選ぶ
    for p in combinations(members, 2):

        team1 = tuple(sorted(p))

        team2 = tuple(sorted(
            i for i in members
            if i not in team1
        ))

        # ペアの重複回数
        pair_overlap = (
            pair_count[team1]
            + pair_count[team2]
        )

        # 対戦相手の重複回数
        opponent_overlap = 0

        for a in team1:
            for b in team2:
                pair = tuple(sorted((a, b)))
                opponent_overlap += opponent_count[pair]

        # 評価値
        score = (
            pair_overlap * 10
            + opponent_overlap * 2
        )

        if score < best_score:
            best_score = score
            best_teams = [(team1, team2)]

        elif score == best_score:
            best_teams.append((team1, team2))

    # 同点ならランダム選択
    return random.choice(best_teams)


# =========================
# 1試合を生成
# =========================


def game():

    # 最初の試合は固定
    if len(st.session_state.history) == 0:
        team1 = (1, 2)
        team2 = (3, 4)

        members = [1, 2, 3, 4]
        current_rest = [
            p for p in people if p not in members
        ]

    # 2試合目以降は自動選択
    else:
        members, current_rest = select_members(
            people, enter_count, num
        )

        team1, team2 = select_teams(members)

    # 出場回数を更新
    for p in members:
        enter_count[p] += 1

    # 休憩回数を更新
    for p in current_rest:
        rest_count[p] += 1

    # ペア回数を更新
    pair_count[team1] += 1
    pair_count[team2] += 1

    # 対戦回数を更新
    for a in team1:
        for b in team2:
            pair = tuple(sorted((a, b)))
            opponent_count[pair] += 1

    # 前回の休憩者を保存
    st.session_state.last_rest = set(current_rest)

    return (team1, team2), current_rest



# =========================
# Streamlit画面
# =========================

st.title("チーム分けシステム")

col1, col2 = st.columns(2)

with col1:
    execute = st.button("20試合生成")

with col2:
    reset = st.button("履歴リセット")

if reset:
    initialize()
    st.success("履歴をリセットしました")

if execute:

    for _ in range(20):

        team, rest = game()

        st.session_state.history.append({
            "team": team,
            "rest": rest
        })


# =========================
# 試合結果の表示
# =========================

st.subheader("試合結果")

for i, result in enumerate(st.session_state.history, 1):

    team = result["team"]
    rest = result["rest"]

    st.write(
        f"第{i}試合: "
        f"{team[0]} vs {team[1]}"
    )

    st.write(f"休憩: {rest}")


# =========================
# 出場回数の表示
# =========================

st.subheader("出場・休憩回数")

data = []

for p in people:
    data.append({
        "参加者": p,
        "出場回数": enter_count[p],
        "休憩回数": rest_count[p]
    })

st.dataframe(
    data,
    hide_index=True,
    use_container_width=True
)


# =========================
# ペア履歴の表示
# =========================

st.subheader("ペア履歴")

pair_data = []

for pair, count in sorted(pair_count.items()):
    if count > 0:
        pair_data.append({
            "ペア": str(pair),
            "同じチームになった回数": count
        })

st.dataframe(
    pair_data,
    hide_index=True,
    use_container_width=True
)
