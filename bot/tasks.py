import asyncio
import logging
import json
from calendar import timegm
from datetime import datetime as dt
from bot.main import bot
from bot.database import db
from bot.helpers import fetch_feed, get_upwork_status
import re
from html import unescape


def transform_description(text):
    text = re.sub(' +', ' ', text)
    text = text.replace('<br/>', '\n').replace('<br />', '\n').replace('<br>', '\n').replace('<b>', '').replace('</b>', '')
    text = re.sub('\n+', '\n', text)
    text = text.split('<a href="https://www.upwork.com/jobs/')[0]
    text = text.replace('Budget:', '<b>Budget:</b>').replace('Posted On:', '<b>Posted On:</b>').replace('Category:', '<b>Category:</b>')
    text = text.replace('Skills:', '<b>Skills:</b> ').replace('Country:', '<b>Country:</b>')
    if len(text) > 3800:
        new_text = text.split('<b>Posted')[0]
        text = new_text[:1024] + '...\n<b>Posted On:</b>' + text.split('<b>Posted On:</b>')[-1]
    return text


def get_job_id(link):
    link = link.split('_%7E')[-1].split('?')[0]
    return '~' + link

async def update_process():
    if await get_upwork_status(bot):
        count = await update_processing()
        if count > 0:
            logging.info(f'Found {count} feeds for updating')
        else:
            logging.info(f'No updates found')
    else:
        logging.info('Upwork is down.')


async def update_processing():
    count = 0
    now = int(dt.utcnow().timestamp())
    cond = 'this.period < {} - this.last_updated'.format(now)
    async for x in db.chats.find({'feed_url': {'$exists': True},
                                  '$where': cond}):
        r = await fetch_feed(x['feed_url'])
        if r:
            asyncio.ensure_future(notify(x, r, now))
            count += 1

    return count


async def notify(chat, r, now):
    feed_updated = timegm(r.entries[0].updated_parsed)
    logging.debug(f"tag: {chat['tag']}, feed_updated from db: {chat['feed_updated']}, latest item: {feed_updated}")
    entries = []
    for x in r.entries:
        if chat['feed_updated'] < timegm(x.updated_parsed):
            entries.append(x)
            # if published for not last entry is bigger
            if feed_updated < timegm(x.updated_parsed):
                feed_updated = timegm(x.updated_parsed)
                logging.debug(f"found latest timestamp: {feed_updated}")
    entries.reverse()
    length = len(entries)
    if length > 0:
        logging.debug(f"last entry timestamp: {feed_updated}")
        logging.info(f"Found {length} new entries for chat_id {chat['chat_id']} ({chat['username']}) for feed: {chat['tag']}")
        upd = {'$set': {'last_updated': now, 'feed_updated': feed_updated}}
        await db.chats.update_one({'chat_id': chat['chat_id'], 'tag': chat['tag']}, upd)
    else:
        logging.info(f"Not found entries for chat_id {chat['chat_id']} ({chat['username']}) for feed: {chat['tag']}")

    for x in entries:
        logging.info(f'New entry: {x}')
        job_id = get_job_id(x['link'])
        x['link'] = 'https://www.upwork.com/jobs/' + job_id
        x['title'] = unescape(re.sub('- Upwork', '', x['title']))
        x['summary'] = transform_description(unescape(x['summary']))
        msg = '<b>{title}</b>\n\n{summary}\n\n<b>feed:</b> #{tag}'.format(**x, tag=chat['tag'])
        apply_link = f'https://www.upwork.com/ab/proposals/job/{job_id}/apply/#/'
        open_link = x['link']
        inline_button = {
            "type": "InlineKeyboardMarkup",
            "inline_keyboard": [
                [
                    {
                        "type": "InlineKeyboardButton",
                        "text": "Open job",
                        "url": open_link
                    },
                    {
                        "type": "InlineKeyboardButton",
                        "text": "Apply",
                        "url": apply_link
                    }

                ],
            ],
        }

        try:
            await bot.send_message(chat['chat_id'],
                                   msg,
                                   parse_mode="HTML",
                                   reply_markup=json.dumps(inline_button))
        except Exception as e:
            if e.response.status == 403:
                logging.info('Bot blocked by user {} - {} . Removing..'
                            .format(chat.get('username', chat['chat_id']), chat['chat_id']))
                await db.chats.delete_many({'chat_id': chat['chat_id']})
            raise e

    
