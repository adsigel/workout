from app.main import app
from app.models import MovementType, MuscleGroupType
from fastapi.testclient import TestClient
import json

client = TestClient(app)

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
    }
]

# Convert enum values to strings for JSON serialization
exercises_json = []
for exercise in exercises:
    exercise_json = exercise.copy()
    exercise_json["movement_types"] = [mt.value for mt in exercise["movement_types"]]
    exercise_json["muscle_groups"] = [mg.value for mg in exercise["muscle_groups"]]
    exercises_json.append(exercise_json)

# Send the request to create all exercises
response = client.post("/exercises/bulk", json=exercises_json)
print(f"Created {len(response.json())} exercises") 