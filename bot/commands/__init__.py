from . import base
from .period import period
from .feed import add, delete, list


def register_commands(bot):
    '''Registering commands'''

    for cmd in ('start', 'stop', 'help', 'upwork_status_off', 'upwork_status_on'):
        bot.add_command('/{}'.format(cmd), getattr(base, cmd))

    for cmd in ('add', 'delete', 'list', 'period'):
        bot.add_command('/{}'.format(cmd), eval(cmd))
