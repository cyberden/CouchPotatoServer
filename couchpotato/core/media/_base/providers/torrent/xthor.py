from couchpotato.core.helpers.variable import tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
from couchpotato.core.helpers import namer_check
import json
import re
import unicodedata

log = CPLog(__name__)


class Base(TorrentProvider):

    urls = {
        'search': 'https://api.xthor.tk/?passkey=%(passkey)s&search=&category=&freeleech=&tmdbid=%(tmdbid)s&size=',
        'detail': 'https://xthor.tk/details.php?id=%s'
    }

    def _search(self, movie, quality, results):           
        url = self.urls['search'] % {'passkey': self.conf('passkey'), 'tmdbid': movie['info']['tmdb_id'] }
        data = self.getJsonData(url)

        if data[u'error'][u'code'] == 0 and 'torrents' in data:
            for currentresult in data['torrents']:
                new = {}

                new['id'] = currentresult['id']
                new['name'] = currentresult['name']
                new['url'] = currentresult['download_link']
                new['detail_url'] = self.urls['detail'] % currentresult['id']
                new['size'] = tryInt(currentresult['size']) / 1024 / 1024
                new['seeders'] = tryInt(currentresult['seeders'])
                new['leechers'] = tryInt(currentresult['leechers'])
                         
                results.append(new)
        return


config = [{
    'name': 'xthor',
    'groups': [{
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'xthor',
            'description': 'See <a href="https://xthor.tk/">xthor</a>',
            'icon' : 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAAACXBIWXMAAAsTAAALEwEAmpwYAAACRUlEQVR4nEWSS2/TQBSF752nHT+TJmmTtKVICIkFP4H/L7FBLBArpD5U+nIetWPH45m5wyIFzuboSN/ZfQh/wxgbJXk2mWfjWVpMIwEY3Prx9uH+tq7rEMIRw2NJKWfzVVIsWJyhTlk0Et5gGBKFksOvn9/v766PHw4AWuvlchlnSyw+AlNhfEXJGSBjQg6EZvc0mc6dte2+BgDOGFutzrWOgRcQFbD8jO++iLjEqKD2mZAHJoau0aPk0NR2MLwcl8X4EgBB51Cc8lGm2xvZPYj2jgVHfe0GQ0OHiDI9ada/2XS2xGQJagL5CoNVZlMuztI8jrDLLz8oKUHGgQKZLkqmaZYznZQkBWRTSCZMJ1GWyrQYXXzSk5XKptFswRiDeA5uYH0vVMq4kMA15mdifCmoD2ZnPPYWQnlhQHngqFIYtoAY3ADAGTJkSqBKpHnW6QQoeFU6YOHkyucr1+2DiECMACQAC+7AXLcbaSldTfU9E4pHZbj5SsTtvnM331zbBO9BJMBEoM57wzHQyeki1sp5G0wt8gXrqtBUrroeHn7YwZInQA3tsx36qrrnxpgyicbTuVAjaiu/uwUiiKeBSdtunWnB9PB6E1xfVXeHw4ETUd/tZ+OiHE9QJdS+2G7ruq3vm9BVfmihfQLf1fV6s1m/qTEMw+u2KrOoPHvPi/PgjTetbZ7soQ6HV3L9ZlNtNmsiejsAQN/3z48Pbl9FodMCOBKQPexf9/Wuql6apjnS/219G4hKKSEEIiPy1lrn3D+xj/kDN/1GOELQrVcAAAAASUVORK5CYII=',
            'wizard': True,
            'options': [{
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
                },
                {
                    'name': 'passkey',
                    'default': '',
                },
                {
                    'name': 'seed_ratio',
                    'label': 'Seed ratio',
                    'type': 'float',
                    'default': 1,
                    'description': 'Will not be (re)moved until this seed ratio is met.',
                },
                {
                    'name': 'seed_time',
                    'label': 'Seed time',
                    'type': 'int',
                    'default': 40,
                    'description': 'Will not be (re)moved until this seed time (in hours) is met.',
                },
                {
                    'name': 'extra_score',
                    'advanced': True,
                    'label': 'Extra Score',
                    'type': 'int',
                    'default': 0,
                    'description': 'Starting score for each release found via this provider.',
                }],
        },],
}]
