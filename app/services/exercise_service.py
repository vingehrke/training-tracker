from sqlalchemy.orm import Session
from ..db.models import Exercise, WeightType


def get_all(session: Session) -> list[Exercise]:
    return session.query(Exercise).order_by(Exercise.name).all()


def get_by_id(session: Session, exercise_id: int) -> Exercise | None:
    return session.get(Exercise, exercise_id)


def create(session: Session, name: str, weight_type: WeightType, muscle_group: str | None = None) -> Exercise:
    exercise = Exercise(name=name, weight_type=weight_type, muscle_group=muscle_group)
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


def update(session: Session, exercise_id: int, name: str, weight_type: WeightType, muscle_group: str | None = None) -> Exercise | None:
    exercise = get_by_id(session, exercise_id)
    if not exercise:
        return None
    exercise.name = name
    exercise.weight_type = weight_type
    exercise.muscle_group = muscle_group
    session.commit()
    session.refresh(exercise)
    return exercise


def delete(session: Session, exercise_id: int) -> bool:
    exercise = get_by_id(session, exercise_id)
    if not exercise:
        return False
    session.delete(exercise)
    session.commit()
    return True
