import asyncio
import settings

""" 
    python3.5
    module: aiohttp bottom urlextract asyncws 
"""

settings.irc()
settings.youtube()

settings.irc.host = 'chat.freenode.net'
settings.irc.port = 6697
settings.irc.ssl = True
settings.irc.NICK = "dreggerb0t"
settings.irc.CHANNELS = ["#test", "#test2"]
settings.youtube.api_key = None


import irc
import younow

loop = asyncio.get_event_loop()

""" 
    younow.run('YounowChannelName1', ['#irc_channel1', '#irc_channel2' ...])
    younow.run('YounowChannelName2', ['#irc_channel1', '#irc_channel2' ...])
"""

younow.run('YounowChannelName', ['#test', '#test2'])
irc.run()

loop.run_forever()
