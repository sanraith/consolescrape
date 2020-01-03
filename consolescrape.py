import datetime
import logging
import pickle
import requests
from collections import namedtuple
from lxml import html
from requests import RequestException


class Game:
    def __init__(self, title):
        self.title = title
        self._states = []

    @property
    def state(self):
        return self._states[-1]

    @property
    def states(self):
        return list(self._states)

    @property
    def creation_date(self):
        return self._states[0].timestamp

    def add_state(self, new_state):
        if len(self._states) > 0:
            if all([self.state[x] == new_state[x] for x in range(1, len(GameState._fields))]):
                return  # new state is the same as the last excluding timestamp
        self._states.append(new_state)


GameState = namedtuple("GameState", ["timestamp", "price", "in_stock"])


class Scraper:
    def __init__(self):
        self.time_now = datetime.datetime.now()

    @staticmethod
    def load_url(url, iscached):
        if iscached == True:
            raise NotImplementedError("Caching is not implemented.")
        page = requests.get(url)
        content = page.content
        logging.info("Loaded page from the internet.")
        return content

    @staticmethod
    def trim_elem(elements):
        return str(elements[0]).strip()

    def scrape_page(self, content):
        states = {}
        tree = html.fromstring(content)
        cards = tree.xpath("//div[contains(@class, 'content')]//article[contains(@class, 'card')]")
        for card in cards:
            title = self.trim_elem(card.xpath(".//h3[@class='product-title']/a/text()"))
            price = self.trim_elem(card.xpath(".//div[@class='price']/div[contains(@class, 'now')]/text()"))
            in_stock = bool(card.xpath(".//li[contains(@class, 'stock-info') and contains(text(), 'Készleten')]"))
            try:
                price = int(price.replace(" ", ""))
            except ValueError:
                price = None
            states[title] = GameState(self.time_now, price, in_stock)
        return states

    def fetch_game_states(self, games_dict):
        page_index = 0
        error_count = 0
        while True:
            page_index += 1
            url = "https://www.konzolvilag.hu/switch/jatekok/oldal-{}".format(page_index)
            print("Loading page: {} ".format(url), end="")
            try:
                content = self.load_url(url, iscached=False)
                game_states = self.scrape_page(content)
                print("Found {} games.".format(len(game_states)))
            except ValueError:
                break
            except RequestException:
                error_count += 1
                if error_count > 10:
                    break
                print("Error #{}. Retrying....".format(error_count))
                page_index -= 1
                continue
            if not game_states:
                print("Done.")
                break

            for title, game_state in game_states.items():
                if title not in games_dict:
                    games_dict[title] = Game(title)
                games_dict[title].add_state(game_state)
        return games_dict

    def print_available_games(self, games):
        available_games = list(filter(lambda x: x.state.price and x.state.in_stock, games))
        max_title_length = max([len(x.title) for x in available_games])
        max_price_length = max([len(str(x.state.price)) for x in available_games])
        print("\nGames: {}, available: {}.".format(len(games), len(available_games)))
        for game in sorted(available_games, key=lambda x: x.title):
            padded_title = game.title.ljust(max_title_length)
            padded_price = str(game.state.price).rjust(max_price_length)

            prev_price = next((x.price for x in reversed(game.states) if x.price != game.state.price), None)
            if prev_price:
                change_chars = "↑↑" if game.state.price > prev_price else "↓↓"
                prev_price = " {} from {} Ft".format(change_chars, prev_price) if prev_price else ""
            else:
                prev_price = ""

            print("{title} - {price} Ft [{timestamp}]{change}".format(
                title=padded_title, price=padded_price, timestamp=game.state.timestamp.strftime("%y.%m.%d. %H:%M"), change=prev_price))

    def print_last_changes(self, games):
        timestamps = {state.timestamp for game in games for state in game.states}
        if len(timestamps) <= 1:
            return

        last_date = max([x.state.timestamp for x in games])
        print("\nLast changes [{}]:".format(last_date.strftime("%y.%m.%d. %H:%M")))
        changed_games = sorted(filter(lambda x: x.state.timestamp == last_date, games), key=lambda x: x.title)
        max_title_length = max([len(x.title) for x in changed_games])
        for game in changed_games:
            stock_change = ""
            price_change = ""
            if len(game.states) == 1:
                stock_change = "Added."
            else:
                s1 = game.states[-2]
                s2 = game.state
                if s1.price != s2.price:
                    price_change = "{} => {} Ft ".format(s1.price, s2.price)
                if s1.in_stock != s2.in_stock:
                    stock_change = "Now {}. ".format("available" if s2.in_stock else "unavailable")

            state_str = "{n} - {a}{p}".format(n=game.title.ljust(max_title_length), p=price_change, a=stock_change)
            print(state_str)

    def load_db(self):
        try:
            with open("games.db", "rb") as fb:
                games_dict = pickle.load(fb)
        except FileNotFoundError:
            games_dict = {}
        return games_dict

    def save_db(self, games_dict):
        with open("games.db", "wb") as fb:
            pickle.dump(games_dict, fb)


def main():
    scraper = Scraper()
    games_dict = scraper.load_db()
    scraper.fetch_game_states(games_dict)
    scraper.print_available_games(games_dict.values())
    scraper.print_last_changes(games_dict.values())
    scraper.save_db(games_dict)


if __name__ == "__main__":
    main()
