
import logging
import requests
import csv


class ImdbWatchlist:
    """
    IMDB Watchlist
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".imdb_service")
        self.url = "https://www.imdb.com/list/ls003585836/export"
        self.update()

    def update(self):
        """
        Update watchlist
        """
        self.logger.info(f"Getting IMDB watchlist")
        # Get IMDB watchlist via csv export
        watchlist_url = "https://www.imdb.com/list/ls003585836/export"
        r = requests.get(self.url)
        reader = csv.reader(r.text.split("\n"), delimiter=",")
        self.watchlist = []
        movie_count = -1
        for row in reader:
            if len(row) == 0 or row[7] != "movie":
                continue

            movie_count += 1
            if movie_count == 0:
                self.logger.debug(f"CSV Columns:")
                for index, c in enumerate(row):
                    self.logger.debug(f"\t{index}: {c}")
                continue

            self.logger.debug(f"\t{row[1]} {row[5]}")
            self.watchlist.append(row[1])

        self.logger.debug(f"IMDB Watchlist: {movie_count} movies found.")
        return self.watchlist
