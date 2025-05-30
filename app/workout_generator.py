from typing import List, Dict, Set, Optional
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
    
    def get_movement_types(self, exercise: models.Exercise) -> Set[MovementType]:
        """Get all movement types for an exercise."""
        stmt = models.exercise_movement_types.select().where(
            models.exercise_movement_types.c.exercise_id == exercise.id
        )
        result = self.db.execute(stmt)
        return {MovementType(mt[1]) for mt in result}
    
    def are_exercises_similar(self, exercise1: models.Exercise, exercise2: models.Exercise) -> bool:
        """Check if two exercises are too similar to be done in sequence."""
        # Get movement types and muscle groups
        movement_types1 = self.get_movement_types(exercise1)
        movement_types2 = self.get_movement_types(exercise2)
        muscle_groups1 = self.get_muscle_groups(exercise1)
        muscle_groups2 = self.get_muscle_groups(exercise2)
        
        # Check for movement type overlap
        movement_overlap = bool(movement_types1.intersection(movement_types2))
        
        # Check for significant muscle group overlap (more than 50% of muscle groups)
        common_muscle_groups = muscle_groups1.intersection(muscle_groups2)
        total_muscle_groups = muscle_groups1.union(muscle_groups2)
        muscle_overlap_ratio = len(common_muscle_groups) / len(total_muscle_groups)
        
        # Exercises are similar if they share movement types or have significant muscle group overlap
        return movement_overlap or muscle_overlap_ratio > 0.5
    
    def select_exercise_for_movement_type(self, movement_type: MovementType, 
                                        excluded_exercises: Set[models.Exercise],
                                        previous_exercise: Optional[models.Exercise] = None) -> models.Exercise:
        """Select a random exercise for a movement type, excluding already selected exercises and similar exercises."""
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
        
        # If there's a previous exercise, filter out similar ones
        if previous_exercise:
            available_exercises = [ex for ex in available_exercises 
                                 if not self.are_exercises_similar(ex, previous_exercise)]
            
            # If we filtered out all exercises, fall back to the original list
            if not available_exercises:
                available_exercises = [ex for ex in self.get_exercises_by_movement_type(movement_type)
                                     if ex not in excluded_exercises]
                
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
                
                # Select exercises ensuring no similar exercises are adjacent
                selected = []
                available = exercises.copy()
                previous_exercise = None
                
                while len(selected) < num_exercises and available:
                    # Try to find an exercise that's not similar to the previous one
                    candidates = [ex for ex in available if not previous_exercise or not self.are_exercises_similar(ex, previous_exercise)]
                    
                    # If no suitable candidates, fall back to any available exercise
                    if not candidates:
                        candidates = available
                    
                    exercise = random.choice(candidates)
                    selected.append(exercise)
                    available.remove(exercise)
                    previous_exercise = exercise
                
                if len(selected) < num_exercises:
                    continue  # Skip this configuration if we couldn't get enough exercises
                
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