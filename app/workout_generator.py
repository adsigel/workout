from typing import List, Dict, Set, Optional
from sqlalchemy.orm import Session
from . import models
from .models import MovementType, MuscleGroupType
import random
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    
    def is_frontal_or_transverse(self, exercise: models.Exercise) -> bool:
        """Return True if exercise is frontal or transverse plane (TWIST or targets side_deltoids, adductors, abductors)."""
        movement_types = self.get_movement_types(exercise)
        muscle_groups = self.get_muscle_groups(exercise)
        if MovementType.TWIST in movement_types:
            return True
        frontal_mgs = {MuscleGroupType.SIDE_DELTOIDS, MuscleGroupType.ADDUCTORS, MuscleGroupType.ABDUCTORS}
        return bool(frontal_mgs.intersection(muscle_groups))

    def generate_workout(self, duration_minutes: int, allowed_muscle_groups: list[str] = None, allowed_equipment: list[str] = None, intensity_level: int = 3) -> Dict:
        """Generate a workout with the specified duration in minutes, optionally filtering by allowed muscle groups, equipment, and intensity level (1-5)."""
        try:
            logger.info(f"Starting workout generation with params: duration={duration_minutes}, muscle_groups={allowed_muscle_groups}, equipment={allowed_equipment}, intensity_level={intensity_level}")
            
            INTENSITY_MAP = {
                1: ["low"],
                2: ["low", "medium"],
                3: ["medium"],
                4: ["medium", "high"],
                5: ["high"]
            }
            allowed_intensities = INTENSITY_MAP.get(intensity_level, ["medium"])
            
            exercises = self.db.query(models.Exercise).all()
            if not exercises:
                raise ValueError("No exercises available in the database")
            
            logger.info(f"Found {len(exercises)} total exercises")

            # Deduplicate exercises by name
            unique_exercises = {}
            for ex in exercises:
                if ex.name not in unique_exercises:
                    unique_exercises[ex.name] = ex
            exercises = list(unique_exercises.values())
            logger.info(f"After deduplication: {len(exercises)} exercises")

            # Store original exercises for fallback
            original_exercises = exercises.copy()

            # Filter by allowed muscle groups if provided
            if allowed_muscle_groups:
                allowed_mg_set = set(allowed_muscle_groups)
                def is_allowed_by_mg(ex):
                    ex_mgs = {mg.name for mg in ex.muscle_groups}
                    return ex_mgs.issubset(allowed_mg_set)
                filtered_exercises = list(filter(is_allowed_by_mg, exercises))
                if filtered_exercises:
                    exercises = filtered_exercises
                    logger.info(f"After muscle group filtering: {len(exercises)} exercises")

            # Filter by allowed equipment if provided
            if allowed_equipment:
                allowed_equip_set = set(allowed_equipment)
                def is_allowed_by_equip(ex):
                    ex_equip = {e.name for e in ex.equipment}
                    return bool(ex_equip.intersection(allowed_equip_set))
                filtered_exercises = list(filter(is_allowed_by_equip, exercises))
                if filtered_exercises:
                    exercises = filtered_exercises
                    logger.info(f"After equipment filtering: {len(exercises)} exercises")

            # Filter by allowed intensities
            filtered_exercises = [ex for ex in exercises if (getattr(ex, 'intensity', None) or 'medium') in allowed_intensities]
            if filtered_exercises:
                exercises = filtered_exercises
                logger.info(f"After intensity_level filtering: {len(exercises)} exercises")

            # If we have too few exercises after filtering, fall back to less strict filtering
            if len(exercises) < 3:
                logger.info("Too few exercises after strict filtering, falling back to less strict filtering")
                exercises = original_exercises.copy()
                # Try filtering by just muscle groups and equipment
                if allowed_muscle_groups or allowed_equipment:
                    filtered_exercises = exercises
                    if allowed_muscle_groups:
                        allowed_mg_set = set(allowed_muscle_groups)
                        filtered_exercises = [ex for ex in filtered_exercises if any(mg.name in allowed_mg_set for mg in ex.muscle_groups)]
                    if allowed_equipment and filtered_exercises:
                        allowed_equip_set = set(allowed_equipment)
                        filtered_exercises = [ex for ex in filtered_exercises if any(e.name in allowed_equip_set for e in ex.equipment)]
                    if filtered_exercises:
                        exercises = filtered_exercises
                    logger.info(f"After less strict filtering: {len(exercises)} exercises")
            if len(exercises) < 3:
                logger.info("Still too few exercises, using all exercises")
                exercises = original_exercises

            # Identify all frontal/transverse exercises
            frontal_transverse_exercises = [ex for ex in exercises if self.is_frontal_or_transverse(ex)]
            logger.info(f"Found {len(frontal_transverse_exercises)} frontal/transverse exercises")

            # Determine how many are required
            if duration_minutes <= 20:
                required_count = 1
            else:
                required_count = 2

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
                        candidates = [ex for ex in available if not previous_exercise or not self.are_exercises_similar(ex, previous_exercise)]
                        if not candidates:
                            candidates = available
                        exercise = random.choice(candidates)
                        selected.append(exercise)
                        available.remove(exercise)
                        previous_exercise = exercise
                    if len(selected) < num_exercises:
                        continue
                    # Ensure required number of frontal/transverse exercises
                    ft_count = sum(1 for ex in selected if self.is_frontal_or_transverse(ex))
                    if ft_count < required_count and len(frontal_transverse_exercises) >= required_count:
                        # Replace random exercises with frontal/transverse ones
                        to_add = required_count - ft_count
                        # Find which ones are missing
                        missing = [ex for ex in frontal_transverse_exercises if ex not in selected]
                        if len(missing) >= to_add:
                            # Replace random non-frontal/transverse exercises
                            non_ft_indices = [i for i, ex in enumerate(selected) if not self.is_frontal_or_transverse(ex)]
                            for i in non_ft_indices[:to_add]:
                                selected[i] = missing.pop()
                    # Recount after replacement
                    ft_count = sum(1 for ex in selected if self.is_frontal_or_transverse(ex))
                    if ft_count < required_count:
                        continue  # Skip this config if we can't meet the requirement
                    total_seconds = self.calculate_workout_duration(selected, num_rounds)
                    diff = abs(total_seconds - target_seconds)
                    if diff < best_diff:
                        best_diff = diff
                        best_config = (selected, num_rounds, total_seconds)
                    if diff == 0:
                        break

            if best_config is None:
                raise ValueError("Could not generate a workout with the given constraints")

            workout_exercises, rounds, total_seconds = best_config
            estimated_duration_minutes = round(total_seconds / 60)
            
            logger.info(f"Successfully generated workout with {len(workout_exercises)} exercises, {rounds} rounds, {estimated_duration_minutes} minutes")
            
            return {
                "exercises": workout_exercises,
                "rounds": rounds,
                "estimated_duration_minutes": estimated_duration_minutes
            }
        except Exception as e:
            logger.error(f"Error generating workout: {str(e)}")
            raise 

    def swap_exercise(self, current_workout_ids: list[int], swap_out_id: int, allowed_muscle_groups: list[str] = None, allowed_equipment: list[str] = None, intensity_level: int = 3) -> models.Exercise:
        INTENSITY_MAP = {
            1: ["low"],
            2: ["low", "medium"],
            3: ["medium"],
            4: ["medium", "high"],
            5: ["high"]
        }
        allowed_intensities = INTENSITY_MAP.get(intensity_level, ["medium"])
        exercises = self.db.query(models.Exercise).all()
        # Deduplicate by name
        unique_exercises = {}
        for ex in exercises:
            if ex.name not in unique_exercises:
                unique_exercises[ex.name] = ex
        exercises = list(unique_exercises.values())
        # Filter by muscle groups
        if allowed_muscle_groups:
            allowed_mg_set = set(allowed_muscle_groups)
            def is_allowed_by_mg(ex):
                ex_mgs = {mg.name for mg in ex.muscle_groups}
                return ex_mgs.issubset(allowed_mg_set)
            filtered_exercises = list(filter(is_allowed_by_mg, exercises))
            if filtered_exercises:
                exercises = filtered_exercises
        # Filter by equipment
        if allowed_equipment:
            allowed_equip_set = set(allowed_equipment)
            def is_allowed_by_equip(ex):
                ex_equip = {e.name for e in ex.equipment}
                return bool(ex_equip.intersection(allowed_equip_set))
            filtered_exercises = list(filter(is_allowed_by_equip, exercises))
            if filtered_exercises:
                exercises = filtered_exercises
        # Filter by intensity
        filtered_exercises = [ex for ex in exercises if (getattr(ex, 'intensity', None) or 'medium') in allowed_intensities]
        if filtered_exercises:
            exercises = filtered_exercises
        # Remove exercises already in the workout
        exercises = [ex for ex in exercises if ex.id not in current_workout_ids]
        # Find the index of the exercise to swap out
        try:
            idx = current_workout_ids.index(swap_out_id)
        except ValueError:
            raise ValueError("Exercise to swap out not found in current workout")
        # Get neighbors if any
        prev_id = current_workout_ids[idx-1] if idx > 0 else None
        next_id = current_workout_ids[idx+1] if idx < len(current_workout_ids)-1 else None
        prev_ex = next((ex for ex in self.db.query(models.Exercise).all() if ex.id == prev_id), None)
        next_ex = next((ex for ex in self.db.query(models.Exercise).all() if ex.id == next_id), None)
        # Prefer exercises that are not similar to neighbors
        candidates = exercises
        if prev_ex:
            candidates = [ex for ex in candidates if not self.are_exercises_similar(ex, prev_ex)]
        if next_ex:
            candidates = [ex for ex in candidates if not self.are_exercises_similar(ex, next_ex)]
        if not candidates:
            candidates = exercises  # fallback if too strict
        if not candidates:
            raise ValueError("No suitable replacement exercise found")
        return random.choice(candidates) 