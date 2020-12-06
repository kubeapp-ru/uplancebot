from datetime import timedelta
from config import settings
from bot.database import db

'''
The choice of the period consists of three steps:
'''
s2i = lambda x: int(x) if x.isdigit() else 0

CONVERT = {'h': lambda x: s2i(x) * 3600,
           'm': lambda x: s2i(x) * 60,
           's': lambda x: s2i(x)}

async def handler(chat, message):
    val = 0
    for x in message.get('text', []).split():
        m = CONVERT.get(x[-1])
        if m:
            val += m(x[0:-1])
    if val < settings.MIN_UPDATE_PERIOD:
        msg = 'Period should be more than {} sec. Cancelling.'\
              .format(settings.MIN_UPDATE_PERIOD)
    else:
        msg = 'Period is set to: {}'.format(timedelta(seconds=val))
        await db.chats.update_many({'chat_id': chat.id},
                                   {'$set': {'period': val}})
    return await chat.send_text(msg)


async def period(chat, msg):
    chat.bot.set_next_step(chat, handler)
    return await chat.send_text('Input period\nMinimum {} seconds\nFor example: \n 1m \n 1h \n 1h 30m 15s'
                                .format(settings.MIN_UPDATE_PERIOD))
