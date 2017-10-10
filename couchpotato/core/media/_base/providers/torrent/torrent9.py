from bs4 import BeautifulSoup
from couchpotato.core.helpers.variable import getTitle, tryInt
from couchpotato.core.logger import CPLog
from couchpotato.core.helpers.encoding import simplifyString, tryUrlencode
from couchpotato.core.media._base.providers.torrent.base import TorrentProvider
import cookielib
import re
import traceback
import urllib
import urllib2
import unicodedata
from couchpotato.core.helpers import namer_check
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

log = CPLog(__name__)


class Base(TorrentProvider):
    urls = {
        'site': 'http://www.torrent9.pe/',
        'search': 'http://www.torrent9.pe/search_torrent/',
    }

    def _search(self, movie, quality, results):
        TitleStringReal = (getTitle(movie['info']) + ' ' + simplifyString(quality['identifier'])).replace('-',' ').replace(' ',' ').replace(' ',' ').replace(' ',' ').encode("utf-8")
        log.info('Title %s', TitleStringReal)
        URL = ((self.urls['search']) + TitleStringReal.replace('.', '-').replace(' ', '-') + '.html,trie-seeds-d').encode('utf-8')

        req = urllib2.Request(URL, headers={'User-Agent' : "Mozilla/5.0"})
        log.info('opening url %s', URL)
        data = urllib2.urlopen(req,timeout=500)
        log.info('data retrieved')
        id = 1000

        if data:
            try:
                html = BeautifulSoup(data)
                torrent_rows = html.findAll('tr')

                for result in torrent_rows:
                    try:
                        if not result.find('a'):
                            continue

                        title = result.find('a').get_text(strip=False)
                        log.info('found title %s',title)

                        testname = namer_check.correctName(title.lower(),movie)
                        if testname == 0:
                            log.info('%s not match %s',(title.lower(),movie['info']['titles']))
                            continue
                        log.info('title %s match',title)

                        tmp = result.find("a")['href'].split('/')[-1].replace('.html', '.torrent').strip()
                        download_url = (self.urls['site'] + 'get_torrent/{0}'.format(tmp) + ".torrent")
                        detail_url = (self.urls['site'] + 'torrent/{0}'.format(tmp))
                        log.debug('download_url %s',download_url)

                        if not all([title, download_url]):
                            continue

                        seeders = int(result.find(class_="seed_ok").get_text(strip=True))
                        leechers = int(result.find_all('td')[3].get_text(strip=True))
                        size = result.find_all('td')[1].get_text(strip=True)

                        def extra_check(item):
                            return True

                        size = size.lower()
                        size = size.replace("go", "gb")
                        size = size.replace("mo", "mb")
                        size = size.replace("ko", "kb")
                        size = size.replace(' ','')
                        size = self.parseSize(str(size))

                        new = {}
                        new['id'] = id
                        new['name'] = title.strip()
                        new['url'] = download_url
                        new['detail_url'] = detail_url
                        new['size'] = size
                        new['seeders'] = seeders
                        new['leechers'] = leechers
                        new['extra_check'] = extra_check
                        new['download'] = self.loginDownload
                        results.append(new)
                        log.info(results)
                        id = id + 1
                    except StandardError, e:
                        log.info('boum %s',e)
                    continue

            except AttributeError:
                log.debug('No search results found.')
        else:
            log.debug('No search results found.')
     
    def login(self):
        log.info('Try to login on torrent9')
        return True

    def download(self, url='', nzb_id=''):
        log.debug('download %s',url)
        req = urllib2.Request(url, headers={'User-Agent' : "Mozilla/5.0"})
        try:
            return urllib2.urlopen(req).read()
        except:
            log.error('Failed downloading from %s: %s', (self.getName(), traceback.format_exc()))

    loginDownload = download

config = [{
    'name': 'torrent9',
    'groups': [{
            'tab': 'searcher',
            'list': 'torrent_providers',
            'name': 'torrent9',
            'description': 'See <a href="http://www.torrent9.pe/">Torrent9</a>',
            'icon': 'iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAABHNCSVQICAgIfAhkiAAAAgZJREFUOI2lkj9oE2EYxn93l/Quf440gXg4lBoEMd2MDuLSkk0R6hCnuqjUoR0c7FDo4Ca0CDo7uRRBqEMDXSLUUqRDiZM1NMEI1VKTlDZpUppccvc5nJp/KooPfMPH+z3P+zzv+8F/Quq8XIVEEOY0kASIzpoLlBKUV+CuCblfCjyF/P3V1Qi6jrCs7k4eD/X1dS5NTy9tQaJD2MFDkA23W8UwQFGQRJcB0DS0cBg/DPY4a0OVZcHeHihKf1ifD6pVfGD/VmBAUeDwEGQZLAskCVQV6nVYW+M4lSLQo9stoKpQLoNtO2QhYHsbkkmOczm+AP5eBy/BfwRDn8GHJLkpFp3utRpkMpDLwckJvlCIM9Uqg6YZeAAj58E1CVlXCaaigcCjsWhU8Xq9UCo5lisVx4FhODFkGbdpMtlqXa4IsVUHYkLcVlbg3ddGo3AzErl2emLCGaCmwcAAuL4ntCxoNpFsG8O2odlkXojF17CgAK2PsJna2Xk/ViyOh0dHXWhaewaW1T6mSb5a5V6rtbAMU4D5c18FyCzu7i5fyWZvDMfjOh4PNBpd5A/5vLheq93ZhMc/eF0Lr0NhaX8/eS6djo/EYqfQdUekUuHNxsZR4uDg1id40f9J+qE/CwTeitlZIWZmxKtQqOSFi39D7IQy5/c/fxIMpoGhfyUDMAwXzsL4n958A9jfxsJ8X4WQAAAAAElFTkSuQmCC',
            'wizard': True,
            'options': [{
                    'name': 'enabled',
                    'type': 'enabler',
                    'default': False,
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
                    'default': 10,
                    'description': 'Starting score for each release found via this provider.',
                }],
        },],
}]
