'use client';

import { useState } from 'react';

const MUSCLE_GROUPS = [
  'chest', 'front_deltoids', 'side_deltoids', 'rear_deltoids', 'biceps', 'triceps', 'forearms', 'upper_back', 'lats',
  'abs', 'obliques', 'lower_back', 'quads', 'hamstrings', 'glutes', 'calves', 'adductors', 'abductors'
];

const MUSCLE_GROUP_CATEGORIES = {
  'UPPER BODY': [
    'chest', 'front_deltoids', 'side_deltoids', 'rear_deltoids', 'biceps', 'triceps', 'forearms', 'upper_back', 'lats'
  ],
  'CORE': [
    'abs', 'obliques', 'lower_back'
  ],
  'LOWER BODY': [
    'quads', 'hamstrings', 'glutes', 'calves', 'adductors', 'abductors'
  ]
};

const EQUIPMENT = [
  'kettlebell', 'dumbbell', 'stall bars'
];

const DURATION_OPTIONS = [15, 20, 30, 45];

const INTENSITY_LEVELS = [
  { value: 1, label: '1 (Low)' },
  { value: 2, label: '2 (Low/Medium)' },
  { value: 3, label: '3 (Medium)' },
  { value: 4, label: '4 (Medium/High)' },
  { value: 5, label: '5 (High)' },
];

interface Exercise {
  id: number;
  name: string;
  description: string;
  estimated_duration: number;
  equipment: { name: string }[];
  muscle_groups: { name: string }[];
  movement_types: string[];
  intensity?: string;
}

interface Workout {
  exercises: Exercise[];
  rounds: number;
  estimated_duration_minutes: number;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Home() {
  const [duration, setDuration] = useState(20);
  const [workout, setWorkout] = useState<Workout | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedMuscleGroups, setSelectedMuscleGroups] = useState<string[]>([...MUSCLE_GROUPS]);
  const [selectedEquipment, setSelectedEquipment] = useState<string[]>([...EQUIPMENT]);
  const [intensityLevel, setIntensityLevel] = useState(3);
  const [swapLoadingIndex, setSwapLoadingIndex] = useState<number | null>(null);

  const handleMuscleGroupChange = (group: string) => {
    setSelectedMuscleGroups((prev) =>
      prev.includes(group)
        ? prev.filter((g) => g !== group)
        : [...prev, group]
    );
  };

  const handleEquipmentChange = (equipment: string) => {
    setSelectedEquipment((prev) =>
      prev.includes(equipment)
        ? prev.filter((e) => e !== equipment)
        : [...prev, equipment]
    );
  };

