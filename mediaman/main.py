import logging

import typer

from mediaman.services import ImdbWatchlist, TraktService

logging.basicConfig(
    format="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)
app = typer.Typer()

app = typer.Typer()


class Scope:
    trakt: TraktService
    imdb: ImdbWatchlist


scope = Scope()


@app.command()
def update_watchlist():
    scope.imdb = ImdbWatchlist()
    scope.trakt.update_watchlist(scope.imdb.watchlist)


@app.command()
def cleanup_watchlist():
    scope.trakt.cleanup_watchlist()


@app.command()
def update_collect():
    scope.trakt.update_collect()


@app.command()
def list_collect():
    scope.trakt.list_collect()


@app.command()
def all():
    scope.imdb = ImdbWatchlist()
    scope.trakt.update_watchlist(scope.imdb.watchlist)
    scope.trakt.cleanup_watchlist()
    scope.trakt.update_collect()
    scope.trakt.list_collect()


@app.callback()
def setup():
    scope.trakt = TraktService()
    return


if __name__ == "__main__":
    app()
