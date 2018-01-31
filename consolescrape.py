import logging
import requests
from collections import namedtuple
from lxml import html

GameItem = namedtuple("GameItem", ["title", "price", "in_stock"])


def load_url(url, iscached):
    cache_file_name = "cached.html"
    try:
        if not iscached:
            raise ValueError("no cache")
        with open(cache_file_name, "rt", encoding="utf-8") as file:
            content = file.read()
            logging.info("Loded page from cache.")
    except ValueError:
        page = requests.get(url)
        content = page.content
        logging.info("Loded page from the internet.")
        with open(cache_file_name, "wt", encoding="utf-8") as file:
            file.write(str(content))
    return content


def trim_elem(elements):
    return str(elements[0]).strip()


def scrape_page(content):
    games = []
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
        games.append(GameItem(title, price, in_stock))
    return games


def get_games():
    games = []
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
        games.extend(games_page)
    return games


def print_available_games(games):
    available_games = list(filter(lambda x: x.price and x.in_stock, games))
    max_title_length = max([len(x.title) for x in available_games])
    max_price_length = max([len(str(x.price)) for x in available_games])
    for game in sorted(available_games, key=lambda x: x.title):
        padded_title = game.title.ljust(max_title_length)
        padded_price = str(game.price).rjust(max_price_length)
        print("{t} {p} Ft".format(t=padded_title, p=padded_price))
    print("\nGames: {}, available: {}.".format(len(games), len(available_games)))


def main():
    games = get_games()
    print_available_games(games)


if __name__ == "__main__":
    main()
