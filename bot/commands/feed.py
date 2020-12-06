from calendar import timegm
from datetime import datetime as dt
from config import settings
from bot.database import db
from bot.helpers import fetch_feed
import re

async def check_admin(chat):
    if chat.id in settings.ADMINS:
        return True
    else:
        await chat.send_text('Sorry you are not in Admins list.')

async def add(chat, msg):
    check = check_admin(chat)
    if check:
        name = chat.message.get('text', '').strip()
        if name == "/add":
            chat.bot.set_next_step(chat, add)
            return await chat.send_text("Enter name for new feed. \nDon't use special symbols or spaces")
        name = chat.message.get('text', '').strip()
        if len(name) > 20:
            chat.bot.set_next_step(chat, add)
            return await chat.send_text('Please do not make long names. Limit is 20 symbols.\n'
                                        'Try enter name again.')
        if not re.match("^[a-zA-Z0-9_]*$", name):
            chat.bot.set_next_step(chat, add)
            return await chat.send_text('Please do not use special symbols or space.\n'
                                        'Try enter name again.')
        c = await db.chats.count_documents({'chat_id': chat.id})
        if c >= settings.MAX_FEED_COUNT:
            return await chat.send_text('You have reached limit.\n\
    Only {} searches could be saved.\n\
    Please delete some using command /delete_feed'.format(settings.MAX_FEED_COUNT))
        d = await db.chats.find_one({'chat_id': chat.id, 'tag': name})

        if d is not None:
            chat.bot.set_next_step(chat, add)
            return await chat.send_text('That name exist, please enter different name for new feed.')

        chat.bot.set_next_step(chat, feed, name=name)
        await chat.send_text('Please enter the RSS feed url for search *{}*'.format(name), parse_mode='Markdown')
        return await chat.send_photo(photo=open("/opt/bot/images/rss.png", "rb"), caption="Open RSS page and copy url from address bar.")

async def delete(chat, msg):
    check = check_admin(chat)
    if check:
        name = chat.message.get('text', '').strip()
        d = db.chats.find({'chat_id': chat.id})
        list_d = []
        for i in await d.to_list(length=settings.MAX_FEED_COUNT):
            list_d.append(i['tag'])
        str_list_d = ', '.join(list_d)
        if list_d is None:
            return await chat.send_text('You don\'t have any feeds. Use /add to add new feed.')
        if name == "/delete_feed":
            chat.bot.set_next_step(chat, delete_feed)
            return await chat.send_text('Enter name of feed for deleting: {}'.format(str_list_d))
        tag_query = await db.chats.find_one({'chat_id': chat.id, 'tag': name})
        if tag_query is None and user_exist is not None:
            chat.bot.set_next_step(chat, delete_feed)
            return await chat.send_text('Wrong name, choose it from list: {}'.format(str_list_d))
        await db.chats.delete_one({'chat_id': chat.id, 'tag': name})
        return await chat.send_text('Feed with name _{}_ were deleted.'.format(name), parse_mode='Markdown')

async def list(chat, msg):
    check = check_admin(chat)
    if check:
        feed = db.chats.find({'chat_id': chat.id})
        message = ""
        for i in await feed.to_list(length=settings.MAX_FEED_COUNT):
            line = "{tag}:\n{feed_url}\n\n".format(**i)
            message+=line
        return await chat.send_text('Here is your feeds:\n\n{}'.format(message))

async def feed(chat, msg, **name):
    url = chat.message.get('text', '').strip()
    d = await db.chats.find_one({'chat_id': chat.id, 'feed_url': url})
    if d is not None:
        chat.bot.set_next_step(chat, feed, name=name['name'])
        return await chat.send_text('That url already exist, please enter different RSS feed url')
    r = await fetch_feed(url)
    if r:
        msg = 'Subscribed to your RSS feed - {}.\n\
Update period was set to {} seconds.\n\
You can change period with command /period \n\
Also you can check list of feed with command /list \n\
and add new feeds with /add'.format(name['name'], settings.MIN_UPDATE_PERIOD)
        upd = {'$set': {'chat_id': chat.id,
                        'username': chat.sender.get('username', ''),
                        'feed_url': url,
                        'last_updated': int(dt.utcnow().timestamp()),
                        'feed_updated': timegm(r.feed.updated_parsed),
                        'status_notify': True,
                        'tag': name['name'],
                        'period': settings.MIN_UPDATE_PERIOD}}
        await db.chats.update_one({'chat_id': chat.id, 'tag': name['name']}, upd, upsert=True)
    else:
        msg = 'Can not find any data from given url.'
    return await chat.send_text(msg)

async def cancel(chat, msg):
    #do nothing
    return True