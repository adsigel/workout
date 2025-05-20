from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import SessionLocal, engine
from .models import MovementType, MuscleGroupType
from .workout_generator import WorkoutGenerator
from app.seed_exercises import seed_exercises

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workout Planner API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://workout-client.onrender.com",  # TODO: Replace with your actual frontend Render URL
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_exercise_movement_types(db: Session, exercise_id: int) -> List[MovementType]:
    stmt = models.exercise_movement_types.select().where(models.exercise_movement_types.c.exercise_id == exercise_id)
    result = db.execute(stmt)
    return [MovementType(mt[1]) for mt in result]

@app.post("/exercises/", response_model=schemas.Exercise)
def create_exercise(exercise: schemas.ExerciseCreate, db: Session = Depends(get_db)):
    # Create the exercise
    db_exercise = models.Exercise(
        name=exercise.name,
        description=exercise.description,
        estimated_duration=exercise.estimated_duration
    )
    db.add(db_exercise)
    db.flush()  # Flush to get the ID

    # Handle equipment
    for equip_name in exercise.equipment:
        equip = db.query(models.Equipment).filter(models.Equipment.name == equip_name).first()
        if not equip:
            equip = models.Equipment(name=equip_name)
            db.add(equip)
            db.flush()
        db_exercise.equipment.append(equip)

    # Handle muscle groups
    for muscle_group in exercise.muscle_groups:
        mg = db.query(models.MuscleGroup).filter(models.MuscleGroup.name == muscle_group).first()
        if not mg:
            mg = models.MuscleGroup(name=muscle_group)
            db.add(mg)
            db.flush()
        db_exercise.muscle_groups.append(mg)

    # Handle movement types
    for movement_type in exercise.movement_types:
        # Add the movement type to the association table
        stmt = models.exercise_movement_types.insert().values(
            exercise_id=db_exercise.id,
            movement_type=movement_type.value
        )
        db.execute(stmt)

    db.commit()
    db.refresh(db_exercise)
    
    # Get movement types for response
    movement_types = get_exercise_movement_types(db, db_exercise.id)
    
    # Create response object
    response = schemas.Exercise(
        id=db_exercise.id,
        name=db_exercise.name,
        description=db_exercise.description,
        movement_types=movement_types,
        estimated_duration=db_exercise.estimated_duration,
        equipment=db_exercise.equipment,
        muscle_groups=db_exercise.muscle_groups
    )
    return response

@app.post("/exercises/bulk", response_model=List[schemas.Exercise])
def create_exercises(exercises: List[schemas.ExerciseCreate], db: Session = Depends(get_db)):
    created_exercises = []
    for exercise in exercises:
        created_exercises.append(create_exercise(exercise, db))
    return created_exercises

@app.get("/exercises/", response_model=List[schemas.Exercise])
def read_exercises(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    exercises = db.query(models.Exercise).offset(skip).limit(limit).all()
    response_exercises = []
    for exercise in exercises:
        movement_types = get_exercise_movement_types(db, exercise.id)
        response_exercises.append(schemas.Exercise(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            movement_types=movement_types,
            estimated_duration=exercise.estimated_duration,
            equipment=exercise.equipment,
            muscle_groups=exercise.muscle_groups
        ))
    return response_exercises

@app.get("/exercises/{exercise_id}", response_model=schemas.Exercise)
def read_exercise(exercise_id: int, db: Session = Depends(get_db)):
    exercise = db.query(models.Exercise).filter(models.Exercise.id == exercise_id).first()
    if exercise is None:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    movement_types = get_exercise_movement_types(db, exercise.id)
    return schemas.Exercise(
        id=exercise.id,
        name=exercise.name,
        description=exercise.description,
        movement_types=movement_types,
        estimated_duration=exercise.estimated_duration,
        equipment=exercise.equipment,
        muscle_groups=exercise.muscle_groups
    )

@app.get("/workouts/generate", response_model=schemas.Workout)
def generate_workout(duration_minutes: int, db: Session = Depends(get_db)):
    """Generate a workout with the specified duration in minutes."""
    try:
        generator = WorkoutGenerator(db)
        workout = generator.generate_workout(duration_minutes)
        
        # Convert exercises to response format
        exercises = []
        for exercise in workout["exercises"]:
            movement_types = get_exercise_movement_types(db, exercise.id)
            exercises.append(schemas.Exercise(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                movement_types=movement_types,
                estimated_duration=exercise.estimated_duration,
                equipment=exercise.equipment,
                muscle_groups=exercise.muscle_groups
            ))
        
        return schemas.Workout(
            exercises=exercises,
            rounds=workout["rounds"],
            estimated_duration_minutes=workout["estimated_duration_minutes"]
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    seed_exercises(db)
    return {"status": "seeded"} 