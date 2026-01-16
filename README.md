# Citadel Analytics Demo System

A fully deterministic demo analytics data and simulation layer for the Citadel college social networking app. All data is synthetic (fake) and generated in code, with every metric mathematically correct, internally consistent, and derived from raw event rows.

## Features

- **Fully Deterministic**: All data generation is reproducible with fixed seed
- **Event-Driven**: All metrics derived from raw event data, never hard-coded
- **Mathematically Correct**: All distributions and totals match specified targets
- **Internally Consistent**: Deleting a single event changes downstream metrics
- **Demo Mode Gated**: All functionality requires `DEMO_MODE=true`

## System Requirements

- Python 3.8+
- SQLite3 (included with Python)

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set DEMO_MODE environment variable:
```bash
export DEMO_MODE=true
```

Or set it in your shell profile for persistence.

## Quick Start

### 1. Initialize Demo Data

Generate all synthetic data:

```bash
python main.py init
```

This creates a SQLite database (`citadel_demo.db`) with all synthetic events.

### 2. View Analytics

View all metrics in table format:

```bash
python main.py analytics
```

Or get JSON output:

```bash
python main.py analytics --format json
```

### 3. Verify Metrics

Verify that all metrics match expected targets:

```bash
python main.py verify
```

### 4. Start API Server

Start the REST API server for dashboard consumption:

```bash
python api.py
```

The API will be available at `http://localhost:5000`

## API Endpoints

All endpoints require `DEMO_MODE=true`:

- `GET /api/health` - Health check
- `GET /api/metrics` - Get all metrics
- `GET /api/metrics/users` - User metrics
- `GET /api/metrics/sessions` - Session metrics
- `GET /api/metrics/vibes` - Vibe metrics
- `GET /api/metrics/matches` - Match metrics
- `GET /api/metrics/messages` - Message metrics
- `GET /api/metrics/conversations` - Conversation metrics
- `GET /api/metrics/revenue` - Revenue metrics
- `GET /api/metrics/funnel` - Funnel metrics
- `GET /api/metrics/activity` - Activity heatmap data
- `GET /api/metrics/demographics` - Demographic distributions
- `GET /api/events?type=<type>&limit=<n>` - Raw event data

## Data Specifications

### Time Window
- **Dates**: December 25, 26, 27, 2024 (IST)
- **Timezone**: IST (UTC+5:30)
- **Format**: ISO-8601 timestamps

### User Base
- **Total Users**: 100
- **Signup Distribution**:
  - Dec 25: 56 users
  - Dec 26: 41 users
  - Dec 27: 3 users
- **Gender**: 52 male, 48 female
- **Profile Complete**: 100% (all users)

### Sessions & Activity
- **Daily Active Users**: 56 (Dec 25), 92 (Dec 26), 94 (Dec 27)
- **Total Sessions**: 215 (Dec 25), 350 (Dec 26), 358 (Dec 27)
- **Avg Sessions/User/Day**: 3.8
- **Avg Session Duration**: 3.2 minutes
- **Activity Peaks**: 5-6 PM (primary), 11-12 PM & 9-10 PM (secondary)

### Vibes (Likes)
- **Total Vibes**: 1,033
  - Dec 25: 228
  - Dec 26: 410
  - Dec 27: 395
- **Avg Vibes/Active User/Day**: ~4.1
- **Adjective Distribution**:
  - Confident: 230
  - Fun: 210
  - Smart: 205
  - Chill: 190
  - Ambitious: 198
- **Expiration**: 24 hours

### Matches
- **Total Matches**: 191
  - Dec 25: 42
  - Dec 26: 78
  - Dec 27: 71
- **Match Rate**: ~18.5%
- **Avg Time to Match**: ~1 hour 28 minutes
- **Expiration**: 24 hours

### Messaging
- **Total Conversations**: 167
- **Total Messages**: 1,257
  - Dec 25: 165
  - Dec 26: 480
  - Dec 27: 612
- **Response Rate**: 72%
- **Avg Response Time**: ~14 minutes
- **Conversation Depth**:
  - 1-5 messages: 74 conversations
  - 6-15 messages: 61 conversations
  - 16-30 messages: 24 conversations
  - 31+ messages: 8 conversations (max 47)

### Message Requests
- **Total Requests**: 104
- **Accepted**: 63 (60.5%)
- **Declined**: 41
- **Pending**: 0

### Premium & Revenue
- **Premium Users**: 12 total
  - Dec 25: 4 upgrades
  - Dec 26: 6 upgrades
  - Dec 27: 2 upgrades
- **Price**: ₹99/month
- **MRR**: ₹1,188
- **Avg LTV**: ₹297 (3 months)

### User Journey Funnel
- Signups: 100
- Profile Complete: 100 (100%)
- First Vibe Sent: 86 (86%)
- Match Created: 54 (54%)
- First Message: 33 (33%)

## Database Schema

The system uses SQLite with the following tables:

- `users` - User accounts and profiles
- `sessions` - App sessions with timestamps
- `vibes` - Vibe events (likes)
- `matches` - Match events from mutual vibes
- `conversations` - Conversation threads
- `messages` - Individual messages
- `message_requests` - Message request events
- `premium_subscriptions` - Premium subscription records
- `user_events` - First-action tracking for funnel

## Architecture

```
config.py          - Configuration and constants
database.py        - Database schema and connection
data_generator.py  - Deterministic data generation
analytics.py       - Metric computation from events
main.py            - CLI interface
api.py             - REST API server
```

## Key Principles

1. **Deterministic**: Fixed random seed ensures reproducibility
2. **Event-Driven**: All metrics computed from raw events
3. **Consistent**: Single event deletion changes downstream metrics
4. **Gated**: All operations require `DEMO_MODE=true`
5. **Realistic**: Timestamps follow realistic activity patterns

## Customization

To modify the demo data:

1. Edit `config.py` to change distributions and targets
2. Run `python main.py init` to regenerate data
3. Run `python main.py verify` to check metrics

## Troubleshooting

**Issue**: "DEMO_MODE not enabled"
- **Solution**: Set `export DEMO_MODE=true`

**Issue**: Metrics don't match targets
- **Solution**: Run `python main.py verify` to see discrepancies
- Regenerate data with `python main.py init`

**Issue**: Database locked
- **Solution**: Ensure all database connections are closed
- Delete `citadel_demo.db` and regenerate

## License

Internal use only - Citadel Analytics Demo System
