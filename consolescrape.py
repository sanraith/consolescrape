import logging
import requests
import datetime
from collections import namedtuple
from lxml import html


class Game:
    def __init__(self, title):
        self.title = title
        self.states = []

    @property
    def state(self):
        return self.states[-1]

    @property
    def creation_date(self):
        return self.states[0].timestamp


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
    games_dict = {}
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
        games_dict[title] = GameState(time_now, price, in_stock)
    return games_dict


def get_games(games_dict):
    page_index = 0
    while True:
        page_index += 1
        url = "https://www.konzolvilag.hu/switch/jatekok/oldal-{}".format(page_index)
        print("Loading page: {}".format(url))
        try:
            content = load_url(url, iscached=False)
            games_page = scrape_page(content)
        except ValueError:
            break
        if not games_page:
            print("Done.\n")
            break

        for title, game_state in games_page.items():
            if title not in games_dict:
                games_dict[title] = Game(title)
            games_dict[title].states.append(game_state)
    return games_dict


def print_available_games(games):
    available_games = list(filter(lambda x: x.state.price and x.state.in_stock, games))
    max_title_length = max([len(x.title) for x in available_games])
    max_price_length = max([len(str(x.state.price)) for x in available_games])
    for game in sorted(available_games, key=lambda x: x.title):
        padded_title = game.title.ljust(max_title_length)
        padded_price = str(game.state.price).rjust(max_price_length)
        print("{t} {p} Ft".format(t=padded_title, p=padded_price))
    print("\nGames: {}, available: {}.".format(len(games), len(available_games)))


def main():
    games_dict = {}  # todo persist
    get_games(games_dict)
    print_available_games(games_dict.values())


if __name__ == "__main__":
    main()
