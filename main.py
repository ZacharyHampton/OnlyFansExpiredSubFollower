from account import Account


def main():
    cookies = input('Cookies: ')
    xbcSha1 = input('X-BC Header or bcTokenSha in localStorage: ')
    userAgent = input('User-Agent: ')

    account = Account(cookies, xbcSha1, userAgent)
    account.followExpired()


if __name__ == '__main__':
    main()

