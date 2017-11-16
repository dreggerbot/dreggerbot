import asyncio
import bottom
import settings
import youtube
from urlextract import URLExtract

host = settings.irc.host
port = settings.irc.port
ssl = settings.irc.ssl
NICK = settings.irc.NICK
CHANNELS = settings.irc.CHANNELS


bot = bottom.Client(host=host, port=port, ssl=ssl)
loop = asyncio.get_event_loop()


def run():
    loop.create_task(bot.connect())

def send_message(_targets, _msg):
    if isinstance(_targets, list):
        for _target in _targets:
            bot.send("PRIVMSG", target=_target, message=_msg)
    if isinstance(_targets, str):
        bot.send("PRIVMSG", target=_targets, message=_msg)


class Handler:

    def handler(self, nick, target, msg):

        handler_coros = [
            self.onUrl
        ]

        for handler_coro in handler_coros:
            asyncio.get_event_loop().create_task(
                handler_coro(nick, target, msg)
            )

    async def onUrl(self, nick, target, msg):
        urls = URLExtract().find_urls(
            msg, only_unique=True
        )
        for url in urls:

            """ youtube video stats """
            if settings.youtube.api_key:
                result = await youtube.run(url)
                print(target, result)
                send_message(target, result)


handler = Handler()

@bot.on('PING')
def keepalive(message, **kwargs):
    bot.send('PONG', message=message)


@bot.on('CLIENT_CONNECT')
async def connect(**kwargs):
    bot.send('NICK', nick=NICK)
    bot.send('USER', user=NICK, realname=NICK)
    done, pending = await asyncio.wait(
        [bot.wait("RPL_ENDOFMOTD"),
         bot.wait("ERR_NOMOTD")],
        loop=loop, return_when=asyncio.FIRST_COMPLETED)
    # Cancel whichever waiter's event didn't come in.
    for future in pending:
        future.cancel()
    for CHANNEL in CHANNELS:
        bot.send('JOIN', channel=CHANNEL)


@bot.on('PRIVMSG')
def message(nick, target, message, **kwargs):
    if nick == NICK:
        """ ignore own """
        return
    if target == NICK:
        """ direct message """
        pass
    if target in CHANNELS:
        """ channel message """
        pass

    handler.handler(nick, target, message)

