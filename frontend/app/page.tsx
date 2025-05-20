'use client';

import { useState } from 'react';

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

  const generateWorkout = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_URL}/workouts/generate?duration_minutes=${duration}`);
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
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-lg font-semibold mb-4">Generate Workout</h2>
        <div className="space-y-4">
          <div>
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
              Workout Duration (minutes)
            </label>
            <input
              type="number"
              id="duration"
              min="10"
              max="60"
              value={duration}
              onChange={(e) => setDuration(Number(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
            />
          </div>
          <button
            onClick={generateWorkout}
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50"
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