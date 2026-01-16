"""
Main entry point for Citadel Analytics Demo System
"""
import json
import argparse
from database import Database
from data_generator import DataGenerator
from analytics import Analytics
from config import DEMO_MODE

def initialize_demo_data(db_path: str = None):
    """Initialize demo database with all synthetic data"""
    if not DEMO_MODE:
        print("Error: DEMO_MODE must be enabled")
        return
    
    db = Database(db_path) if db_path else Database()
    
    try:
        print("Creating database schema...")
        db.create_schema()
        
        print("Clearing existing data...")
        db.clear_all_data()
        
        print("Generating demo data...")
        generator = DataGenerator(db)
        generator.generate_all()
        
        print("\nDemo data generation complete!")
        print(f"Database saved to: {db.db_path}")
        
    finally:
        db.close()

def get_analytics(db_path: str = None, format: str = 'json'):
    """Get all analytics metrics"""
    if not DEMO_MODE:
        print("Error: DEMO_MODE must be enabled")
        return
    
    db = Database(db_path) if db_path else Database()
    
    try:
        analytics = Analytics(db)
        metrics = analytics.get_all_metrics()
        
        # Add message request metrics
        metrics['message_requests'] = analytics.get_message_request_metrics()
        
        if format == 'json':
            print(json.dumps(metrics, indent=2, default=str))
        else:
            print_metrics_table(metrics)
        
    finally:
        db.close()

def print_metrics_table(metrics: dict):
    """Print metrics in a readable table format"""
    print("\n" + "="*60)
    print("CITADEL ANALYTICS - DEMO METRICS")
    print("="*60)
    
    print("\n📊 USER METRICS")
    print(f"  Total Users: {metrics['users']['total_users']}")
    print(f"  Profile Complete: {metrics['users']['profile_complete']} ({metrics['users']['profile_completion_rate']:.1f}%)")
    print(f"  Premium Users: {metrics['users']['premium_users']}")
    
    print("\n📈 SESSION METRICS")
    print(f"  Total Sessions: {metrics['sessions']['total_sessions']}")
    print(f"  Avg Session Duration: {metrics['sessions']['avg_session_duration_minutes']:.2f} minutes")
    print(f"  DAU by Date: {metrics['sessions']['dau_by_date']}")
    
    print("\n❤️ VIBE METRICS")
    print(f"  Total Vibes Sent: {metrics['vibes']['total_vibes_sent']}")
    print(f"  Total Vibes Received: {metrics['vibes']['total_vibes_received']}")
    print(f"  Vibe-to-Match Rate: {metrics['matches']['vibe_to_match_rate']:.2f}%")
    
    print("\n💑 MATCH METRICS")
    print(f"  Total Matches: {metrics['matches']['total_matches']}")
    print(f"  Avg Time to Match: {metrics['matches']['avg_time_to_match_minutes']:.2f} minutes")
    
    print("\n💬 MESSAGE METRICS")
    print(f"  Total Messages: {metrics['messages']['total_messages']}")
    print(f"  Response Rate: {metrics['messages']['response_rate']:.2f}%")
    print(f"  Avg Response Time: {metrics['messages']['avg_response_time_minutes']:.2f} minutes")
    
    print("\n📧 CONVERSATION METRICS")
    print(f"  Total Conversations: {metrics['conversations']['total_conversations']}")
    print(f"  Max Depth: {metrics['conversations']['max_conversation_depth']} messages")
    print(f"  Active Conversations (Dec 27): {metrics['conversations']['active_conversations_dec27']}")
    
    print("\n💰 REVENUE METRICS")
    print(f"  MRR: ₹{metrics['revenue']['mrr']}")
    print(f"  Avg LTV: ₹{metrics['revenue']['avg_ltv']:.2f}")
    print(f"  Total Revenue: ₹{metrics['revenue']['total_revenue']}")
    
    print("\n🎯 FUNNEL METRICS")
    funnel = metrics['funnel']
    print(f"  Signups: {funnel['signups']}")
    print(f"  Profile Complete: {funnel['profile_complete']} ({funnel['conversion_rates']['signup_to_profile']:.1f}%)")
    print(f"  First Vibe Sent: {funnel['first_vibe_sent']} ({funnel['conversion_rates']['signup_to_vibe']:.1f}%)")
    print(f"  Match Created: {funnel['match_created']} ({funnel['conversion_rates']['signup_to_match']:.1f}%)")
    print(f"  First Message: {funnel['first_message']} ({funnel['conversion_rates']['signup_to_message']:.1f}%)")
    
    print("\n" + "="*60)

