'''Bot keyboards and some helpers'''

import json
import itertools
from config import const

ALL = 'SELECT ALL'
ACTIONS = ('add', 'view', 'drop')
ADD, VIEW, DROP = ACTIONS
INC_DEC = {'Increase': 1, 'Decrease': -1}

remove = json.dumps({'remove_keyboard': True})

btn = lambda x: {'text': x}


def chunk(arr, cols):
    return [[btn(x) for x in row if x]
            for row in itertools.zip_longest(*[iter(arr)] * cols)]

kbd = lambda btns, cols: json.dumps({'keyboard': chunk(btns, cols),
                                     'resize_keyboard': True})

actions = kbd(ACTIONS, 3)
exchanges = kbd(const.EXCHANGES, 2)
inc_dec = kbd(INC_DEC.keys(), 2)


def _markets(pairs):
    l = sorted(list(pairs))
    buttons = chunk(l, 3)
    buttons.append([btn(ALL)])
    return json.dumps({'keyboard': buttons, 'resize_keyboard': True})

markets = _markets
