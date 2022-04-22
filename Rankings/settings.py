from pydantic import BaseSettings

__all__ = ['Settings']


class Settings(BaseSettings):
    sport: str = "Pool"
    show_wins: bool = True
    show_losses: bool = True
    show_draws: bool = False
    show_percent: bool = True
    show_rating: bool = True
    show_true_skill_sigma: bool = False
    show_true_skill_mu: bool = False
    show_normalised_rating: bool = True
    support_draws: bool = False
    max_players_per_game: int = 2
    max_teams: int = 10
    support_individual: bool = True

    league_title: str = "BAR Technologies Billiards Society"

    initial_k: float = 30
    standard_k: float = 16
    use_true_skill: bool = False
    sort_by: str = "nrating"

    host: str = "0.0.0.0"
    port: int = 8080
