import logging
import typer
from mediaman.services import TraktService, ImdbWatchlist

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)
app = typer.Typer()

@app.command()
def all():
    trakt = TraktService()
    imdb = ImdbWatchlist()

    trakt.update_watchlist(imdb.watchlist)
    trakt.cleanup_watchlist()
    trakt.update_collect()
    trakt.list_collect()

def main():
    app()
    return

if __name__ == "__main__":
    main()
