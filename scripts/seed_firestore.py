from google.cloud import firestore

PROJECT_ID = "qwiklabs-gcp-01-57b0d8b0ef08"
db = firestore.Client(project=PROJECT_ID)

INITIAL_WORKOUTS = [
    {
        "workout_id": "w1",
        "title": "Zone 2 Base Endurance Ride",
        "type": "cycling",
        "duration_minutes": 90,
        "target_zone": "Zone 2 (55-75% FTP)",
        "intensity": "Moderate",
        "description": "Steady endurance ride focusing on smooth cadence (85-95 rpm) and aerobic efficiency.",
        "tss_estimate": 70,
    },
    {
        "workout_id": "w2",
        "title": "Aerobic Threshold Swim Sets",
        "type": "swimming",
        "duration_minutes": 45,
        "target_zone": "Zone 3 / Threshold",
        "intensity": "High",
        "description": "Warmup 400m, 10x100m at threshold pace on 1:45 rest interval, 200m cooldown.",
        "tss_estimate": 50,
    },
    {
        "workout_id": "w3",
        "title": "Brick Workout - Tempo Run",
        "type": "running",
        "duration_minutes": 60,
        "target_zone": "Zone 3-4",
        "intensity": "Challenging",
        "description": "20min easy warmup, 30min tempo run at race pace (7:30/mi target), 10min cooldown.",
        "tss_estimate": 65,
    },
    {
        "workout_id": "w4",
        "title": "FTP Power Intervals",
        "type": "cycling",
        "duration_minutes": 60,
        "target_zone": "Zone 4 (95-105% FTP)",
        "intensity": "High",
        "description": "15min warmup, 5x4min at 100% FTP with 3min recovery, 15min cooldown.",
        "tss_estimate": 75,
    },
]


def seed_database():
    collection_ref = db.collection("workouts")
    for workout in INITIAL_WORKOUTS:
        doc_ref = collection_ref.document(workout["workout_id"])
        doc_ref.set(workout)
        print(f"Seeded workout: {workout['title']} ({workout['workout_id']})")


if __name__ == "__main__":
    seed_database()
