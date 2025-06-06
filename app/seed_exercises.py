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
            ],
            "intensity": "high"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "high"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "medium"
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
            ],
            "intensity": "high"
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
            ],
            "intensity": "medium"
        },
        {
            "name": "Kettlebell Side Bend",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell in one hand. Bend sideways at the waist, keeping the back straight. Return to starting position. Complete all reps on one side before switching.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,  # seconds
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Standing Dumbbell Wood Chops",
            "description": "Stand with feet shoulder-width apart, holding a dumbbell with both hands. Start with the weight at one hip, then swing it diagonally across the body to the opposite shoulder, rotating the torso. Return to starting position.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Standing Overhead Press",
            "description": "Stand with feet shoulder-width apart, holding weights at shoulder height. Press the weights overhead until arms are fully extended, then lower back to starting position.",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 45,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS],
            "intensity": "medium"
        },
        {
            "name": "Mountain Climbers",
            "description": "Start in a plank position. Alternately bring knees toward chest in a running motion, keeping hips low and core engaged.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 45,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Bent-Over Kettlebell Row (Two Hand)",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell with both hands. Hinge at hips, keeping back straight. Pull the kettlebell to the chest, then lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.BICEPS],
            "intensity": "medium"
        },
        {
            "name": "Bent-Over Kettlebell Row (One Hand)",
            "description": "Stand with feet staggered, holding a kettlebell in one hand. Hinge at hips, keeping back straight. Pull the kettlebell to the chest, then lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.BICEPS],
            "intensity": "medium"
        },
        {
            "name": "Kettlebell High Pull",
            "description": "Stand with feet shoulder-width apart, holding a kettlebell between legs. Explosively pull the kettlebell up to chest height, keeping elbows high. Lower with control.",
            "movement_types": [MovementType.PULL, MovementType.HINGE],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.UPPER_BACK, MuscleGroupType.LATS, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Plank Pull-Through",
            "description": "Start in a plank position with a weight beside you. Reach under with one hand to grab the weight, pull it across to the other side, then repeat in the opposite direction.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 45,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Side Plank Underarm Twist",
            "description": "Start in a side plank position. Rotate the top arm under the body, then back to starting position. Complete all reps on one side before switching.",
            "movement_types": [MovementType.CORE, MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Kneeling Dumbbell Straight Arm Chop",
            "description": "Kneel on one knee, holding a dumbbell with both hands. Start with arms extended overhead, then chop diagonally across the body, rotating the torso.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Racked Kettlebell Squat",
            "description": "Hold kettlebells in the rack position (at shoulder height). Perform a squat, keeping chest up and core engaged. Return to standing position.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS, MuscleGroupType.LOWER_BACK],
            "intensity": "medium"
        },
        {
            "name": "Deadbugs",
            "description": "A core stability exercise performed lying on your back, optionally holding a dumbbell or kettlebell in each hand.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 40,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Curtsy Goblet Lunge",
            "description": "A lunge variation where you step one leg behind and across the other, holding a kettlebell at your chest.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS],
            "intensity": "medium"
        },
        {
            "name": "Kickstand Single Arm Deadlift",
            "description": "A unilateral hinge movement with a kettlebell, using a kickstand stance for balance.",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.HAMSTRINGS, MuscleGroupType.GLUTES, MuscleGroupType.LOWER_BACK, MuscleGroupType.FOREARMS],
            "intensity": "medium"
        },
        {
            "name": "Pull-ups",
            "description": "A vertical pulling exercise performed on stall bars.",
            "movement_types": [MovementType.PULL],
            "estimated_duration": 30,
            "equipment": ["stall bars"],
            "muscle_groups": [MuscleGroupType.LATS, MuscleGroupType.BICEPS, MuscleGroupType.UPPER_BACK],
            "intensity": "medium"
        },
        {
            "name": "Tricep Dips",
            "description": "A bodyweight pushing exercise performed on stall bars to target the triceps.",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 30,
            "equipment": ["stall bars"],
            "muscle_groups": [MuscleGroupType.TRICEPS, MuscleGroupType.CHEST, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Bicep Curls",
            "description": "A classic arm exercise performed with dumbbells or kettlebells.",
            "movement_types": [MovementType.PULL],
            "estimated_duration": 30,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.BICEPS, MuscleGroupType.FOREARMS],
            "intensity": "medium"
        },
        {
            "name": "Hip Bridges",
            "description": "A glute and hamstring exercise performed on the floor, optionally with a dumbbell for added resistance.",
            "movement_types": [MovementType.HINGE],
            "estimated_duration": 35,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.GLUTES, MuscleGroupType.HAMSTRINGS, MuscleGroupType.LOWER_BACK],
            "intensity": "medium"
        },
        {
            "name": "Reverse Goblet Lunge",
            "description": "A lunge variation stepping backward, holding a kettlebell at your chest.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS],
            "intensity": "medium"
        },
        {
            "name": "Overhead March",
            "description": "March in place while holding a kettlebell or dumbbell overhead, engaging the core and shoulders.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 35,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Squat Thruster with a Twist",
            "description": "A full-body movement: squat holding a dumbbell, then press overhead and rotate the torso at the top.",
            "movement_types": [MovementType.SQUAT, MovementType.PUSH, MovementType.TWIST],
            "estimated_duration": 45,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS, MuscleGroupType.OBLIQUES, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS],
            "intensity": "high"
        },
        {
            "name": "Bicep Hammer Curls",
            "description": "Stand with feet shoulder-width apart, holding dumbbells with palms facing each other. Curl the weights up while keeping palms facing inward throughout the movement.",
            "movement_types": [MovementType.PULL],
            "estimated_duration": 35,
            "equipment": ["dumbbell"],
            "muscle_groups": [MuscleGroupType.BICEPS, MuscleGroupType.FOREARMS],
            "intensity": "medium"
        },
        {
            "name": "Pushup into Side Plank",
            "description": "Start in a pushup position. Perform a pushup, then rotate into a side plank, raising one arm toward the ceiling. Return to pushup position and repeat on the other side.",
            "movement_types": [MovementType.PUSH, MovementType.CORE],
            "estimated_duration": 45,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.CHEST, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS, MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Sumo Squat",
            "description": "Stand with feet wide apart, toes pointed slightly outward. Hold a weight between your legs and perform a squat, keeping chest up and knees tracking over toes.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["kettlebell", "dumbbell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ADDUCTORS, MuscleGroupType.ABS],
            "intensity": "medium"
        },
        {
            "name": "Single-arm Kettlebell Clean",
            "description": "Start with kettlebell between feet. Hinge at hips, grab kettlebell, and explosively pull it up to rack position, keeping it close to body.",
            "movement_types": [MovementType.HINGE, MovementType.PULL],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.HAMSTRINGS, MuscleGroupType.GLUTES, MuscleGroupType.FOREARMS, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "high"
        },
        {
            "name": "Lateral Lunge",
            "description": "Step to the side, keeping toes pointed forward. Bend the knee of the stepping leg while keeping the other leg straight. Return to center and repeat on other side.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 40,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ADDUCTORS, MuscleGroupType.ABDUCTORS],
            "intensity": "medium"
        },
        {
            "name": "Boxer Squat",
            "description": "Perform a squat while holding weights at chest height, alternating between left and right sides like a boxer's stance.",
            "movement_types": [MovementType.SQUAT],
            "estimated_duration": 45,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Russian Twists",
            "description": "Sit on floor with knees bent, holding weight. Lean back slightly and rotate torso from side to side, keeping core engaged.",
            "movement_types": [MovementType.TWIST],
            "estimated_duration": 40,
            "equipment": ["dumbbell", "kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Leg Raises",
            "description": "Lie on back with legs straight. Raise legs to vertical position, then lower back down with control, keeping lower back pressed into floor.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 35,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.LOWER_BACK],
            "intensity": "medium"
        },
        {
            "name": "Windshield Wipers",
            "description": "Lie on back with arms extended to sides. Raise legs to vertical, then lower them side to side like windshield wipers, keeping shoulders on ground.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 40,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.OBLIQUES],
            "intensity": "medium"
        },
        {
            "name": "Goblet Overhead Press",
            "description": "Hold a kettlebell by the horns at chest height and press it overhead, keeping your core engaged.",
            "movement_types": [MovementType.PUSH],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS, MuscleGroupType.ABS],
            "intensity": "medium"
        },
        {
            "name": "Shoulder Taps",
            "description": "From a plank position, tap each shoulder with the opposite hand, keeping hips steady.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 30,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS],
            "intensity": "low"
        },
        {
            "name": "Standing Knee to Elbow Twists",
            "description": "Stand tall, bring one knee up and twist your torso to touch the opposite elbow to the knee.",
            "movement_types": [MovementType.TWIST, MovementType.CORE],
            "estimated_duration": 30,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.OBLIQUES, MuscleGroupType.ABS, MuscleGroupType.HAMSTRINGS],
            "intensity": "low"
        },
        {
            "name": "Push Up Walkouts",
            "description": "From standing, hinge at the hips, walk your hands out to a pushup position, perform a pushup, then walk back and stand.",
            "movement_types": [MovementType.PUSH, MovementType.HINGE, MovementType.CORE],
            "estimated_duration": 40,
            "equipment": [],
            "muscle_groups": [MuscleGroupType.CHEST, MuscleGroupType.ABS, MuscleGroupType.HAMSTRINGS, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Two-handed Kettlebell Clean to Press",
            "description": "Clean a kettlebell to chest height with both hands, then press it overhead.",
            "movement_types": [MovementType.HINGE, MovementType.PUSH],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.GLUTES, MuscleGroupType.HAMSTRINGS, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS, MuscleGroupType.ABS],
            "intensity": "high"
        },
        {
            "name": "One-handed Kettlebell Clean to Press",
            "description": "Clean a kettlebell to the rack position with one hand, then press it overhead.",
            "movement_types": [MovementType.HINGE, MovementType.PUSH],
            "estimated_duration": 40,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.GLUTES, MuscleGroupType.HAMSTRINGS, MuscleGroupType.FRONT_DELTOIDS, MuscleGroupType.TRICEPS, MuscleGroupType.ABS],
            "intensity": "high"
        },
        {
            "name": "Kettlebell Racked March",
            "description": "Hold a kettlebell in the rack position and march in place, keeping your core tight.",
            "movement_types": [MovementType.CORE],
            "estimated_duration": 35,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.ABS, MuscleGroupType.QUADS, MuscleGroupType.GLUTES, MuscleGroupType.FRONT_DELTOIDS],
            "intensity": "medium"
        },
        {
            "name": "Two-handed Kettlebell Clean to Squat",
            "description": "Clean a kettlebell to chest height with both hands, then perform a squat.",
            "movement_types": [MovementType.HINGE, MovementType.SQUAT],
            "estimated_duration": 45,
            "equipment": ["kettlebell"],
            "muscle_groups": [MuscleGroupType.GLUTES, MuscleGroupType.HAMSTRINGS, MuscleGroupType.QUADS, MuscleGroupType.ABS],
            "intensity": "high"
        }
    ]
    
    # Validate muscle groups before proceeding
    validate_muscle_groups(exercises)
    
    # Get existing exercise names
    existing_exercises = {ex.name for ex in db.query(models.Exercise).all()}
    
    # Track which exercises were added
    added_exercises = []
    skipped_exercises = []
    
    for exercise_data in exercises:
        db_exercise = db.query(models.Exercise).filter(models.Exercise.name == exercise_data["name"]).first()
        if db_exercise:
            # Update intensity if needed
            db_exercise.intensity = exercise_data["intensity"]
            db.commit()
            skipped_exercises.append(exercise_data["name"])
            continue
        # Create exercise
        db_exercise = models.Exercise(
            name=exercise_data["name"],
            description=exercise_data["description"],
            estimated_duration=exercise_data["estimated_duration"],
            intensity=exercise_data["intensity"]
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

        added_exercises.append(exercise_data["name"])

    db.commit()
    
    # Return summary of what was added and skipped
    return {
        "added": added_exercises,
        "skipped": skipped_exercises,
        "total_added": len(added_exercises),
        "total_skipped": len(skipped_exercises)
    }

if __name__ == "__main__":
    # List valid muscle groups before seeding
    list_valid_muscle_groups()
    
    db = next(get_db())
    result = seed_exercises(db)
    print("\nSeeding Summary:")
    print(f"Added {result['total_added']} new exercises:")
    for name in result["added"]:
        print(f"- {name}")
    print(f"\nSkipped {result['total_skipped']} existing exercises:")
    for name in result["skipped"]:
        print(f"- {name}") 