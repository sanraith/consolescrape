import logging
import requests
import datetime
import pickle
from collections import namedtuple
from lxml import html


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


def load_url(url, iscached):
    if iscached == True:
        raise NotImplementedError("Caching is not implemented.")
    page = requests.get(url)
    content = page.content
    logging.info("Loded page from the internet.")
    return content


def trim_elem(elements):
    return str(elements[0]).strip()


def scrape_page(content):
    states = {}
    time_now = datetime.datetime.now()
    tree = html.fromstring(content)
    cards = tree.xpath("//div[contains(@class, 'content')]//article[contains(@class, 'card')]")
    for card in cards:
        title = trim_elem(card.xpath(".//h3[@class='product-title']/a/text()"))
        price = trim_elem(card.xpath(".//div[@class='price']/div[contains(@class, 'now')]/text()"))
        in_stock = bool(card.xpath(".//li[contains(@class, 'stock-info') and contains(text(), 'Készleten')]"))
        try:
            price = int(price.replace(" ", ""))
        except ValueError:
            price = None
        states[title] = GameState(time_now, price, in_stock)
    return states


def fetch_game_states(games_dict):
    page_index = 0
    while True:
        page_index += 1
        url = "https://www.konzolvilag.hu/switch/jatekok/oldal-{}".format(page_index)
        print("Loading page: {}".format(url))
        try:
            content = load_url(url, iscached=False)
            game_states = scrape_page(content)
        except ValueError:
            break
        if not game_states:
            print("Done.\n")
            break

        for title, game_state in game_states.items():
            if title not in games_dict:
                games_dict[title] = Game(title)
            games_dict[title].add_state(game_state)
    return games_dict


def print_available_games(games):
    available_games = list(filter(lambda x: x.state.price and x.state.in_stock, games))
    max_title_length = max([len(x.title) for x in available_games])
    max_price_length = max([len(str(x.state.price)) for x in available_games])
    last_change = max([x.state.timestamp for x in available_games])
    for game in sorted(available_games, key=lambda x: x.title):
        padded_title = game.title.ljust(max_title_length)
        padded_price = str(game.state.price).rjust(max_price_length)
        print("{title} {price} Ft [{timestamp}]".format(
            title=padded_title, price=padded_price, timestamp=game.state.timestamp))
    print("\nGames: {}, available: {}, last change: {}".format(len(games), len(available_games), last_change))


def load_db():
    try:
        with open("games.db", "rb") as fb:
            games_dict = pickle.load(fb)
    except FileNotFoundError:
        games_dict = {}
    return games_dict


def save_db(games_dict):
    with open("games.db", "wb") as fb:
        pickle.dump(games_dict, fb)


def main():
    games_dict = load_db()
    fetch_game_states(games_dict)
    print_available_games(games_dict.values())
    save_db(games_dict)


if __name__ == "__main__":
    main()