def verify_metrics(db_path: str = None):
    """Verify that all metrics match expected targets"""
    if not DEMO_MODE:
        print("Error: DEMO_MODE must be enabled")
        return
    
    from config import (
        DAILY_ACTIVE_USERS, DAILY_SESSIONS, DAILY_VIBES, DAILY_MATCHES,
        DAILY_MESSAGES, FUNNEL_TARGETS, TOTAL_MESSAGE_REQUESTS,
        MESSAGE_REQUESTS_ACCEPTED, MESSAGE_REQUESTS_DECLINED
    )
    
    db = Database(db_path) if db_path else Database()
    
    try:
        analytics = Analytics(db)
        metrics = analytics.get_all_metrics()
        metrics['message_requests'] = analytics.get_message_request_metrics()
        
        print("\n" + "="*60)
        print("METRIC VERIFICATION")
        print("="*60)
        
        errors = []
        warnings = []
        
        # Verify DAU
        dau = metrics['sessions']['dau_by_date']
        for date, expected in DAILY_ACTIVE_USERS.items():
            actual = dau.get(date, 0)
            if actual != expected:
                errors.append(f"DAU mismatch on {date}: expected {expected}, got {actual}")
        
        # Verify sessions
        sessions = metrics['sessions']['sessions_by_date']
        for date, expected in DAILY_SESSIONS.items():
            actual = sessions.get(date, 0)
            if actual != expected:
                errors.append(f"Sessions mismatch on {date}: expected {expected}, got {actual}")
        
        # Verify vibes
        vibes = metrics['vibes']['vibes_by_date']
        for date, expected in DAILY_VIBES.items():
            actual = vibes.get(date, 0)
            if abs(actual - expected) > 2:  # Allow small variance
                warnings.append(f"Vibes variance on {date}: expected {expected}, got {actual}")
        
        # Verify matches
        matches = metrics['matches']['matches_by_date']
        for date, expected in DAILY_MATCHES.items():
            actual = matches.get(date, 0)
            if abs(actual - expected) > 2:
                warnings.append(f"Matches variance on {date}: expected {expected}, got {actual}")
        
        # Verify messages
        messages = metrics['messages']['messages_by_date']
        total_messages = sum(messages.values())
        expected_total = sum(DAILY_MESSAGES.values())
        if abs(total_messages - expected_total) > 10:
            warnings.append(f"Messages variance: expected {expected_total}, got {total_messages}")
        
        # Verify funnel
        funnel = metrics['funnel']
        for key, expected in FUNNEL_TARGETS.items():
            actual = funnel.get(key, 0)
            if actual != expected:
                errors.append(f"Funnel {key}: expected {expected}, got {actual}")
        
        # Verify message requests
        mr = metrics['message_requests']
        if mr['total_requests'] != TOTAL_MESSAGE_REQUESTS:
            errors.append(f"Message requests: expected {TOTAL_MESSAGE_REQUESTS}, got {mr['total_requests']}")
        if mr['accepted'] != MESSAGE_REQUESTS_ACCEPTED:
            errors.append(f"Accepted requests: expected {MESSAGE_REQUESTS_ACCEPTED}, got {mr['accepted']}")
        if mr['declined'] != MESSAGE_REQUESTS_DECLINED:
            errors.append(f"Declined requests: expected {MESSAGE_REQUESTS_DECLINED}, got {mr['declined']}")
        
        if errors:
            print("\n❌ ERRORS FOUND:")
            for error in errors:
                print(f"  - {error}")
        
        if warnings:
            print("\n⚠️  WARNINGS:")
            for warning in warnings:
                print(f"  - {warning}")
        
        if not errors and not warnings:
            print("\n✅ All metrics verified successfully!")
        
        print("="*60 + "\n")
        
    finally:
        db.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Citadel Analytics Demo System')
    parser.add_argument('command', choices=['init', 'analytics', 'verify'], 
                       help='Command to execute')
    parser.add_argument('--db-path', type=str, help='Path to database file')
    parser.add_argument('--format', choices=['json', 'table'], default='table',
                       help='Output format for analytics')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        initialize_demo_data(args.db_path)
    elif args.command == 'analytics':
        get_analytics(args.db_path, args.format)
    elif args.command == 'verify':
        verify_metrics(args.db_path)
