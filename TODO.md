# Workout Planner TODO List

## Frontend Development
- [ ] Create a modern, responsive web interface using React/Next.js
- [X] Implement workout request form with duration and intensity options
- [ ] Design workout display view with exercise details and timing
- [ ] Add exercise demonstration videos/images
- [ ] Create user authentication system
- [ ] Add workout history tracking

## Intensity Management
- [X] Add intensity levels (Low, Medium, High)
- [ ] Implement dynamic rest period adjustment based on intensity
  - Low: 60s between exercises, 3min between supersets
  - Medium: 45s between exercises, 2min between supersets
  - High: 30s between exercises, 1.5min between supersets
- [ ] Add option for EMOM (Every Minute On the Minute) style workouts
- [ ] Implement AMRAP (As Many Rounds As Possible) workout type
- [ ] Update workout database to identify which exercises are dynamic and enable filtering

## Exercise Database Expansion
- [ ] Add more compound movements
- [ ] Include bodyweight-only exercises
- [ ] Add kettlebell-specific exercises
- [ ] Include cardio/conditioning exercises
- [ ] Add yoga/stretching exercises
- [ ] Include mobility exercises
- [ ] Add exercise difficulty ratings
- [ ] Add more exercises beyond the sagittal plane

## Progress Tracking
- [ ] Create workout history table
- [ ] Add weight tracking per exercise
- [ ] Track reps/sets completed
- [ ] Add personal records tracking
- [ ] Implement progress visualization
- [ ] Add workout notes/comments
- [ ] Create progress reports

## Advanced Workout Generation
- [X] Add muscle group targeting/exclusion options
- [ ] Implement split workout types (Upper/Lower, Push/Pull, etc.)
- [X] Add equipment availability filter
- [ ] Create workout templates
- [ ] Add progressive overload tracking
- [ ] Implement deload week scheduling
- [ ] Add exercise rotation to prevent plateaus
- [ ] Allow for the user to replace individual exercises post-generation

## Additional Features
- [ ] Add workout sharing functionality
- [ ] Implement workout rating system
- [ ] Add social features (following, sharing)
- [ ] Create workout challenges
- [ ] Add nutrition tracking integration
- [ ] Implement workout reminders/notifications
- [ ] Add export functionality for workout data
- [ ] Create a custom API endpoint that returns a human-readable and filterable list of exercises (e.g., by equipment, muscle group, movement type, etc.) 