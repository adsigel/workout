from sqlalchemy import Column, Integer, String, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class MovementType(enum.Enum):
    PUSH = "push"
    PULL = "pull"
    HINGE = "hinge"
    SQUAT = "squat"
    TWIST = "twist"
    CORE = "core"

class MuscleGroupType(enum.Enum):
    # Upper Body
    CHEST = "chest"  # Pectoralis major and minor
    FRONT_DELTOIDS = "front_deltoids"  # Anterior deltoids
    SIDE_DELTOIDS = "side_deltoids"  # Lateral deltoids
    REAR_DELTOIDS = "rear_deltoids"  # Posterior deltoids
    BICEPS = "biceps"  # Biceps brachii
    TRICEPS = "triceps"  # Triceps brachii
    FOREARMS = "forearms"  # Flexors and extensors
    UPPER_BACK = "upper_back"  # Trapezius, rhomboids
    LATS = "lats"  # Latissimus dorsi
    
    # Core
    ABS = "abs"  # Rectus abdominis
    OBLIQUES = "obliques"  # Internal and external obliques
    LOWER_BACK = "lower_back"  # Erector spinae
    
    # Lower Body
    QUADS = "quads"  # Quadriceps
    HAMSTRINGS = "hamstrings"  # Hamstrings
    GLUTES = "glutes"  # Gluteus maximus, medius, minimus
    CALVES = "calves"  # Gastrocnemius, soleus
    ADDUCTORS = "adductors"  # Adductor magnus, longus, brevis
    ABDUCTORS = "abductors"  # Gluteus medius, minimus, tensor fasciae latae

# Association tables for many-to-many relationships
exercise_equipment = Table(
    'exercise_equipment',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercises.id')),
    Column('equipment_id', Integer, ForeignKey('equipment.id'))
)

exercise_muscle_groups = Table(
    'exercise_muscle_groups',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercises.id')),
    Column('muscle_group_id', Integer, ForeignKey('muscle_groups.id'))
)

exercise_movement_types = Table(
    'exercise_movement_types',
    Base.metadata,
    Column('exercise_id', Integer, ForeignKey('exercises.id')),
    Column('movement_type', String)  # Store as string instead of Enum
)

class Exercise(Base):
    __tablename__ = 'exercises'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    equipment = relationship("Equipment", secondary=exercise_equipment, back_populates="exercises")
    muscle_groups = relationship("MuscleGroup", secondary=exercise_muscle_groups, back_populates="exercises")
    estimated_duration = Column(Integer)  # Duration in seconds
    intensity = Column(String, default='medium')  # 'low', 'medium', 'high'

class Equipment(Base):
    __tablename__ = 'equipment'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    exercises = relationship("Exercise", secondary=exercise_equipment, back_populates="equipment")

class MuscleGroup(Base):
    __tablename__ = 'muscle_groups'

    id = Column(Integer, primary_key=True)
    name = Column(Enum(MuscleGroupType), nullable=False, unique=True)
    exercises = relationship("Exercise", secondary=exercise_muscle_groups, back_populates="muscle_groups") 