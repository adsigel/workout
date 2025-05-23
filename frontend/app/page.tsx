'use client';

import { useState } from 'react';

const MUSCLE_GROUPS = [
  'chest', 'front_deltoids', 'side_deltoids', 'rear_deltoids', 'biceps', 'triceps', 'forearms', 'upper_back', 'lats',
  'abs', 'obliques', 'lower_back', 'quads', 'hamstrings', 'glutes', 'calves', 'adductors', 'abductors'
];

const DURATION_OPTIONS = [15, 20, 30, 45];

interface Exercise {
  id: number;
  name: string;
  description: string;
  estimated_duration: number;
  equipment: { name: string }[];
  muscle_groups: { name: string }[];
  movement_types: string[];
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

  const handleMuscleGroupChange = (group: string) => {
    setSelectedMuscleGroups((prev) =>
      prev.includes(group)
        ? prev.filter((g) => g !== group)
        : [...prev, group]
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

  return (
    <div className="space-y-6">
      <div className="bg-pink-500 text-white p-4 mb-4">Test Tailwind Color</div>
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Generate Workout</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
              Workout Duration (minutes)
            </label>
            <select
              id="duration"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 text-[20px]"
            >
              {DURATION_OPTIONS.map((option) => (
                <option key={option} value={option}>{option} minutes</option>
              ))}
            </select>
          </div>
          <div className="h-8"></div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2 mt-6">Muscle Groups</label>
            <div className="flex flex-col gap-2">
              {MUSCLE_GROUPS.map((group) => (
                <label key={group} className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={selectedMuscleGroups.includes(group)}
                    onChange={() => handleMuscleGroupChange(group)}
                    className="accent-blue-600"
                  />
                  <span className="text-base capitalize">{group.replace('_', ' ')}</span>
                </label>
              ))}
            </div>
          </div>
          <button
            onClick={generateWorkout}
            disabled={loading}
            className="w-full bg-orange-600 text-white py-3 px-4 rounded-md text-[24px] font-semibold hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 disabled:opacity-50 mt-6"
          >
            {loading ? 'Generating...' : 'Generate Workout'}
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-md">
          {error}
        </div>
      )}

      {workout && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-lg font-semibold mb-4">
            Your {workout.estimated_duration_minutes}-Minute Workout
          </h2>
          <p className="text-gray-600 mb-4">
            {workout.rounds} rounds of {workout.exercises.length} exercises
          </p>
          <div className="space-y-4">
            {workout.exercises.map((exercise, index) => (
              <div key={exercise.id} className="border-b border-gray-200 pb-4 last:border-0">
                <h3 className="font-medium">{index + 1}. {exercise.name}</h3>
                <p className="text-sm text-gray-600 mt-1">{exercise.description}</p>
                <div className="mt-2 flex flex-wrap gap-2">
                  {exercise.movement_types.length > 0 && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                      {exercise.movement_types.join(', ')}
                    </span>
                  )}
                  {exercise.equipment.length > 0 && (
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      {exercise.equipment.map(e => e.name).join(', ')}
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
      )}
    </div>
  );
} 