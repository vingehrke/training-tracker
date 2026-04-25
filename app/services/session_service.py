from sqlalchemy.orm import Session as DBSession
from datetime import datetime
from ..db.models import WorkoutSession, ExerciseSet, WeightType


def start_session(db: DBSession, plan_id: int) -> WorkoutSession:
    session = WorkoutSession(plan_id=plan_id, started_at=datetime.now())
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def finish_session(db: DBSession, session_id: int, notes: str | None = None) -> WorkoutSession | None:
    session = db.get(WorkoutSession, session_id)
    if not session:
        return None
    session.finished_at = datetime.now()
    session.notes = notes
    db.commit()
    db.refresh(session)
    return session


def log_set(
    db: DBSession,
    session_id: int,
    exercise_id: int,
    set_number: int,
    reps: int,
    weight_kg: float | None = None,
    weight_level: int | None = None,
) -> ExerciseSet:
    exercise_set = ExerciseSet(
        session_id=session_id,
        exercise_id=exercise_id,
        set_number=set_number,
        reps=reps,
        weight_kg=weight_kg,
        weight_level=weight_level,
    )
    db.add(exercise_set)
    db.commit()
    db.refresh(exercise_set)
    return exercise_set


def get_sets_for_session(db: DBSession, session_id: int, exercise_id: int) -> list[ExerciseSet]:
    return (
        db.query(ExerciseSet)
        .filter_by(session_id=session_id, exercise_id=exercise_id)
        .order_by(ExerciseSet.set_number)
        .all()
    )


def get_recent_sessions(db: DBSession, limit: int = 10) -> list[WorkoutSession]:
    return (
        db.query(WorkoutSession)
        .order_by(WorkoutSession.started_at.desc())
        .limit(limit)
        .all()
    )


def get_last_sets(db: DBSession, exercise_id: int) -> list[ExerciseSet]:
    """Letzte Sätze einer Übung über alle Sessions — nützlich als Referenz."""
    last_session = (
        db.query(WorkoutSession)
        .join(ExerciseSet)
        .filter(ExerciseSet.exercise_id == exercise_id)
        .order_by(WorkoutSession.started_at.desc())
        .first()
    )
    if not last_session:
        return []
    return get_sets_for_session(db, last_session.id, exercise_id)
