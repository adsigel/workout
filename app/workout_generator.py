from typing import List, Dict, Set
from sqlalchemy.orm import Session
from . import models
from .models import MovementType, MuscleGroupType
import random

class WorkoutGenerator:
    def __init__(self, db: Session):
        self.db = db
        self.required_movement_types = {
            MovementType.PUSH,
            MovementType.PULL,
            MovementType.SQUAT,
            MovementType.HINGE,
            MovementType.CORE,
            MovementType.TWIST
        }
        self.core_movement_types = {MovementType.CORE, MovementType.TWIST}
        
    def get_exercises_by_movement_type(self, movement_type: MovementType) -> List[models.Exercise]:
        """Get all exercises of a specific movement type."""
        # Get all exercise IDs that have this movement type
        stmt = models.exercise_movement_types.select().where(
            models.exercise_movement_types.c.movement_type == movement_type.value
        )
        result = self.db.execute(stmt)
        exercise_ids = [row[0] for row in result]
        
        if not exercise_ids:
            return []
            
        # Get the full exercise objects
        return self.db.query(models.Exercise).filter(models.Exercise.id.in_(exercise_ids)).all()
    
    def get_exercises_by_movement_types(self, movement_types: Set[MovementType]) -> List[models.Exercise]:
        """Get all exercises that match any of the given movement types."""
        exercises = []
        for movement_type in movement_types:
            exercises.extend(self.get_exercises_by_movement_type(movement_type))
        return exercises
    
    def get_muscle_groups(self, exercise: models.Exercise) -> Set[MuscleGroupType]:
        """Get all muscle groups targeted by an exercise."""
        return {mg.name for mg in exercise.muscle_groups}
    
    def has_overlapping_muscle_groups(self, exercise1: models.Exercise, exercise2: models.Exercise) -> bool:
        """Check if two exercises target any of the same muscle groups."""
        muscle_groups1 = self.get_muscle_groups(exercise1)
        muscle_groups2 = self.get_muscle_groups(exercise2)
        return bool(muscle_groups1.intersection(muscle_groups2))
    
    def select_exercise_for_movement_type(self, movement_type: MovementType, 
                                        excluded_exercises: Set[models.Exercise]) -> models.Exercise:
        """Select a random exercise for a movement type, excluding already selected exercises."""
        available_exercises = [ex for ex in self.get_exercises_by_movement_type(movement_type)
                             if ex not in excluded_exercises]
        if not available_exercises:
            # If no exercises found for this movement type, try core movement types
            if movement_type in self.core_movement_types:
                core_exercises = []
                for core_type in self.core_movement_types:
                    core_exercises.extend(self.get_exercises_by_movement_type(core_type))
                available_exercises = [ex for ex in core_exercises if ex not in excluded_exercises]
            
            if not available_exercises:
                raise ValueError(f"No available exercises for movement type {movement_type}")
                
        return random.choice(available_exercises)
    
    def generate_superset(self, size: int = 5) -> List[models.Exercise]:
        """Generate a superset of exercises that target different muscle groups."""
        selected_exercises = set()
        
        # First, ensure we have one of each required movement type
        for movement_type in self.required_movement_types:
            try:
                exercise = self.select_exercise_for_movement_type(movement_type, selected_exercises)
                selected_exercises.add(exercise)
            except ValueError as e:
                # If we can't find an exercise for a specific movement type, skip it
                # (this should only happen for CORE/TWIST since they're interchangeable)
                if movement_type not in self.core_movement_types:
                    raise e
                continue
        
        # If we need more exercises, add them while avoiding muscle group overlap
        while len(selected_exercises) < size:
            all_exercises = self.db.query(models.Exercise).all()
            available_exercises = [ex for ex in all_exercises 
                                 if ex not in selected_exercises and
                                 not any(self.has_overlapping_muscle_groups(ex, selected) 
                                       for selected in selected_exercises)]
            
            if not available_exercises:
                break  # Can't add more exercises without overlap
                
            selected_exercises.add(random.choice(available_exercises))
        
        return list(selected_exercises)
    
    def calculate_workout_duration(self, exercises: List[models.Exercise], 
                                 rounds: int = 2) -> int:
        """Calculate total workout duration in seconds."""
        # Warm-up and stretching
        total_duration = 5 * 60  # 5 minutes
        
        # Exercise duration
        for exercise in exercises:
            # Exercise duration + rest between exercises
            total_duration += (exercise.estimated_duration + 30) * rounds
        
        # Rest between rounds
        total_duration += 90 * (rounds - 1)  # 1.5 minutes between rounds
        
        return total_duration
    
    def generate_workout(self, duration_minutes: int, allowed_muscle_groups: list[str] = None, allowed_equipment: list[str] = None) -> Dict:
        """Generate a workout with the specified duration in minutes, optionally filtering by allowed muscle groups and equipment."""
        exercises = self.db.query(models.Exercise).all()
        if not exercises:
            raise ValueError("No exercises available in the database")

        # Deduplicate exercises by name
        unique_exercises = {}
        for ex in exercises:
            if ex.name not in unique_exercises:
                unique_exercises[ex.name] = ex
        exercises = list(unique_exercises.values())

        # Filter by allowed muscle groups if provided
        if allowed_muscle_groups:
            allowed_mg_set = set(allowed_muscle_groups)
            def is_allowed_by_mg(ex):
                ex_mgs = {mg.name for mg in ex.muscle_groups}
                # Only include exercises where all muscle groups are in the allowed set
                return ex_mgs.issubset(allowed_mg_set)
            filtered_exercises = list(filter(is_allowed_by_mg, exercises))
            if filtered_exercises:
                exercises = filtered_exercises

        # Filter by allowed equipment if provided
        if allowed_equipment:
            allowed_equip_set = set(allowed_equipment)
            def is_allowed_by_equip(ex):
                ex_equip = {e.name for e in ex.equipment}
                # Include exercise if ANY of its equipment is in the allowed set
                return bool(ex_equip.intersection(allowed_equip_set))
            filtered_exercises = list(filter(is_allowed_by_equip, exercises))
            if filtered_exercises:
                exercises = filtered_exercises

        min_exercises = 3
        max_exercises = min(10, len(exercises))
        min_rounds = 1
        max_rounds = 4

        best_config = None
        best_diff = float('inf')
        target_seconds = duration_minutes * 60

        # Try different combinations of exercises and rounds
        for num_exercises in range(min_exercises, max_exercises + 1):
            for num_rounds in range(min_rounds, max_rounds + 1):
                if num_exercises > len(exercises):
                    continue
                selected = random.sample(exercises, num_exercises)
                total_seconds = self.calculate_workout_duration(selected, num_rounds)
                diff = abs(total_seconds - target_seconds)
                if diff < best_diff:
                    best_diff = diff
                    best_config = (selected, num_rounds, total_seconds)
                if diff == 0:
                    break

        workout_exercises, rounds, total_seconds = best_config
        estimated_duration_minutes = round(total_seconds / 60)

        return {
            "exercises": workout_exercises,
            "rounds": rounds,
            "estimated_duration_minutes": estimated_duration_minutes
        } 