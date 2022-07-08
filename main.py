from account import Account


def main():
    cookies = input('Cookies: ')
    xbcSha1 = input('X-BC Header or bcTokenSha in localStorage: ')

    account = Account(cookies, xbcSha1)
    account.followExpired()


if __name__ == '__main__':
    main()

