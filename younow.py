import aiohttp
import asyncws
import json
import asyncio
from irc import send_message


class Events:

    """
        banned_fan
        new_comment
        onBroadcast
        onBroadcastEnd
        onBroadcastPlayData
        onChat
        onGift
        onGuestConnecting
        onGuestEnd
        onGuestPublish
        onLikes
        onPartnerSticker
        onSuperMessage
        onSystemMessage
        onTopFanChange
        onViewers
        pusher_connection_established
        pusher_internal_subscription_succeeded
        ...
    """

    def onBroadcast(self, result, channel_id, channel_name, irc_channels):
        msg = 'younow [user: %s] screamt etzala tatsächlich' % channel_name
        send_message(irc_channels, msg)

    def onBroadcastPlayData(self, result, channel_id, channel_name, irc_channels):
        #print(channel_name, 'onBroadcastPlayData [data][message]:', [key for key in result['data']['message']])
        pass

    def onChat(self, result, channel_id, channel_name, irc_channels):
        comments = result['data']['message']['comments']
        for comment in comments:
            if comment['userId'] == channel_id:
                """ channel op schreib """
                msg = 'younow: [channel: %s] [user: %s]: %s' % (channel_name, channel_name, comment['comment'])
                print(msg)
                send_message(irc_channels, msg)
            else:
                """ jemand anders schreibt """
                msg = 'younow: [channel: %s] [user: %s]: %s' % (channel_name, comment['name'], comment['comment'])
                print(msg)


    def pusher_connection_established(self, result, channel_id, channel_name, irc_channels):
        print(channel_name, result)
        pass

    def pusher_internal_subscription_succeeded(self, result, channel_id, channel_name, irc_channels):
        print(channel_name, result)

    def _onAnyOther(self, result, channel_id, channel_name, irc_channels):
        pass


class Handler:
    def __init__(self):
        self.events = Events()

    def handler(self, result, channel_id, channel_name, irc_channels):
        res = json.loads(result)
        event = res['event'].replace(':', '_')
        on_other = getattr(
            self.events, '_onAnyOther', None
        )
        on_event = getattr(
            self.events, event, on_other
        )
        if on_event:
            res['data'] = json.loads(res['data'])
            on_event(
                res, channel_id, channel_name, irc_channels
            )


handler = Handler()


async def get_channel_info(channel_name):
    url = "https://api.younow.com/php/api/broadcast/info/curId=0/user=%s" % channel_name
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            response = await resp.json()
        session.close()
    print(channel_name, response)
    return response


async def ws_connect(channel_name, irc_channels):
    channel_data = await get_channel_info(channel_name)
    channel_id = channel_data['userId']
    url = 'wss://ws-younow.pusher.com/app/d5b7447226fc2cd78dbb?protocol=7&client=js&version=2.2.4&flash=false'
    payload = ['{"event":"pusher:subscribe","data":{"channel":"public-channel_%s"}}' % channel_id,
               '{"event":"pusher:subscribe","data":{"channel":"public-async-channel_%s"}}' % channel_id]
    ws = await asyncws.connect(url)
    await ws.send(payload[0])
    await ws.send(payload[1])
    while True:
        result = await ws.recv()

        handler.handler(
            result, channel_id, channel_name, irc_channels
        )


def run(channel_name, irc_channels):
    asyncio.get_event_loop().create_task(
        ws_connect(
            channel_name, irc_channels
        )
    )

