# -*- coding: UTF-8 -*-
import os
import asyncio
import aiohttp
import logging
import feedparser
import random
from datetime import datetime
from config import settings
from bot.database import db
from pymongo import DESCENDING
import cfscrape


async def fetch_feed(url):
    data = await fetch_data(url)
    return parse_feed(data) if data else data


async def get_upwork_status(bot):
    resp = await fetch_data(settings.UPWORK_STATUS, json=True)
    if resp:
        try:
            status = resp['result']['status_overall']
            status_code = resp['result']['status_overall']['status_code']
            updated = resp['result']['status_overall']['updated']
            updated_date = datetime.strptime(updated, '%Y-%m-%dT%H:%M:%S.%fZ')
        except KeyError:
            return False
        last_status = await db.status.find_one(sort=[('_id', DESCENDING)])
        if last_status is None:
            # For first time start
            r = await db.status.insert_one({'website': 'upwork', 'status_code': status_code, 'datetime': updated_date})
            return True
        if last_status['status_code'] != status_code:
            await notify(bot, status.get('status', 'Unknown'))
            r = await db.status.insert_one({'website': 'upwork', 'status_code': status_code, 'datetime': updated_date})
        if status_code == 100:
            return True
    return False


async def fetch_data(url, json=False):
    '''Helper returns a feed from url'''
    async with cfscrape.CloudflareScraperAsync() as session:
    #async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    return await resp.json(encoding="utf8") if json else await resp.text(encoding="utf8")
                else:
                    g.inc()
                    logging.warn('Fetch data failed. URL: {}, \n'
                                'Status: {}. {}'.format(url, resp.status, resp.json()))
        except Exception as e:
            logging.exception(e)
    return None


async def get_last_status(sort_field):
    async for x in db.status.find().sort(sort_field, -1).limit(1):
        return x


def parse_feed(data):
    feed = feedparser.parse(data)
    if not feed.bozo:
        return feed
    logging.warn('{}').format(feed.bozo_exception.getMessage())
    return None


async def notify(bot, s):
    async for chat in db.chats.find({'status_notify': True}):
        task = bot.send_message(chat['chat_id'],
                                '*Upwork status has changed to {}.*\n\
Please check https://status.upwork.com for more information'.format(s),\
                               parse_mode='Markdown')
        asyncio.ensure_future(task)
