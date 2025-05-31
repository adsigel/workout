from fastapi import FastAPI, Depends, HTTPException, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
from . import models, schemas
from .database import SessionLocal, engine
from .models import MovementType, MuscleGroupType
from .workout_generator import WorkoutGenerator
from app.seed_exercises import seed_exercises
import logging

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
        estimated_duration=exercise.estimated_duration,
        intensity=getattr(exercise, 'intensity', 'medium')
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
        intensity = getattr(exercise, "intensity", None) or "medium"
        response_exercises.append(schemas.Exercise(
            id=exercise.id,
            name=exercise.name,
            description=exercise.description,
            movement_types=movement_types,
            estimated_duration=exercise.estimated_duration,
            equipment=exercise.equipment,
            muscle_groups=exercise.muscle_groups,
            intensity=intensity
        ))
    return response_exercises

@app.get("/exercises/names", response_model=List[str])
def read_exercise_names(db: Session = Depends(get_db)):
    """Get just the names of all exercises."""
    exercises = db.query(models.Exercise).all()
    return [exercise.name for exercise in exercises]

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
def generate_workout(
    duration_minutes: int,
    muscle_groups: list[str] = Query(None),
    equipment: list[str] = Query(None),
    intensity_level: int = Query(3),
    db: Session = Depends(get_db)
):
    """Generate a workout with the specified duration in minutes, allowed muscle groups, allowed equipment, and intensity level (1-5)."""
    try:
        generator = WorkoutGenerator(db)
        workout = generator.generate_workout(
            duration_minutes, 
            allowed_muscle_groups=muscle_groups,
            allowed_equipment=equipment,
            intensity_level=intensity_level
        )
        
        # Convert exercises to response format
        exercises = []
        for exercise in workout["exercises"]:
            movement_types = get_exercise_movement_types(db, exercise.id)
            exercise_response = schemas.Exercise(
                id=exercise.id,
                name=exercise.name,
                description=exercise.description,
                movement_types=movement_types,
                estimated_duration=exercise.estimated_duration,
                equipment=exercise.equipment,
                muscle_groups=exercise.muscle_groups,
                intensity=exercise.intensity
            )
            exercises.append(exercise_response)
        
        workout_response = schemas.Workout(
            exercises=exercises,
            rounds=workout["rounds"],
            estimated_duration_minutes=workout["estimated_duration_minutes"]
        )
        
        return workout_response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error in generate_workout endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/seed")
def seed(db: Session = Depends(get_db)):
    try:
        result = seed_exercises(db)
        return {
            "status": "seeded",
            "summary": {
                "added": result.get("added", []),
                "skipped": result.get("skipped", []),
                "total_added": result.get("total_added", 0),
                "total_skipped": result.get("total_skipped", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/exercises/cleanup", response_model=List[str])
def cleanup_duplicates(db: Session = Depends(get_db)):
    """Remove duplicate exercises, keeping only the first occurrence of each name."""
    # Get all exercises
    all_exercises = db.query(models.Exercise).all()
    
    # Track seen names and exercises to delete
    seen_names = set()
    to_delete = []
    
    for exercise in all_exercises:
        if exercise.name in seen_names:
            to_delete.append(exercise)
        else:
            seen_names.add(exercise.name)
    
    # Delete duplicates
    deleted_names = []
    for exercise in to_delete:
        deleted_names.append(exercise.name)
        db.delete(exercise)
    
    db.commit()
    return deleted_names

@app.post("/workouts/swap_exercise", response_model=schemas.Exercise)
def swap_exercise(
    current_workout_ids: list[int] = Body(...),
    swap_out_id: int = Body(...),
    muscle_groups: list[str] = Query(None),
    equipment: list[str] = Query(None),
    intensity_level: int = Query(3),
    db: Session = Depends(get_db)
):
    """Swap out an exercise in a workout for a new best-fit exercise."""
    try:
        generator = WorkoutGenerator(db)
        new_ex = generator.swap_exercise(
            current_workout_ids=current_workout_ids,
            swap_out_id=swap_out_id,
            allowed_muscle_groups=muscle_groups,
            allowed_equipment=equipment,
            intensity_level=intensity_level
        )
        movement_types = get_exercise_movement_types(db, new_ex.id)
        return schemas.Exercise(
            id=new_ex.id,
            name=new_ex.name,
            description=new_ex.description,
            movement_types=movement_types,
            estimated_duration=new_ex.estimated_duration,
            equipment=new_ex.equipment,
            muscle_groups=new_ex.muscle_groups,
            intensity=new_ex.intensity
        )
    except Exception as e:
        logger.error(f"Error in swap_exercise endpoint: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e)) 