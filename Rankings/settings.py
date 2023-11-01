from pydantic import BaseSettings

__all__ = ["Settings"]


class Settings(BaseSettings):
    sport: str = "Pool"
    show_wins: bool = True
    show_losses: bool = True
    show_draws: bool = False
    show_percent: bool = True
    show_rating: bool = True
    support_draws: bool = False
    max_players_per_game: int = 2

    league_title: str = "BAR Technologies Billiards Society"

    initial_k: float = 30
    standard_k: float = 16
    sort_by: str = "nrating"

    host: str = "0.0.0.0"
    port: int = 8080

    backend_cors_origins: list[str] = ["*"]

    mongo_host: str = "localhost"
    mongo_port: int = 27017
