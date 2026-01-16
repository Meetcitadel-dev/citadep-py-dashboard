"""
Configuration for Citadel Analytics Demo System
"""
import os
from datetime import datetime, timezone, timedelta

# DEMO_MODE flag - all demo data generation is gated behind this
DEMO_MODE = os.getenv('DEMO_MODE', 'true').lower() == 'true'

# IST timezone offset (+05:30)
IST_OFFSET = timezone(timedelta(hours=5, minutes=30))

# Demo date range: Dec 25, 26, 27 in IST
DEMO_START_DATE = datetime(2024, 12, 25, 0, 0, 0, tzinfo=IST_OFFSET)
DEMO_END_DATE = datetime(2024, 12, 28, 0, 0, 0, tzinfo=IST_OFFSET)  # Exclusive end

# Database path
DB_PATH = os.getenv('DB_PATH', 'citadel_demo.db')

# Fixed distributions
USER_SIGNUP_DISTRIBUTION = {
    '2024-12-25': 56,
    '2024-12-26': 41,
    '2024-12-27': 3
}

GENDER_DISTRIBUTION = {
    'male': 52,
    'female': 48
}

ACADEMIC_YEAR_DISTRIBUTION = {
    'Freshman': 28,
    'Sophomore': 32,
    'Junior': 29,
    'Senior': 9,
    'Graduate': 2
}

DAILY_ACTIVE_USERS = {
    '2024-12-25': 56,
    '2024-12-26': 92,
    '2024-12-27': 94
}

DAILY_SESSIONS = {
    '2024-12-25': 215,
    '2024-12-26': 350,
    '2024-12-27': 358
}

DAILY_VIBES = {
    '2024-12-25': 228,
    '2024-12-26': 410,
    '2024-12-27': 395
}

DAILY_MATCHES = {
    '2024-12-25': 42,
    '2024-12-26': 78,
    '2024-12-27': 71
}

DAILY_MESSAGES = {
    '2024-12-25': 165,
    '2024-12-26': 480,
    '2024-12-27': 612
}

PREMIUM_UPGRADES = {
    '2024-12-25': 4,
    '2024-12-26': 6,
    '2024-12-27': 2
}

# Vibe adjective distribution (positive)
POSITIVE_ADJECTIVES = {
    'Confident': 230,
    'Fun': 210,
    'Smart': 205,
    'Chill': 190,
    'Ambitious': 198
}

# Negative adjectives (smaller counts)
NEGATIVE_ADJECTIVES = {
    'Shy': 50,
    'Quiet': 45,
    'Reserved': 40
}

# Activity peak hours (IST) - weights for distribution
ACTIVITY_PEAKS = [
    (17, 18, 0.35),  # 5-6 PM - primary peak
    (23, 24, 0.25),  # 11-12 PM - secondary peak
    (21, 22, 0.20),  # 9-10 PM - secondary peak
    (12, 13, 0.10),  # 12-1 PM - moderate
    (14, 15, 0.10),  # 2-3 PM - moderate
]

# Premium pricing
PREMIUM_PRICE_MONTHLY = 99  # ₹99
PREMIUM_AVG_LIFETIME_MONTHS = 3

# Conversation depth distribution
CONVERSATION_DEPTH_DISTRIBUTION = {
    (1, 5): 74,
    (6, 15): 61,
    (16, 30): 24,
    (31, 100): 8  # Max 47 messages in deepest
}

# Message request stats
TOTAL_MESSAGE_REQUESTS = 104
MESSAGE_REQUESTS_ACCEPTED = 63
MESSAGE_REQUESTS_DECLINED = 41

# Funnel targets
FUNNEL_TARGETS = {
    'signups': 100,
    'profile_complete': 100,
    'first_vibe_sent': 86,
    'match_created': 54,
    'first_message': 33
}

# Averages
AVG_SESSIONS_PER_USER_PER_DAY = 3.8
AVG_SESSION_DURATION_MINUTES = 3.2
AVG_VIBES_PER_ACTIVE_USER_PER_DAY = 4.1
AVG_VIBE_TO_MATCH_TIME_MINUTES = 88  # 1 hour 28 minutes
AVG_RESPONSE_TIME_MINUTES = 14
VIBE_TO_MATCH_RATE = 0.185  # 18.5%
RESPONSE_RATE = 0.72  # 72%
MESSAGE_REQUEST_ACCEPTANCE_RATE = 0.605  # 60.5%
