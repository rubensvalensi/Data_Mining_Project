import bs4 as bs
import urllib.request
import pandas as pd
import time
import datetime
from os import path
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = '/Users/mac/PycharmProjects/itcpython/chromedriver/chromedriver'
PATH_WEBSITE = 'https://www.tradingview.com'
PATH = 'https://www.tradingview.com/markets/stocks-usa/market-movers-active/'
PARSE_METHOD = 'html.parser'
EMPTY_STR = ' '
REPLACE_1 = '\n\n'
REPLACE_2 = '\n\t\t\t\t\t\t\t\t'
REPLACE_3 = '\n'
REPLACE_4 = '\n\t\t\t'
REPLACE_5 = '\n\t\t\t\t\t\t'
TAG_1 = 'tr'
TAG_2 = 'td'
TAG_3 = 'a'
TAG_4 = 'div'
TAG_5 = 'class'
TAG_6 = 'tv-widget-description__text'
TAG_7 = 'tv-widget-fundamentals__item'
TAG_7_1 = 'tv-widget-fundamentals__row'
TAG_8 = 'span'
TAG_9 = 'tv-widget-fundamentals__label apply-overflow-tooltip'
TAG_10 = 'tv-widget-fundamentals__value apply-overflow-tooltip'
IMG_SIGN = 1
FILE_101 = '\STOCK_FILES\data_complete_stocks.csv'
PATH_FILES = '\STOCK_FILES\{}_{}.csv'
DATE = '%Y-%m-%d'
HOUR = '%H:%M:%S'
SYMBOLS = 'Symbols'
NAMES = 'Names'
DESCRIPTIONS = "About the company"
PRICES = 'Prices'
PERCENT_CHANGES = '% Change'
VOLUME = 'Volume'
MARKET_CAP = 'Market Cap'
ACTUAL_TIME = 'Actual Time'
ENT_VAL = 'Entreprise value'
TOT_SH = 'Total share'
EMPLOYEES = 'Num of employees'
TOT_DEBT = 'Total debt'
TOT_ASS = 'Total asset'
AVG_VOL = 'Average volume'
TOP_PRICE = 'Top year price'
LOW_PRICE = 'Low year price'
DIV = 'Dividend'
LAST_REV = 'Last year revenue'
TOT_REV = 'Total year revenue'
CASH_FLOW = 'Free cash flow'


def scrape_page(soup):
    lines = []
    prices = []
    percent_changes = []
    volume = []
    market_cap = []
    actual_hour_lst = []
    link = []

    for tr in soup.find_all(TAG_1)[1:]:
        tds = tr.find_all(TAG_2)
        for i, td in enumerate(tds):
            if td.find('a', href=True) != None and i == 0:  # TODO expliquer a haim trouver au hasard
                a = td.find('a', href=True)
                url = PATH_WEBSITE + a.get('href')
                link.append(url)
        symbols_and_names = (tds[0].text).replace(REPLACE_1, EMPTY_STR).replace(REPLACE_2, EMPTY_STR).strip(
                REPLACE_3).strip()
        lines.append(symbols_and_names.split())
        prices.append(tds[1].text)
        percent_changes.append(tds[2].text)
        volume.append(tds[5].text)
        market_cap.append(tds[6].text)
        actual_hour_lst.append(datetime.datetime.now().strftime(HOUR))
    return lines, prices, percent_changes, volume, market_cap, actual_hour_lst, link


def parse_symbols_names(lines):
    """
    parse names symbols on the main page
    """
    names = []
    symbols = []
    for word in lines:
        if len(word[0]) != IMG_SIGN:
            symbols.append(word[0])
            names.append(EMPTY_STR.join(word[1:]))
        else:
            symbols.append(word[1])
            names.append(EMPTY_STR.join(word[2:]))
    return names, symbols


def get_descritption(url):
    """
    scrape one page
    """
    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    driver = webdriver.Chrome(options=options, executable_path=DRIVER_PATH)


    driver.get(url)
    source = driver.page_source
    soup = bs.BeautifulSoup(source, PARSE_METHOD)
    driver.quit()
    financial = []
    descriptions = []

    try:
        for text in soup.find(TAG_4, {TAG_5: TAG_6}):
            descriptions.append(text.strip(REPLACE_4))
    except TypeError:
        descriptions.append("Don't have description")

    try:

        for span in soup.find_all(TAG_4, {TAG_5: TAG_7_1}):
            title = span.find(TAG_8, {TAG_5: TAG_9})
            value = span.find(TAG_8, {TAG_5: TAG_10})
            financial.append({title.text.strip(REPLACE_5): value.text.strip(REPLACE_5)})


        description = descriptions[0]
        enterprise_value = financial[1]
        total_shares = financial[3]
        nb_employees = financial[4]
        total_debt = financial[14]
        total_asset = financial[15]
        avg_volume = financial[20]
        top_year_price = financial[22]
        low_year_price = financial[23]
        dividend = financial[24]
        last_year_revenue = financial[38]
        total_revenue = financial[39]
        free_cash_flow = financial[40]

        return description, enterprise_value, total_shares, nb_employees, total_debt, total_asset, avg_volume, top_year_price, \
               low_year_price, dividend, last_year_revenue, total_revenue, free_cash_flow

    except Exception:
        enterprise_value = {'Enterprise Value (MRQ)': 'NaN'}
        total_shares = {'Total Shares Outstanding (MRQ)': 'NaN'}
        nb_employees = {'Number of Employees': 'NaN'}
        total_debt = {'Total Debt (MRQ)': 'NaN'}
        total_asset = {'Total Assets (MRQ)': 'NaN'}
        avg_volume = {'Average Volume (10 day)': 'NaN'}
        top_year_price = {'52 Week High': 'NaN'}
        low_year_price ={'52 Week Low': 'NaN'}
        dividend = {'Dividends Paid (FY)': 'NaN'}
        last_year_revenue = {'Last Year Revenue (FY)': 'NaN'}
        total_revenue = {'Total Revenue (FY)': 'NaN'}
        free_cash_flow = {'Free Cash Flow (TTM)': 'NaN'}
        return descriptions[0], enterprise_value, total_shares, nb_employees, total_debt, total_asset, avg_volume, top_year_price, \
               low_year_price, dividend, last_year_revenue, total_revenue, free_cash_flow


