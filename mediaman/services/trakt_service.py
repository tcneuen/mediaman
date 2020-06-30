import sys
import logging
import configparser

import trakt
from trakt.movies import Movie
from trakt.users import User


class TraktService:
    def __init__(self):
        self.logger = logging.getLogger(__name__ + ".trakt_service")

        config = configparser.ConfigParser()
        config.read("config.ini")
        trakt.core.AUTH_METHOD = trakt.core.OAUTH_AUTH
        trakt.core.CLIENT_ID = config["trakt"]["CLIENT_ID"]
        trakt.core.CLIENT_SECRET = config["trakt"]["CLIENT_SECRET"]
        self.__username__ = "tcneuen"
        trakt.core.init(
            self.__username__,
            client_id=config["trakt"]["CLIENT_ID"],
            client_secret=config["trakt"]["CLIENT_SECRET"],
            store=True,
        )

    def update_watchlist(self, movie_list: list) -> bool:
        """
        Update watchlist based on IMDB movie list
        """
        if not movie_list:
            return False
        self.logger.info("Update watchlist")

        # Get trakt watchlist
        trakt_list = [m.imdb for m in User(self.__username__).watchlist_movies]
        watched = [m.imdb for m in User(self.__username__).watched_movies]
        self.logger.debug(f"Trakt Watchlist: {len(trakt_list)} movies found.")

        # Compare movies and add missing to trakt
        diff_movies = set(movie_list).difference(trakt_list)
        self.logger.debug(f"{len(diff_movies)} differences found.")

        # Unwatched movies on imdb watchlist and missing on trakt
        add_movies = set(diff_movies).difference(watched)
        movies_added = []
        for m in add_movies:
            try:
                movie = Movie(m)
                self.logger.debug(f"added {movie.imdb} {movie.title}")
                movie.add_to_watchlist()
                movies_added.append(f" + {movie.title} ({movie.year})")
            except:
                self.logger.warning(f"{m} NOT FOUND")

        msg = "Update watchlist COMPLETE:\n"
        if len(add_movies) == 0:
            msg += "No changes found."
        else:
            msg += f"{len(movies_added)} movies added\n"
            msg += "\n".join(movies_added)

        # Movies that do have been watched and are on IMDB
        movies_watched = []
        imdb_watched = set(movie_list).intersection(watched)
        self.logger.debug(f"{len(imdb_watched)} movies watched on IMDB list")
        for m in imdb_watched:
            try:
                movie = Movie(m)
                self.logger.debug(f"watched {movie.imdb} {movie.title}")
                movies_watched.append(f" - {movie.title} ({movie.year})")
            except:
                self.logger.warning(f"{m} NOT FOUND")

        if len(movies_watched) != 0:
            msg += f"\n\n{len(movies_watched)} movies watched on IMDB list\n"
            msg += "\n".join(movies_watched)

        self.logger.info(msg)

        return True

    def cleanup_watchlist(self):
        """
        Remove watched movies from watchlist
        """
        self.logger.info("Cleanup watchlist")
        watchlist = [m.imdb for m in User(self.__username__).watchlist_movies]
        watched = [m.imdb for m in User(self.__username__).watched_movies]
        watched_movies = set(watchlist).intersection(watched)

        movies_removed = []
        for m in watched_movies:
            try:
                movie = Movie(m)
                self.logger.debug(f"removed {movie.imdb} {movie.title}")
                movie.remove_from_watchlist()
                movies_removed.append(f" - {movie.title} ({movie.year})")
            except:
                self.logger.warning(f"{m} NOT FOUND")

        msg = "Cleanup watchlist COMPLETE:\n"
        if len(watched_movies) == 0:
            msg += "No changes found."
        else:
            msg += f"{len(movies_removed)} movies removed\n"
            msg += "\n".join(movies_removed)

        self.logger.info(msg)

    def update_collect(self):
        self.logger.info("Update collect")
        watchlist = [m.imdb for m in User(self.__username__).watchlist_movies]
        collected = [m.imdb for m in User(self.__username__).movie_collection]
        watched = [m.imdb for m in User(self.__username__).watched_movies]
        collect = list(set(watched + watchlist))

        collect_list = User(self.__username__).get_list("Collect")

        list_movies = []
        for i in collect_list.get_items():
            if i.media_type == "movies":
                if i.released == False:
                    collect_list.remove_items(i)
                    self.logger.debug(f"unmarked {i.title} ({i.year})")
                else:
                    list_movies.append(i.imdb)

        self.logger.debug(f"Checking {len(collect)} for possible collection")
        self.logger.debug(f"{len(list_movies)} currently marked")
        collect_movies = set(collect).difference(collected).difference(list_movies)

        self.logger.debug(f"Checking {len(collect_movies)} for possible collection")

        movies_marked = []
        for m in collect_movies:
            try:
                movie = Movie(m)
                if movie.released == False:
                    continue
                # if movie.ratings["rating"] < 6:
                #     continue
                self.logger.debug(f"marked {movie.imdb} {movie.title}")
                collect_list.add_items(movie)
                movies_marked.append(f" + {movie.title} ({movie.year})")
            except:
                self.logger.error(sys.exc_info()[0])

        msg = "Update collect COMPLETE:\n"
        msg += f"{len(movies_marked)} movies marked for collection\n"
        if len(movies_marked) != 0:
            msg += "\n".join(movies_marked)

        movies_unmarked = []
        collected_movies = set(collected).intersection(list_movies)
        for m in collected_movies:
            try:
                movie = Movie(m)
                self.logger.debug(
                    f'unmarked {movie.imdb} {movie.title} {movie.ratings["rating"]}'
                )
                collect_list.remove_items(movie)
                movies_unmarked.append(f" - {movie.title} ({movie.year})")
            except:
                self.logger.error(sys.exc_info()[0])

        msg += f"\n\n{len(movies_unmarked)} movies unmarked\n"
        if len(movies_unmarked) != 0:
            msg += "\n".join(movies_unmarked)

        self.logger.info(msg)

    def list_collect(self):
        import datetime

        collect_list = User(self.__username__).get_list("Collect")

        now = datetime.datetime.now()

        list_movies = "Collect PTP Links:\n"
        movie_list = set()
        for i in collect_list.get_items():
            if i.media_type != "movies":
                continue
            if i.released is None:
                continue
            rel_year = int(i.released[0:4])
            if rel_year > now.year:
                continue
            else:
                ptp_query = f"https://passthepopcorn.me/torrents.php?order_by=relevance&searchstr={i.imdb}"
                movie_msg = f"{i.title} ({i.year}) {ptp_query}\n"
                movie_list.add(movie_msg)
        for m in movie_list:
            list_movies += m
        self.logger.info(list_movies)
