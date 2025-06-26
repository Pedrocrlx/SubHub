"""
Demo Data Generator for SubHub (using app models and storage)

This script populates the SubHub application with demo users and subscription data
for testing and demonstration purposes, using the actual app code for consistency.

Usage:
    python3 generate_demo_data.py
"""

import sys
import os
import random
import argparse
from datetime import date, timedelta

# Ensure app modules are importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app.models.user import User
from src.app.models.subscription import Subscription
from src.app.core.security import hash_password
from src.app.db.storage import user_database, save_data_to_file
from src.app.config import app_settings
from src.app.core.logging import application_logger

# Sample data
DEMO_USERS = [
    {"username": "john_doe", "email": "john@example.com", "password": "Password123!"},
    {"username": "jane_smith", "email": "jane@example.com", "password": "Secret456$"},
    {"username": "tech_guru", "email": "guru@techworld.com", "password": "TechPro789&"},
    {"username": "movie_buff", "email": "cinephile@films.com", "password": "FilmLover321*"},
    {"username": "budget_master", "email": "saver@finance.com", "password": "Frugal567^"},
    {"username": "gamer_pro", "email": "gamer@games.net", "password": "GameOn890!"}
]

SUBSCRIPTIONS = {
    "Entertainment": [
        {"name": "Netflix", "price_range": (15.99, 19.99)},
        {"name": "Disney+", "price_range": (7.99, 10.99)},
        {"name": "HBO Max", "price_range": (9.99, 15.99)},
        {"name": "Hulu", "price_range": (6.99, 12.99)},
        {"name": "Amazon Prime Video", "price_range": (8.99, 14.99)}
    ],
    "Music": [
        {"name": "Spotify Premium", "price_range": (9.99, 14.99)},
        {"name": "Apple Music", "price_range": (9.99, 14.99)},
        {"name": "YouTube Music", "price_range": (9.99, 12.99)}
    ],
    "Productivity": [
        {"name": "Microsoft 365", "price_range": (6.99, 9.99)},
        {"name": "Google Workspace", "price_range": (6.00, 12.00)},
        {"name": "Adobe Creative Cloud", "price_range": (19.99, 52.99)}
    ],
    "Gaming": [
        {"name": "Xbox Game Pass", "price_range": (9.99, 14.99)},
        {"name": "PlayStation Plus", "price_range": (9.99, 17.99)},
        {"name": "Nintendo Switch Online", "price_range": (3.99, 7.99)}
    ],
    "Development": [
        {"name": "GitHub Pro", "price_range": (4.00, 7.00)},
        {"name": "JetBrains All Products", "price_range": (24.90, 24.90)},
        {"name": "GitLab", "price_range": (19.00, 99.00)}
    ]
}

def generate_random_date(start_date=None, max_days_back=365):
    """Generate a random date within the past year."""
    if not start_date:
        start_date = date.today()
    days_back = random.randint(0, max_days_back)
    return (start_date - timedelta(days=days_back)).isoformat()

def get_random_subscriptions(min_count=3, max_count=8):
    """Generate a random list of Subscription objects."""
    subscription_count = random.randint(min_count, max_count)
    selected_services = set()
    subscriptions = []
    while len(subscriptions) < subscription_count:
        category = random.choice(list(SUBSCRIPTIONS.keys()))
        services = SUBSCRIPTIONS[category]
        service = random.choice(services)
        service_name = service["name"]
        if service_name in selected_services:
            continue
        selected_services.add(service_name)
        min_price, max_price = service["price_range"]
        price = round(random.uniform(min_price, max_price), 2)
        start_date = generate_random_date()
        subscriptions.append(Subscription(
            service_name=service_name,
            monthly_price=price,
            category=category,
            starting_date=start_date
        ))
    return subscriptions

def create_demo_users(clear_existing=False):
    """Create demo users with random subscriptions using app models and storage."""
    if clear_existing:
        user_database.clear()
        application_logger.info("Cleared existing user database before generating demo data.")
    for user_info in DEMO_USERS:
        email = user_info["email"]
        if not clear_existing and email in user_database:
            application_logger.info(f"User [{email}] already exists, skipping...")
            continue
        subscriptions = get_random_subscriptions()
        user_database[email] = User(
            username=user_info["username"],
            passhash=hash_password(user_info["password"]),
            email=email,
            subscriptions=subscriptions
        )
        application_logger.info(
            f"Registered user: [{email}] (username: [{user_info['username']}])"
        )
        for sub in subscriptions:
            application_logger.info(
                f"Added subscription for [{email}]: "
                f"[{sub.service_name}] | ${sub.monthly_price:.2f}/month | "
                f"Category: [{sub.category}] | Start: [{sub.starting_date}]"
            )
    save_data_to_file()
    application_logger.info(f"Demo data generation complete. Created/updated [{len(DEMO_USERS)}] users.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate demo data for SubHub')
    parser.add_argument('--clear', action='store_true', help='Clear existing data before creating demo data')
    args = parser.parse_args()
    try:
        create_demo_users(clear_existing=args.clear)
        print(f"Successfully created {len(DEMO_USERS)} demo users with subscriptions!")
        print("Login credentials:")
        for user in DEMO_USERS:
            print(f"  Email: {user['email']}, Password: {user['password']}")
    except Exception as e:
        application_logger.error(f"Error generating demo data: {e}")
        print(f"Error generating demo data: {e}")
        sys.exit(1)