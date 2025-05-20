# from app.main import app
from app.models import MovementType, MuscleGroupType
from app.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends
from app import models

def list_valid_muscle_groups():
    """Print all valid muscle groups for reference."""
    print("\nValid muscle groups:")
    for mg in MuscleGroupType:
        print(f"- {mg.value}")
    print()

def validate_muscle_groups(exercises_data):
    """Validate that all muscle group references exist in the MuscleGroupType enum."""
    valid_muscle_groups = set(mg.value for mg in MuscleGroupType)
    errors = []
    
    for i, exercise in enumerate(exercises_data):
        for muscle_group in exercise["muscle_groups"]:
            if muscle_group.value not in valid_muscle_groups:
                errors.append(f"Exercise '{exercise['name']}' references invalid muscle group: {muscle_group.value}")
    
    if errors:
        raise ValueError("Invalid muscle group references found:\n" + "\n".join(errors))

def seed_exercises(db: Session):
    exercises = [
        {
            "name": "Two-handed Kettlebell Swing",
            "description": "A dynamic hip hinge movement that builds explosive power and posterior chain strength",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 45,  # seconds per set
            "equipment": ["kettlebell"],
            "muscle_groups": [
                MuscleGroupType.HAMSTRINGS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.LOWER_BACK,
                MuscleGroupType.ABS
            ]
        },
        {
            "name": "Pushup",
            "description": "A fundamental bodyweight exercise that builds upper body pushing strength",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 30,
            "equipment": [],
            "muscle_groups": [
                MuscleGroupType.CHEST,
                MuscleGroupType.FRONT_DELTOIDS,
                MuscleGroupType.TRICEPS,
                MuscleGroupType.ABS
            ]
        },
        {
            "name": "Single Leg Romanian Deadlift",
            "description": "A unilateral hip hinge movement that improves balance and posterior chain strength",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 40,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [
                MuscleGroupType.HAMSTRINGS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.LOWER_BACK,
                MuscleGroupType.ABS
            ]
        },
        {
            "name": "Landmine Twist",
            "description": "A rotational core exercise that builds anti-rotation strength",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 35,
            "equipment": ["dumbbell"],
            "muscle_groups": [
                MuscleGroupType.OBLIQUES,
                MuscleGroupType.ABS,
                MuscleGroupType.SIDE_DELTOIDS
            ]
        },
        {
            "name": "Suitcase Deadlift",
            "description": "A unilateral deadlift variation that builds core stability and hip strength",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [
                MuscleGroupType.HAMSTRINGS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.LOWER_BACK,
                MuscleGroupType.ABS,
                MuscleGroupType.FOREARMS
            ]
        },
        {
            "name": "Suitcase Lunge",
            "description": "A unilateral lower body exercise that builds leg strength and core stability",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [
                MuscleGroupType.QUADS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.ABS,
                MuscleGroupType.FOREARMS
            ]
        },
        {
            "name": "Goblet Squat",
            "description": "A front-loaded squat variation that builds leg strength and core stability",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [
                MuscleGroupType.QUADS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.ABS,
                MuscleGroupType.FOREARMS
            ]
        },
        {
            "name": "Goblet Lunge",
            "description": "A unilateral squat variation with front loading for added core challenge",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [
                MuscleGroupType.QUADS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.ABS,
                MuscleGroupType.FOREARMS
            ]
        },
        {
            "name": "Gunslinger",
            "description": "A dynamic kettlebell exercise combining a clean and press with a squat",
            "movement_types": [MovementType.PUSH, MovementType.SQUAT],
            "estimated_duration": 50,
            "equipment": ["kettlebell"],
            "muscle_groups": [
                MuscleGroupType.QUADS,
                MuscleGroupType.GLUTES,
                MuscleGroupType.FRONT_DELTOIDS,
                MuscleGroupType.TRICEPS,
                MuscleGroupType.ABS
            ]
        },
        {
            "name": "Renegade Rows",
            "description": "A compound exercise combining a pushup with a row",
            "movement_types": [MovementType.PUSH, MovementType.PULL],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [
                MuscleGroupType.CHEST,
                MuscleGroupType.FRONT_DELTOIDS,
                MuscleGroupType.TRICEPS,
                MuscleGroupType.LATS,
                MuscleGroupType.BICEPS,
                MuscleGroupType.ABS
            ]
        },
        {
            "name": "Kettlebell Side Bend",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell in one hand. Bend sideways at the waist, keeping the back straight. Return to starting position. Complete all reps on one side before switching.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,  # seconds
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES]
        },
        {
            "name": "Standing Dumbbell Wood Chops",
            "description": "Stand with feet shoulder-width apart, holding a dumbbell with both hands. Start with the weight at one hip, then swing it diagonally across the body to the opposite shoulder, rotating the torso. Return to starting position.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Standing Overhead Press",
            "description": "Stand with feet shoulder-width apart, holding weights at shoulder height. Press the weights overhead until arms are fully extended, then lower back to starting position.",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 45,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS]
        },
        {
            "name": "Mountain Climbers",
            "description": "Start in a plank position. Alternately bring knees toward chest in a running motion, keeping hips low and core engaged.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 45,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Bent-Over Kettlebell Row (Two Hand)",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell with both hands. Hinge at hips, keeping back straight. Pull the kettlebell to the chest, then lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.BICEPS]
        },
        {
            "name": "Bent-Over Kettlebell Row (One Hand)",
            "description": "Stand with feet staggered, holding a kettlebell in one hand. Hinge at hips, keeping back straight. Pull the kettlebell to the chest, then lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.BICEPS]
        },
        {
            "name": "Kettlebell High Pull",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell between legs. Explosively pull the kettlebell up to chest height, keeping elbows high. Lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Plank Pull-Through",
            "description": "Start in a plank position with a weight beside you. Reach under with one hand to grab the weight, pull it across to the other side, then repeat in the opposite direction.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 45,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Side Plank Underarm Twist",
            "description": "Start in a side plank position. Rotate the top arm under the body, then back to starting position. Complete all reps on one side before switching.",
            "movement_types": [MovementType.CORE, MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Kneeling Dumbbell Straight Arm Chop",
            "description": "Kneel on one knee, holding a dumbbell with both hands. Start with arms extended overhead, then chop diagonally across the body, rotating the torso.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Racked Kettlebell Squat",
            "description": "Hold kettlebells in the rack position (at shoulder height). Perform a squat, keeping chest up and core engaged. Return to standing position.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS, MuscleGroupType.LOWER_BACK]
        },
        {
            "name": "Deadbugs",
            "description": "A core stability exercise performed lying on your back, optionally holding a dumbbell or kettlebell in each hand.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 40,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES]
        },
        {
            "name": "Curtsy Goblet Lunge",
            "description": "A lunge variation where you step one leg behind and across the other, holding a kettlebell at your chest.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS]
        },
        {
            "name": "Kickstand Single Arm Deadlift",
            "description": "A unilateral hinge movement with a kettlebell, using a kickstand stance for balance.",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.HAMSTRINGS, MuscleGroupType.GLUTES, MuscleGroupType.LOWER_BACK, MuscleGroupType.FOREARMS]
        },
        {
            "name": "Pull-ups",
            "description": "A vertical pulling exercise performed on stall bars.",
            "movement_types": [MovementType.PULL],
            "estimated_duration": 30,
            "equipment": ["stall bars"],
            "muscle_groups": [MuscleGroupType.LATS, MuscleGroupType.BICEPS, MuscleGroupType.UPPER_BACK]
        },
        {
            "name": "Tricep Dips",
            "description": "A bodyweight pushing exercise performed on stall bars to target the triceps.",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 30,
            "equipment": ["stall bars"],
            "muscle_groups": [MuscleGroupType.TRICEPS, MuscleGroupType.CHEST, MuscleGroupType.FRONT_DELTOIDS]
        },
        {
            "name": "Bicep Curls",
            "description": "A classic arm exercise performed with dumbbells or kettlebells.",
            "movement_types": [MovementType.PULL],
            "estimated_duration": 30,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.BICEPS, MuscleGroupType.FOREARMS]
        },
        {
            "name": "Hip Bridges",
            "description": "A glute and hamstring exercise performed on the floor, optionally with a dumbbell for added resistance.",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 35,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.GLUTES, MuscleGroupType.HAMSTRINGS, MuscleGroupType.LOWER_BACK]
        },
        {
            "name": "Reverse Goblet Lunge",
            "description": "A lunge variation stepping backward, holding a kettlebell at your chest.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS]
        },
        {
            "name": "Overhead March",
            "description": "March in place while holding a kettlebell or dumbbell overhead, engaging the core and shoulders.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 35,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.OBLIQUES]
        },
        {
            "name": "Squat Thruster with a Twist",
            "description": "A full-body movement: squat holding a dumbbell, then press overhead and rotate the torso at the top.",
            "movement_types": [MovementType.SQUAT, MovementType.PUSH, MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS]
        }
    ]
    
    # Validate muscle groups before proceeding
    validate_muscle_groups(exercises)
    
    for exercise_data in exercises:
        # Create exercise
        db_exercise = models.Exercise(
            name=exercise_data["name"],
            description=exercise_data["description"],
            estimated_duration=exercise_data["estimated_duration"]
        )
        db.add(db_exercise)
        db.flush()  # Flush to get the ID

        # Add equipment
        for equip_name in exercise_data["equipment"]:
            equip = db.query(models.Equipment).filter(models.Equipment.name == equip_name).first()
            if not equip:
                equip = models.Equipment(name=equip_name)
                db.add(equip)
                db.flush()
            db_exercise.equipment.append(equip)

        # Add movement types
        for movement_type in exercise_data["movement_types"]:
            stmt = models.exercise_movement_types.insert().values(
                exercise_id=db_exercise.id,
                movement_type=movement_type.value
            )
            db.execute(stmt)

        # Add muscle groups
        for muscle_group in exercise_data["muscle_groups"]:
            mg = db.query(models.MuscleGroup).filter(models.MuscleGroup.name == muscle_group).first()
            if not mg:
                mg = models.MuscleGroup(name=muscle_group)
                db.add(mg)
                db.flush()
            db_exercise.muscle_groups.append(mg)

    db.commit()

if __name__ == "__main__":
    # List valid muscle groups before seeding
    list_valid_muscle_groups()
    
    db = next(get_db())
    seed_exercises(db)
    print("Exercises seeded successfully!") 