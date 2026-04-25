from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime
import enum


class Base(DeclarativeBase):
    pass


class WeightType(str, enum.Enum):
    KG = "kg"
    LEVEL = "level"


class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    weight_type = Column(Enum(WeightType), nullable=False, default=WeightType.KG)
    muscle_group = Column(String, nullable=True)

    plan_exercises = relationship("PlanExercise", back_populates="exercise", cascade="all, delete-orphan")
    exercise_sets = relationship("ExerciseSet", back_populates="exercise", cascade="all, delete-orphan")


class TrainingPlan(Base):
    __tablename__ = "training_plans"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

    plan_exercises = relationship("PlanExercise", back_populates="plan", cascade="all, delete-orphan", order_by="PlanExercise.position")
    sessions = relationship("WorkoutSession", back_populates="plan", cascade="all, delete-orphan")


class PlanExercise(Base):
    __tablename__ = "plan_exercises"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    position = Column(Integer, nullable=False, default=0)

    plan = relationship("TrainingPlan", back_populates="plan_exercises")
    exercise = relationship("Exercise", back_populates="plan_exercises")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True)
    plan_id = Column(Integer, ForeignKey("training_plans.id"), nullable=False)
    started_at = Column(DateTime, nullable=False, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
    notes = Column(String, nullable=True)

    plan = relationship("TrainingPlan", back_populates="sessions")
    exercise_sets = relationship("ExerciseSet", back_populates="session", cascade="all, delete-orphan")


class ExerciseSet(Base):
    __tablename__ = "exercise_sets"

    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    set_number = Column(Integer, nullable=False)
    reps = Column(Integer, nullable=False)
    weight_kg = Column(Float, nullable=True)
    weight_level = Column(Integer, nullable=True)

    session = relationship("WorkoutSession", back_populates="exercise_sets")
    exercise = relationship("Exercise", back_populates="exercise_sets")