def scrape_inner_page(links):
    """
    scrape all the inners page
    """
    descriptions = []
    enterprise_value = []
    total_shares = []
    nb_employees = []
    total_debt = []
    total_asset = []
    avg_volume = []
    top_year_price = []
    low_year_price = []
    dividend = []
    last_year_revenue = []
    total_revenue = []
    free_cash_flow = []

    for url in links:
        desc, ent_val, tot_sh, nb_emp, tot_dbt, tot_ass, avg_vol, top_ye_price, low_pri, divid, last_rev, tot_rev, cash_flow = get_descritption(
            url)
        descriptions.append(desc)
        enterprise_value.append(ent_val)
        total_shares.append(tot_sh)
        nb_employees.append(nb_emp)
        total_debt.append(tot_dbt)
        total_asset.append(tot_ass)
        avg_volume.append(avg_vol)
        top_year_price.append(top_ye_price)
        low_year_price.append(low_pri)
        dividend.append(divid)
        last_year_revenue.append(last_rev)
        total_revenue.append(tot_rev)
        free_cash_flow.append(cash_flow)
    return descriptions, enterprise_value, total_shares, nb_employees, total_debt, total_asset, avg_volume, top_year_price, low_year_price, dividend, last_year_revenue, total_revenue, free_cash_flow


def parse_file(path):
    """

    :param path: the path of the website we want to scrap
    :return: a dictionary with the scrapped elements
    """
    source = urllib.request.urlopen(path).read()
    soup = bs.BeautifulSoup(source, PARSE_METHOD)
    lines, prices, percent_changes, volume, market_cap, actual_hour_lst, links = scrape_page(soup)
    names = parse_symbols_names(lines)[0]
    symbols = parse_symbols_names(lines)[1]
    descriptions, enterprise_value, total_shares, nb_employees, total_debt, total_asset, avg_volume, top_year_price, \
    low_year_price, dividend, last_year_revenue, total_revenue, free_cash_flow = scrape_inner_page(links)

    data =  create_df(symbols, names, descriptions, prices, percent_changes, market_cap, volume, actual_hour_lst,
                     enterprise_value, total_shares, nb_employees, total_debt, total_asset,
                     avg_volume, top_year_price, low_year_price, dividend, last_year_revenue,
                     total_revenue, free_cash_flow)
    return data


def create_df(symbols, names, descriptions, prices, percent_changes, market_cap, volume, time, enterprise_value,
              total_shares, nb_employees, total_debt, total_asset,
              avg_volume, top_year_price, low_year_price, dividend, last_year_revenue,
              total_revenue, free_cash_flow):
    # extracting the data into DataFrame
    general_infos_df = pd.DataFrame(
        {SYMBOLS: symbols, NAMES: names, DESCRIPTIONS: descriptions, PRICES: prices, PERCENT_CHANGES: percent_changes,
         MARKET_CAP: market_cap, VOLUME: volume, ACTUAL_TIME: time})

    print(general_infos_df)
    print()
    print("ùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùùù")

    print()

    financial_page_df = pd.DataFrame(
        {SYMBOLS: symbols, ENT_VAL: enterprise_value, TOT_SH: total_shares, EMPLOYEES: nb_employees,
         TOT_DEBT: total_debt, TOT_ASS: total_asset,
         AVG_VOL: avg_volume, TOP_PRICE: top_year_price, LOW_PRICE: low_year_price, DIV: dividend,
         LAST_REV: last_year_revenue,
         TOT_REV: total_revenue, CASH_FLOW: free_cash_flow, ACTUAL_TIME: time})

    print(financial_page_df)
    # saving the data into csv so we can update the csv
    # data.to_csv(os.getcwd() + FILE_101)
    return general_infos_df, financial_page_df




if __name__ == '__main__':
    parse_file(PATH)

