from app.core.models import Player


def create_player(*, telegram_id, full_name, grade, role) -> Player:
    formatted_full_name = full_name.strip()
    formatted_grade = grade.strip().upper()

    return Player(
        telegram_id=telegram_id,
        full_name=formatted_full_name,
        grade=formatted_grade,
        role=role,
    )
