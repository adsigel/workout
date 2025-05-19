# Workout Planner

A smart workout planning application that generates personalized workouts based on duration, intensity, and available equipment. The application uses a database of exercises with detailed attributes to create balanced and effective workout routines.

## Features

- Dynamic workout generation based on duration
- Exercise database with movement types and muscle groups
- Support for multiple equipment types
- Balanced exercise selection across movement patterns
- Customizable workout parameters

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the FastAPI server:
```bash
uvicorn app.main:app --reload
```

4. Seed the database with initial exercises:
```bash
python -m app.seed_exercises
```

## API Endpoints

- `GET /workouts/generate?duration_minutes={minutes}`: Generate a workout for the specified duration
- `GET /exercises`: List all available exercises
- `POST /exercises`: Add a new exercise to the database

## Development

See [TODO.md](TODO.md) for planned features and improvements.

## License

MIT 