from urllib.parse import urlencode, urlparse, parse_qs
import aiohttp
import settings


key = settings.youtube.api_key

print('api_key', key)

api_url = 'https://www.googleapis.com/youtube/v3/videos'
query_data = {'part': 'snippet,statistics', 'fields': 'items(id,snippet(channelId,title,channelTitle),statistics)'}
item_list = ['title', 'channelTitle', 'viewCount', 'likeCount', 'dislikeCount']
NETLOCS = ['www.youtube.com', 'youtu.be']

def check_url(url):
    u = urlparse(url)
    if u.netloc in NETLOCS:
        return url

def extract_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]

async def get_stats(id):
    query_str = urlencode({'key': key, 'id': id, **query_data})
    req_url = api_url + '?' + query_str
    async with aiohttp.ClientSession() as session:
        async with session.get(req_url) as resp:
            data = await resp.json()
        session.close()
    try:
        nest_dict = data['items'][0]
        flat_dict = {**nest_dict['statistics'], **nest_dict['snippet']}
        result = 'Yotube: ' + ' '.join(['%s: %s' % (item, flat_dict.get(item)) for item in item_list])
        return result
    except:
        pass

async def run(url):
    if check_url(url):
        id = extract_id(url)
        if id:
            res = await get_stats(id)
            return res
