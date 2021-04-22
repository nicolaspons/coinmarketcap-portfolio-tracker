import sys
import getopt
import requests
import pandas as pd
from bs4 import BeautifulSoup


def scrape(MIN_MARKET_CAP, MAX_MARKET_CAP, save):
    URL = 'https://coinmarketcap.com/cryptocurrency-category/'
    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Gets the portfolios
    portfolios = set([a['href'] for a in soup.find_all(
        'a', {'class': 'cmc-link'}) if 'portfolio' in a['href']])

    portfolios = [p for p in portfolios if p.startswith('/view/')]

    print('{} portfolios found'.format(len(portfolios)))

    coins_tracker = {}
    market_caps_tracker = {}

    for portfolio in portfolios:
        URL = 'https://coinmarketcap.com/{}/'.format(portfolio)

        print('Scraping the url: {}'.format(URL))

        page = requests.get(URL)
        soup = BeautifulSoup(page.content, 'html.parser')
        tbody = soup.find('tbody')
        # Gets the coins listed in the current portfolio
        coins = [p.text for p in
                 tbody.find_all('p', {'class': 'sc-1eb5slv-0 iJjGCS'})]
        print('Found {} coins'.format(len(coins)))
        # Gets the market caps of the coins listed in the current portfolio
        market_caps = [p.text for p in tbody.find_all(
            'p', {'class': 'sc-1eb5slv-0 kDEzev'})]
        # Converts the string market cap values to int
        for i in range(len(market_caps)):
            market_caps[i] = int(
                ''.join(c for c in market_caps[i] if c.isdigit()))
        # Saves the coins and their corresponding market caps to a dict
        # Counts the occurrence of coins
        for i, coin in enumerate(coins):
            coins_tracker[coin] = coins_tracker.get(coin, 0) + 1
            if coin not in market_caps_tracker:
                market_caps_tracker[coin] = market_caps[i]
    # Builds the DataFrame
    data = {}
    for coin in coins_tracker.keys():
        data[coin] = [coins_tracker[coin], market_caps_tracker[coin]]

    df = pd.DataFrame.from_dict(
        data, orient='index', columns=['occ', 'market_cap'])

    # Selects the coins with a specific market cap
    selected = df[(df['market_cap'] > MIN_MARKET_CAP) &
                  (df['market_cap'] < MAX_MARKET_CAP)]

    # Sorts the coins from the most popular to the least one
    selected = selected.sort_values(by=['occ'], ascending=False)

    # Saves the DataFrame
    if save:
        selected.to_csv('tracker_coins.csv')
    else:
        print(selected)


def main(argv):
    MIN_MARKET_CAP = 100000000
    MAX_MARKET_CAP = 450000000
    save = False

    try:
        opts, args = getopt.getopt(argv, 'hs', ['min=', 'max=', 'save'])
    except getopt.GetoptError:
        print('tracking.py --min=<MIN_MARKET_CAP> --max=<MIN_MARKET_CAP> -s')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('tracking.py --min=<MIN_MARKET_CAP> --max=<MIN_MARKET_CAP> -s')
            sys.exit(0)
        elif opt in ['-m', '--min']:
            MIN_MARKET_CAP = int(arg)
        elif opt in ['-M', '--max']:
            MAX_MARKET_CAP = int(arg)
        elif opt in ['-s', '--save']:
            save = True

    print('Scrapping coins with a market cap beetween {} and {}...'.format(
        MIN_MARKET_CAP, MAX_MARKET_CAP))
    scrape(MIN_MARKET_CAP, MAX_MARKET_CAP, save)


if __name__ == '__main__':
    main(sys.argv[1:])
