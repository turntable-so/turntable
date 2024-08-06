import os

from vinyl.lib.asset import resource
from vinyl.lib.connect import DatabaseFileConnector


is_dev = os.getenv("DEV", False)
print("is_dev", is_dev)

path_prefix = "data/" if is_dev else "/var/data/"


@resource
def debit_card_specializing():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/debit_card_specializing/debit_card_specializing.sqlite"
    )


@resource
def financial():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/financial/financial.sqlite"
    )


@resource
def formula_1():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/formula_1/formula_1.sqlite"
    )


@resource
def california_schools():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/california_schools/california_schools.sqlite"
    )


@resource
def card_games():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/card_games/card_games.sqlite"
    )


@resource
def card_games():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/card_games/card_games_2.sqlite"
    )


@resource
def european_football_2():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/european_football_2/european_football_2.sqlite"
    )


@resource
def thrombosis_prediction():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/thrombosis_prediction/thrombosis_prediction.sqlite"
    )


@resource
def toxicology():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/toxicology/toxicology.sqlite"
    )


@resource
def student_club():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/student_club/student_club.sqlite"
    )


@resource
def superhero():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/superhero/superhero.sqlite"
    )


@resource
def codebase_community():
    return DatabaseFileConnector(
        f"{path_prefix}dev_databases/codebase_community/codebase_community.sqlite"
    )
