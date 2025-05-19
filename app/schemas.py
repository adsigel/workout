from pydantic import BaseModel
from typing import List, Optional
from .models import MovementType, MuscleGroupType

class EquipmentBase(BaseModel):
    name: str

class EquipmentCreate(EquipmentBase):
    pass

class Equipment(EquipmentBase):
    id: int

    class Config:
        from_attributes = True

class MuscleGroupBase(BaseModel):
    name: MuscleGroupType

class MuscleGroupCreate(MuscleGroupBase):
    pass

class MuscleGroup(MuscleGroupBase):
    id: int

    class Config:
        from_attributes = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    movement_types: List[MovementType]
    estimated_duration: int
    equipment: List[str]
    muscle_groups: List[MuscleGroupType]

class ExerciseCreate(ExerciseBase):
    pass

class Exercise(ExerciseBase):
    id: int
    equipment: List[Equipment]
    muscle_groups: List[MuscleGroup]

    class Config:
        from_attributes = True

class Workout(BaseModel):
    exercises: List[Exercise]
    rounds: int
    estimated_duration_minutes: int 