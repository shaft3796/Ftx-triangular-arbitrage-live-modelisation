from math import floor

from OpenBacktest.ObtUtility import Colors, divide
from ftx import FtxClient
import pandas as pd
import time


class FtxLiveClient:
    def __init__(self, api_key, api_secret, subaccount_name=""):
        self.client = None
        self.__login(api_key, api_secret, subaccount_name)

    # PUBLIC
    # get balance
    def get_balance(self, coin):
        jsonBalance = self.client.get_balances()
        if not jsonBalance:
            return 0
        pandaBalance = pd.DataFrame(jsonBalance)
        if pandaBalance.loc[pandaBalance['coin'] == coin].empty:
            return 0
        else:
            return float(pandaBalance.loc[pandaBalance['coin'] == coin]['availableWithoutBorrow'])

    def get_data(self, pair, resolution, limit, start_time, end_time):
        return pd.DataFrame(self.client.get_historical_data(
            pair,
            resolution,
            limit,
            start_time,
            end_time))

    def get_book(self, pair, unknow=1):
        return self.client.get_orderbook(pair, unknow)

    def get_buy_price(self, pair):
        return self.get_book(pair)['asks'][0][0]

    def get_sell_price(self, pair):
        return self.get_book(pair)['bids'][0][0]

    def get_size_info(self, pair):
        market = self.client.get_market(pair)
        return market['minProvideSize'], market['sizeIncrement']

    def get_current_price(self, pair):
        return self.client.get_market(pair)["price"]

    def get_buying_capacity(self, coin, token, amount=None):
        pair = token + "/" + coin
        balance = self.get_balance(coin)
        if amount is None:
            amount = balance
        elif amount > balance:
            print(Colors.YELLOW, "Advert, amount to large, reducing it. .")
            amount = balance

        return self.__truncate(divide(amount, self.get_current_price(pair)), 10)

    def get_selling_capacity(self, token, amount=None):
        balance = self.get_balance(token)
        if amount is None:
            amount = balance
        elif amount > balance:
            print(Colors.YELLOW, "Advert, amount too large, reducing it. .")
            amount = balance

        return amount

    def market_buy(self, pair: str, amount=None, silent=False):
        splited = pair.split("/")
        coin = splited[1]
        token = splited[0]
        first_token_balance = self.get_balance(token)
        capacity = self.get_buying_capacity(coin, token, amount)
        if not silent:
            print(Colors.PURPLE, "[ORDER]", Colors.GREEN, "Buying", capacity, token)
        order = self.client.place_order(
            market=pair,
            side="buy",
            price=None,
            size=capacity,
            type='market')
        if not silent:
            second_token_balance = self.get_balance(token)
            print(Colors.PURPLE, "[FILLED]", Colors.GREEN, second_token_balance - first_token_balance, token)

    def market_sell(self, pair: str, amount=None, silent=False):
        splited = pair.split("/")
        coin = splited[1]
        token = splited[0]
        first_token_balance = self.get_balance(token)
        capacity = self.get_selling_capacity(token, amount)
        if not silent:
            print(Colors.PURPLE, "[ORDER]", Colors.LIGHT_RED, "Selling", capacity, token)
        order = self.client.place_order(
            market=pair,
            side="sell",
            price=None,
            size=capacity,
            type='market')
        if not silent:
            second_token_balance = self.get_balance(token)
            print(Colors.PURPLE, "[FILLED]", Colors.LIGHT_RED, first_token_balance - second_token_balance, token)
        return order

    def extract_last_hour(self, dataframe):
        start_hour = dataframe["startTime"][len(dataframe["startTime"]) - 1]
        return start_hour.split("T")[1].split(":")[0]

    # PRIVATE
    # login
    def __login(self, api_key, api_secret, subaccount_name=""):
        self.client = FtxClient(api_key=api_key, api_secret=api_secret, subaccount_name=subaccount_name)

    # truncate
    def __truncate(self, n, decimals=0):
        r = floor(float(n) * 10 ** decimals) / 10 ** decimals
        return float(r)
