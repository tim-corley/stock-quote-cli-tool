from decouple import config
import datetime
import requests
import pandas

auth_token = config('FINNHUB_KEY')


# PRINTS ALL AVAILABLE LISTING TO A TEXT FILE IN CURRENT DIR
def get_all_companies(token):
    try:
        data = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(token), timeout=10)
        if data.status_code == 200:
            all_listings = data.json()
            pandas.set_option('display.max_rows', None)
            formatted_listings = pandas.DataFrame(all_listings)
            formatted_listings.sort_values(by=['symbol'], ascending=True, inplace=True, ignore_index=True)
            available_listings = open('./data/available_listings.txt', 'w')
            available_listings.write(str(formatted_listings))
            available_listings.close()
            print('List of all available companies created!')
        else:
            print('Check Status Code: ', data.status_code)
    except requests.ConnectionError as e:
        print("\nConnection Error. Couldn\'t Fetch Data.\n")
        print(str(e))
        pass
    except requests.Timeout as e:
        print("\nTimeout Error\n")
        print(str(e))
        pass
    except requests.RequestException as e:
        print("\nSomething Went Wrong\n")
        print(str(e))
        pass


# RETURNS STOCK SYMBOL FOR COMPANY (PASSED IN BY NAME)
def get_company_symbol(company_name, token):
    try:
        data = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(token), timeout=10)
        if data.status_code == 200:
            all_listings = data.json()
            for listing in all_listings:
                for key, val in listing.items():
                    # if val == 'APPLE INC':
                    if company_name in val:
                        return listing['symbol']
        else:
            print('Check Status Code: ', data.status_code)
    except requests.ConnectionError as e:
        print("\nConnection Error. Couldn\'t Fetch Data.\n")
        print(str(e))
        pass
    except requests.Timeout as e:
        print("\nTimeout Error\n")
        print(str(e))
        pass
    except requests.RequestException as e:
        print("\nSomething Went Wrong\n")
        print(str(e))
        pass


# RETURNS STOCK QUOTE DATA (VIA A DICT) FOR A COMPANY
def get_stock_quote(company_name, token):
    ticker_symbol = get_company_symbol(company_name, auth_token)
    data = requests.get('https://finnhub.io/api/v1/quote?symbol={}&token={}'.format(ticker_symbol, token), timeout=10)
    if data.status_code == 200:
        stock_quote = data.json()
        return stock_quote
    else:
        print('Check Status Code: ', data.status_code)


# RETURNS LATEST STOCK PERFORMANCE (GAIN / LOSS PERCENTAGE)
def calculate_stock_performance(company_name, token):
    stock_data = get_stock_quote(company_name, token)
    perf = round(((stock_data['c'] - stock_data['pc']) / stock_data['c']) * 100, 2)
    dt = datetime.datetime.fromtimestamp(stock_data['t']).strftime("%Y-%m-%d %H:%M:%S")
    return '{} | {}%'.format(str(dt), str(perf))


def format_quote_data(stock_dict):
    formatted_dict = {}
    for key, val in stock_dict.items():
        if key == 'c':
            formatted_dict['CURRENT'] = '${:,.2f}'.format(val)
        elif key == 'h':
            formatted_dict['HIGH'] = '${:,.2f}'.format(val)
        elif key == 'l':
            formatted_dict['LOW'] = '${:,.2f}'.format(val)
        elif key == 'o':
            formatted_dict['OPEN'] = '${:,.2f}'.format(val)
        elif key == 'pc':
            formatted_dict['PREV CLOSE'] = '${:,.2f}'.format(val)
        elif key == 't':
            formatted_dict['DATETIME'] = datetime.datetime.fromtimestamp(val).strftime("%Y-%m-%d %H:%M:%S")
        else:
            print('ERROR!')
    return formatted_dict


# get_all_companies(auth_token)

# ticker_symbol = get_company_symbol('APPLE INC', auth_token)
# print(ticker_symbol)

# company_stock_quote = get_stock_quote(company, auth_token)
# print(company_stock_quote)

# current_stock_data = calculate_stock_performance(company, auth_token)
# print(current_stock_data)

# demo = {'c': 115.07, 'h': 116.55, 'l': 114.74, 'o': 116.39, 'pc': 115.75, 't': 1603464462}
# test = format_quote_data(demo)
# print(test)



