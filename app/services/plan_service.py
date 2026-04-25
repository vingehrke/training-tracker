from sqlalchemy.orm import Session
from ..db.models import TrainingPlan, PlanExercise


def get_all(session: Session) -> list[TrainingPlan]:
    return session.query(TrainingPlan).order_by(TrainingPlan.name).all()


def get_by_id(session: Session, plan_id: int) -> TrainingPlan | None:
    return session.get(TrainingPlan, plan_id)


def create(session: Session, name: str, description: str | None = None) -> TrainingPlan:
    plan = TrainingPlan(name=name, description=description)
    session.add(plan)
    session.commit()
    session.refresh(plan)
    return plan


def update(session: Session, plan_id: int, name: str, description: str | None = None) -> TrainingPlan | None:
    plan = get_by_id(session, plan_id)
    if not plan:
        return None
    plan.name = name
    plan.description = description
    session.commit()
    session.refresh(plan)
    return plan


def delete(session: Session, plan_id: int) -> bool:
    plan = get_by_id(session, plan_id)
    if not plan:
        return False
    session.delete(plan)
    session.commit()
    return True


def add_exercise(session: Session, plan_id: int, exercise_id: int) -> PlanExercise:
    existing = session.query(PlanExercise).filter_by(plan_id=plan_id).count()
    pe = PlanExercise(plan_id=plan_id, exercise_id=exercise_id, position=existing)
    session.add(pe)
    session.commit()
    session.refresh(pe)
    return pe


def remove_exercise(session: Session, plan_exercise_id: int) -> bool:
    pe = session.get(PlanExercise, plan_exercise_id)
    if not pe:
        return False
    session.delete(pe)
    session.commit()
    return True
