#!/usr/bin/env python3
"""Quick script to load seed data"""
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
from pymongo import MongoClient

# Load .env from backend directory
load_dotenv('.env')

MONGO_URI = os.environ.get('MONGO_URI')
DB_NAME = os.environ.get('DB_NAME', 'foodapp')

if not MONGO_URI:
    print("ERROR: MONGO_URI not found in .env file!")
    sys.exit(1)

print(f'Connecting to MongoDB at {MONGO_URI}...')
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Load restaurants
print('Loading restaurants...')
with open('seed_data/restaurants.json', 'r') as f:
    restaurants = json.load(f)

db['restaurants'].delete_many({})
result = db['restaurants'].insert_many(restaurants)
print(f'✅ Loaded {len(result.inserted_ids)} restaurants')

# Load dishes
print('Loading dishes...')
with open('seed_data/dishes_refined.json', 'r') as f:
    dishes = json.load(f)

db['dishes'].delete_many({})
result = db['dishes'].insert_many(dishes)
print(f'✅ Loaded {len(result.inserted_ids)} dishes')

# Verify
restaurant_count = db['restaurants'].count_documents({})
dish_count = db['dishes'].count_documents({})

print('\n' + '='*60)
print('Database Status:')
print(f'  Restaurants: {restaurant_count}')
print(f'  Dishes: {dish_count}')
print('='*60)
print('\n✅ Seed data loaded successfully!')
print('\nNow run the compatibility test:')
print('  python test_compatibility_scoring.py')
