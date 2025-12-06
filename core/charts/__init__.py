import random

CHART_COLORS = [
    'gold',
    'mediumturquoise',
    'darkorange',
    'lightgreen',
    'crimson',
    'dodgerblue',
    'lime',
    'orchid',
    'darkolivegreen',
    'deepskyblue',
    'hotpink',
    'teal',
    'coral',
    'slateblue',
    'yellowgreen',
    'tomato',
    'steelblue',
    'mediumspringgreen',
    'mediumpurple',
    'orangered',
]


def get_colors(n:int) -> list[str]:
    result = set()
    while len(result) < n:
        candidate = random.choice(CHART_COLORS)
        if candidate not in result:
            result.add(candidate)
    return list(result)