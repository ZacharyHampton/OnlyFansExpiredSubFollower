import sys
from dataclasses import dataclass
import requests
import requests.cookies
from http.cookiejar import Cookie, CookieJar
from urllib.parse import urlparse
import hashlib
import time


class Account:
    def __init__(self, cookies: str, xbcSha1: str):
        self.cookies: str = cookies
        self.xbcSha1: str = xbcSha1
        self._Session: requests.Session = requests.Session()
        self._addCookies()

    def _addCookies(self):
        cookies = self.cookies.split("; ")
        for cookie in cookies:
            k, v = cookie.split("=")
            self._Session.cookies.set(k, v, domain=".onlyfans.com")

    def getUserId(self):
        for cookie in self._Session.cookies:
            if cookie.name == 'auth_id':
                return cookie.value

    #: taken from https://github.com/DIGITALCRIMINAL/OnlyFans
    def _createSignedHeaders(self, url: str, referer: str = None):
        userId = self.getUserId()
        dynamicRules = requests.get(
            'https://raw.githubusercontent.com/DATAHOARDERS/dynamic-rules/main/onlyfans.json').json()
        final_time = str(int(round(time.time())))
        path = urlparse(url).path
        query = urlparse(url).query
        path = path if not query else f"{path}?{query}"
        msg = "\n".join([dynamicRules["static_param"], final_time, path, str(userId)])
        message = msg.encode("utf-8")
        hash_object = hashlib.sha1(message)
        sha_1_sign = hash_object.hexdigest()
        sha_1_b = sha_1_sign.encode("ascii")
        checksum = (
                sum([sha_1_b[number] for number in dynamicRules["checksum_indexes"]])
                + dynamicRules["checksum_constant"]
        )

        headers = {
            "sign": dynamicRules["format"].format(sha_1_sign, abs(checksum)),
            "time": final_time,
            "app-token": dynamicRules["app_token"],
            'x-bc': self.xbcSha1,
            'user-id': str(userId),
            'referer': referer if referer else url,
            'authority': 'onlyfans.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-US,en;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'sec-ch-ua': '".Not/A)Brand";v="99", "Google Chrome";v="103", "Chromium";v="103"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36',
        }
        return headers

    def followExpired(self):
        url = 'https://onlyfans.com/api2/v2/subscriptions/count/all'
        headers = self._createSignedHeaders(url, 'https://onlyfans.com/my/subscribers/expired')
        response = self._Session.get(url, headers=headers)
        if response.status_code == 200:
            expiredAccounts = response.json()['subscribers']['expired']
        else:
            print(f'Failed to get subscriber count. Error: {response.status_code}, response text: {response.text}')
            return

        def getSubscribers(o: int):
            u = 'https://onlyfans.com/api2/v2/subscriptions/subscribers?limit=20&offset={}&sort=desc&field=last_activity&type=expired'.format(
                o)
            h = self._createSignedHeaders(u, 'https://onlyfans.com/my/subscribers/expired')
            r = self._Session.get(u, headers=h)
            if r.status_code != 200:
                print(f'Failed to get subscribers. Error: {r.status_code}, response text: {r.text}')
                getSubscribers(o)

            return r

        def subscribeToUser(userId):
            u = 'https://onlyfans.com/api2/v2/users/{}/subscribe'.format(userId)
            h = self._createSignedHeaders(u, 'https://onlyfans.com/my/subscribers/expired')
            r = self._Session.post(u, headers=h, json={"source": "fans"})
            if r.status_code != 200:
                if r.json()['error']['message'] == "Daily limit exceeded. Please try again later.":
                    print('Daily limit reached.')
                    sys.exit(0)

                if r.json()['error']['message'] == "Too many requests...":
                    print('Too many requests.')
                    time.sleep(5)
                    subscribeToUser(userId)

                print(f'Failed to follow {account["username"]}, Error: {r.status_code}, response text: {r.text}')
                time.sleep(1)
                subscribeToUser(userId)
            else:
                print('[{}] Followed account.'.format(account['username']))

        for offset in range(0, expiredAccounts, 20):
            response = getSubscribers(offset)
            for account in response.json():
                print('[{}] Reviewing account...'.format(account['username']))

                if account['subscribePrice'] != 0:
                    print('[{}] Account is not free'.format(account['username']))
                    continue

                if account['subscribedBy']:
                    print('[{}] Account is already subscribed'.format(account['username']))
                else:
                    subscribeToUser(account['id'])
                    time.sleep(1)

