import os

from tools.spiders.alpha_query_spider import AlphaQuerySpider
from tools.util.globals               import G


def run() -> None:
    G.log.directory_create()
    G.log.file_create()

    AlphaQuerySpider().scrape_data()
    return


if __name__ == '__main__':
    os.system("cls")
    run()