  const generateWorkout = async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({
        duration_minutes: duration.toString(),
      });
      selectedMuscleGroups.forEach((mg) => params.append('muscle_groups', mg));
      selectedEquipment.forEach((eq) => params.append('equipment', eq));
      params.append('intensity_level', intensityLevel.toString());
      const response = await fetch(`${API_URL}/workouts/generate?${params.toString()}`);
      if (!response.ok) {
        throw new Error('Failed to generate workout');
      }
      const data = await response.json();
      setWorkout(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleSwapExercise = async (swapIndex: number) => {
    if (!workout) return;
    setSwapLoadingIndex(swapIndex);
    setError(null);
    try {
      const params = new URLSearchParams({
        intensity_level: intensityLevel.toString(),
      });
      selectedMuscleGroups.forEach((mg) => params.append('muscle_groups', mg));
      selectedEquipment.forEach((eq) => params.append('equipment', eq));
      const current_workout_ids = workout.exercises.map((ex) => ex.id);
      const swap_out_id = workout.exercises[swapIndex].id;
      const response = await fetch(`${API_URL}/workouts/swap_exercise?${params.toString()}`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ current_workout_ids, swap_out_id })
        });
      if (!response.ok) {
        throw new Error('Failed to swap exercise');
      }
      const newExercise = await response.json();
      setWorkout((prev) => {
        if (!prev) return prev;
        const newExercises = [...prev.exercises];
        newExercises[swapIndex] = newExercise;
        return { ...prev, exercises: newExercises };
      });
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setSwapLoadingIndex(null);
    }
  };

  return (
    <>
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
            <div className="max-w-md mx-auto">
              <div className="divide-y divide-gray-200">
                <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                  <h2 className="text-2xl font-bold mb-8">Generate Workout</h2>
                  
                  {/* Duration Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Duration (minutes)</label>
                    <select
                      value={duration}
                      onChange={(e) => setDuration(Number(e.target.value))}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm rounded-md"
                    >
                      {DURATION_OPTIONS.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </div>

                  {/* Muscle Groups Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-bold text-gray-700 mb-2">Muscle Groups</label>
                    <div className="space-y-2">
                      {Object.entries(MUSCLE_GROUP_CATEGORIES).map(([category, groups]) => (
                        <div key={category}>
                          <div className="font-semibold text-xs text-gray-500 mb-1 mt-2 uppercase">{category}</div>
                          <div className="grid grid-cols-2 gap-2">
                            {groups.map((group) => (
                              <label key={group} className="inline-flex items-center">
                                <input
                                  type="checkbox"
                                  checked={selectedMuscleGroups.includes(group)}
                                  onChange={() => handleMuscleGroupChange(group)}
                                  className="form-checkbox h-4 w-4 text-orange-600"
                                />
                                <span className="ml-2 text-sm text-gray-700">{group.replace('_', ' ')}</span>
                              </label>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Equipment Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-bold text-gray-700 mb-2">Equipment (click to exclude)</label>
                    <div className="grid grid-cols-2 gap-2">
                      {EQUIPMENT.map((equipment) => (
                        <label key={equipment} className="inline-flex items-center">
                          <input
                            type="checkbox"
                            checked={selectedEquipment.includes(equipment)}
                            onChange={() => handleEquipmentChange(equipment)}
                            className="form-checkbox h-4 w-4 text-orange-600"
                          />
                          <span className="ml-2 text-sm text-gray-700">{equipment.replace('_', ' ')}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Intensity Level Selection */}
                  <div className="mb-6">
                    <label className="block text-sm font-medium text-gray-700 mb-2">Intensity Level</label>
                    <select
                      value={intensityLevel}
                      onChange={(e) => setIntensityLevel(Number(e.target.value))}
                      className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-orange-500 focus:border-orange-500 sm:text-sm rounded-md"
                    >
                      {INTENSITY_LEVELS.map((option) => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </select>
                  </div>

                  <button
                    onClick={generateWorkout}
                    disabled={loading}
                    className="w-full flex justify-center py-4 px-4 border border-transparent rounded-md shadow-lg text-2xl font-bold text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
                  >
                    {loading ? 'Generating...' : 'Generate Workout'}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Workout Display */}
        {error && (
          <div className="mt-4 text-red-600 text-center">{error}</div>
        )}

        {workout && (
          <div className="mt-8 max-w-2xl mx-auto px-4">
            <div className="bg-white shadow rounded-lg p-6">
              <h2 className="text-xl font-semibold mb-4">
                Your {workout.estimated_duration_minutes}-Minute Workout
                <span className="text-gray-500 text-sm ml-2">({workout.rounds} rounds)</span>
              </h2>
              
              <div className="space-y-4">
                {workout.exercises.map((exercise, index) => (
                  <div key={exercise.id} className="border-b border-gray-200 pb-4 last:border-0">
                    <div className="flex items-center gap-2">
                      <h3 className="font-medium mb-0">{index + 1}. {exercise.name}</h3>
                      <button
                        className="ml-2 text-xs px-2 py-1 rounded bg-gray-200 hover:bg-gray-300 focus:outline-none"
                        title="Swap exercise"
                        onClick={() => handleSwapExercise(index)}
                        disabled={swapLoadingIndex === index}
                      >
                        {swapLoadingIndex === index ? '...' : '🔄'}
                      </button>
                      {exercise.equipment.length > 0 && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 uppercase">
                          {exercise.equipment.map(e => e.name === 'kettlebell' ? 'KB' : e.name === 'dumbbell' ? 'DB' : e.name.toUpperCase()).join(', ')}
                        </span>
                      )}
                      {exercise.intensity && (
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold ${exercise.intensity === 'high' ? 'bg-red-200 text-red-800' : exercise.intensity === 'medium' ? 'bg-yellow-100 text-yellow-800' : 'bg-green-100 text-green-800'}`}>{exercise.intensity.toUpperCase()}</span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{exercise.description}</p>
                    <div className="mt-2 flex flex-wrap gap-2">
                      {exercise.movement_types.length > 0 && (
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                          {exercise.movement_types.join(', ')}
                        </span>
                      )}
                      {exercise.muscle_groups.map((group) => (
                        <span
                          key={group.name}
                          className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800"
                        >
                          {group.name}
                        </span>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
} 