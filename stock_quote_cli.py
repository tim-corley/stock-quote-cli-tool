from __future__ import print_function, unicode_literals
from PyInquirer import style_from_dict, Token, prompt
import stock_quote_data
import requests
import pandas
import csv
import os

auth_token = stock_quote_data.auth_token


def search_companies(company_name, token):
    # extract answer string from dict returned by cli prompt
    company_name = company_name['company_name']
    results = []
    try:
        data = requests.get('https://finnhub.io/api/v1/stock/symbol?exchange=US&token={}'.format(token), timeout=10)
        if data.status_code == 200:
            all_listings = data.json()
            for listing in all_listings:
                for key, val in listing.items():
                    if key == 'description':
                        if company_name.lower() in val.lower():
                            results.append({'name': listing['description'], 'symbol': listing['symbol']})
            return results
        else:
            print('Check Status Code: ', data.status_code)
    except requests.ConnectionError as e:
        print("\nConnection Error. Couldn\'t Fetch Data.\n")
        print(str(e))
        pass


style = style_from_dict({
    Token.QuestionMark: '#12a37a bold',
    Token.Selected: '#12a37a bold',
    Token.Pointer: '#12a37a bold',
    Token.Instruction: '',  # default
    Token.Answer: '#12a37a bold',
    Token.Question: '',
})

questions01 = [
    {
        'type': 'input',
        'name': 'company_name',
        'message': 'Search for company name in listings: ',
    }
]

answer01 = prompt(questions01, style=style)
all_matches = search_companies(answer01, auth_token)


questions02 = [
    {
        'type': 'list',
        'name': 'select_company',
        'message': 'Several companies found for {}, please select one.'.format(answer01['company_name']),
        'choices': all_matches
    }
]


def generate_stock_results(company_name, token, pretty_print=True):
    data = stock_quote_data.format_quote_data(stock_quote_data.get_stock_quote(company_name['select_company'], token))
    data['COMPANY'] = company_name['select_company']
    data['DIFF'] = round(float(data['CURRENT'].lstrip('$')) - float(data['PREV CLOSE'].lstrip('$')), 2)
    data['PER'] = '{}%'.format(str(round((data['DIFF'] / int(float(data['CURRENT'].lstrip('$')))) * 100, 2)))
    if pretty_print:
        print(display_results(data))
        return data
    else:
        return data


# TAKES IN A DICT
def display_results(data):
    df = pandas.DataFrame.from_dict(data, orient='index')
    # df = pandas.DataFrame({'ONE': list(data.keys()), 'TWO': list(data.values())})
    return df


# # DIFFERENT APPROACH TO SHOW RESULT DATA
# def show_nested_results(company_name, token):
#   data = {'COMPANY': company_name['select_company'],
#   'DATA': stock_quote_data.format_quote_data(stock_quote_data.get_stock_quote(company_name['select_company'], token)),
#   'PERFORMANCE': {}}
#   data['PERFORMANCE'] = {'DIFF': round(float(data[
#   'DATA']['CURRENT'].lstrip('$')) - float(data['DATA']['PREV CLOSE'].lstrip('$')), 2), 'PER': '{}%'.format(str(round(
#   (round(float(data['DATA']['CURRENT'].lstrip('$')) - float(data['DATA']['PREV CLOSE'].lstrip('$')), 2) / int(float(
#   data['DATA']['CURRENT'].lstrip('$')))) * 100, 2)))}
#   df = pandas.DataFrame.from_dict(data, orient='index')
#   return df


def save_results(data):
    columns = list(data.keys())
    file = './data/ticker_history/{}.csv'.format(data['COMPANY'])
    file_check = os.path.exists(file)
    if file_check:
        with open(file, 'a', newline='') as record_file:
            writer = csv.DictWriter(record_file, fieldnames=columns)
            writer.writerow(data)
            record_file.close()
        print("Successfully appended data to existing csv. View file at: {}{}{}.csv".format(os.getcwd(), '/data/ticket_history/', data['COMPANY']))
    else:
        with open(file, 'w') as record_file:
            writer = csv.DictWriter(record_file, fieldnames=columns)
            writer.writeheader()
            writer.writerow(data)
            record_file.close()
        print("Successfully saved data to a new csv. View file at: {}{}{}.csv".format(os.getcwd(), '/data/ticket_history/', data['COMPANY']))


if len(all_matches) == 0:
    print('Unable to find this company in available listing.')
elif len(all_matches) == 1:
    company_dict = {'select_company': all_matches[0]['name']}
    ticker_data = generate_stock_results(company_dict, auth_token)
elif len(all_matches) > 1:
    answer02 = prompt(questions02, style=style)
    ticker_data = generate_stock_results(answer02, auth_token)


questions03 = [
    {
        'type': 'list',
        'name': 'save_data',
        'message': 'Would you like to save this data to ticker history?',
        'choices': ['Yes', 'No']
    }
]

answer03 = prompt(questions03, style=style)
if answer03['save_data'] == 'Yes':
    save_results(ticker_data)
elif answer03['save_data'] == 'No':
    print('OK - will not save this data.')


# result = generate_stock_results(answer02, auth_token)
# # print(result)
# save_results(result)
