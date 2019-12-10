import logging
from mediaman.services import TraktService, ImdbWatchlist

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def main():
    trakt = TraktService()
    imdb = ImdbWatchlist()

    trakt.update_watchlist(imdb.watchlist)
    trakt.cleanup_watchlist()
    trakt.update_collect()
    trakt.list_collect()

    return


if __name__ == "__main__":
    main()
