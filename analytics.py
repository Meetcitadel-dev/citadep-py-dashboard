"""
Analytics queries that derive all metrics from raw event data
All metrics are computed dynamically, never hard-coded
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from database import Database
from config import DEMO_START_DATE, DEMO_END_DATE, IST_OFFSET, FUNNEL_TARGETS

class Analytics:
    def __init__(self, db: Database):
        self.db = db
    
    def get_all_metrics(self) -> Dict:
        """Get all dashboard metrics"""
        return {
            'users': self.get_user_metrics(),
            'sessions': self.get_session_metrics(),
            'vibes': self.get_vibe_metrics(),
            'matches': self.get_match_metrics(),
            'messages': self.get_message_metrics(),
            'conversations': self.get_conversation_metrics(),
            'revenue': self.get_revenue_metrics(),
            'funnel': self.get_funnel_metrics(),
            'activity': self.get_activity_metrics(),
            'demographics': self.get_demographics()
        }
    
    def get_user_metrics(self) -> Dict:
        """Get user-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()['count']
        
        # Users by signup date
        cursor.execute("""
            SELECT DATE(signup_timestamp) as date, COUNT(*) as count
            FROM users
            GROUP BY DATE(signup_timestamp)
            ORDER BY date
        """)
        signups_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Profile completion (all should be 100%)
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE profile_image_uploaded = 1")
        profile_complete = cursor.fetchone()['count']
        
        # Premium users
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_premium = 1")
        premium_users = cursor.fetchone()['count']
        
        return {
            'total_users': total_users,
            'signups_by_date': signups_by_date,
            'profile_complete': profile_complete,
            'profile_completion_rate': (profile_complete / total_users * 100) if total_users > 0 else 0,
            'premium_users': premium_users,
            'free_users': total_users - premium_users
        }
    
    def get_session_metrics(self) -> Dict:
        """Get session-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Daily Active Users
        cursor.execute("""
            SELECT DATE(start_timestamp) as date, COUNT(DISTINCT user_id) as dau
            FROM sessions
            GROUP BY DATE(start_timestamp)
            ORDER BY date
        """)
        dau_by_date = {row['date']: row['dau'] for row in cursor.fetchall()}
        
        # Total sessions by date
        cursor.execute("""
            SELECT DATE(start_timestamp) as date, COUNT(*) as count
            FROM sessions
            GROUP BY DATE(start_timestamp)
            ORDER BY date
        """)
        sessions_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Average sessions per user per day
        cursor.execute("""
            SELECT 
                DATE(start_timestamp) as date,
                COUNT(*) * 1.0 / COUNT(DISTINCT user_id) as avg_sessions
            FROM sessions
            GROUP BY DATE(start_timestamp)
            ORDER BY date
        """)
        avg_sessions_by_date = {row['date']: row['avg_sessions'] for row in cursor.fetchall()}
        
        # Average session duration
        cursor.execute("""
            SELECT AVG(duration_seconds) / 60.0 as avg_duration_minutes
            FROM sessions
            WHERE duration_seconds IS NOT NULL
        """)
        avg_duration = cursor.fetchone()['avg_duration_minutes'] or 0
        
        # Total time per user per day
        cursor.execute("""
            SELECT 
                DATE(start_timestamp) as date,
                user_id,
                SUM(duration_seconds) / 60.0 as total_minutes
            FROM sessions
            WHERE duration_seconds IS NOT NULL
            GROUP BY DATE(start_timestamp), user_id
        """)
        user_time_by_date = {}
        for row in cursor.fetchall():
            date = row['date']
            if date not in user_time_by_date:
                user_time_by_date[date] = []
            user_time_by_date[date].append(row['total_minutes'])
        
        avg_time_per_user_by_date = {
            date: sum(times) / len(times) if times else 0
            for date, times in user_time_by_date.items()
        }
        
        return {
            'dau_by_date': dau_by_date,
            'sessions_by_date': sessions_by_date,
            'total_sessions': sum(sessions_by_date.values()),
            'avg_sessions_per_user_per_day': avg_sessions_by_date,
            'avg_session_duration_minutes': avg_duration,
            'avg_time_per_user_per_day_minutes': avg_time_per_user_by_date
        }
    
    def get_vibe_metrics(self) -> Dict:
        """Get vibe-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Vibes by date
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM vibes
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        vibes_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Total vibes sent and received (should be equal)
        cursor.execute("SELECT COUNT(*) as count FROM vibes")
        total_vibes_sent = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM vibes")
        total_vibes_received = cursor.fetchone()['count']
        
        # Vibes by adjective
        cursor.execute("""
            SELECT adjective, COUNT(*) as count
            FROM vibes
            GROUP BY adjective
            ORDER BY count DESC
        """)
        vibes_by_adjective = {row['adjective']: row['count'] for row in cursor.fetchall()}
        
        # Vibes per active user per day
        cursor.execute("""
            SELECT 
                DATE(v.timestamp) as date,
                COUNT(*) * 1.0 / COUNT(DISTINCT v.sender_id) as avg_vibes
            FROM vibes v
            GROUP BY DATE(v.timestamp)
            ORDER BY date
        """)
        avg_vibes_by_date = {row['date']: row['avg_vibes'] for row in cursor.fetchall()}
        
        # Premium vs free vibe sending
        cursor.execute("""
            SELECT 
                u.is_premium,
                COUNT(*) as count
            FROM vibes v
            JOIN users u ON v.sender_id = u.user_id
            GROUP BY u.is_premium
        """)
        vibes_by_premium_status = {}
        for row in cursor.fetchall():
            status = 'premium' if row['is_premium'] else 'free'
            vibes_by_premium_status[status] = row['count']
        
        return {
            'vibes_by_date': vibes_by_date,
            'total_vibes_sent': total_vibes_sent,
            'total_vibes_received': total_vibes_received,
            'vibes_by_adjective': vibes_by_adjective,
            'avg_vibes_per_active_user_per_day': avg_vibes_by_date,
            'vibes_by_premium_status': vibes_by_premium_status
        }
    
    def get_match_metrics(self) -> Dict:
        """Get match-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Matches by date
        cursor.execute("""
            SELECT DATE(created_timestamp) as date, COUNT(*) as count
            FROM matches
            GROUP BY DATE(created_timestamp)
            ORDER BY date
        """)
        matches_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Total matches
        cursor.execute("SELECT COUNT(*) as count FROM matches")
        total_matches = cursor.fetchone()['count']
        
        # Vibe-to-match rate
        cursor.execute("SELECT COUNT(*) as count FROM vibes")
        total_vibes = cursor.fetchone()['count']
        vibe_to_match_rate = (total_matches * 2 / total_vibes * 100) if total_vibes > 0 else 0
        
        # Average time from vibe to match
        cursor.execute("""
            SELECT 
                AVG((julianday(m.created_timestamp) - julianday(v1.timestamp)) * 24 * 60) as avg_minutes
            FROM matches m
            JOIN vibes v1 ON m.vibe1_id = v1.vibe_id
            WHERE v1.timestamp < m.created_timestamp
        """)
        avg_match_time = cursor.fetchone()['avg_minutes'] or 0
        
        return {
            'matches_by_date': matches_by_date,
            'total_matches': total_matches,
            'vibe_to_match_rate': vibe_to_match_rate,
            'avg_time_to_match_minutes': avg_match_time
        }
    
    def get_message_metrics(self) -> Dict:
        """Get message-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Messages by date
        cursor.execute("""
            SELECT DATE(timestamp) as date, COUNT(*) as count
            FROM messages
            GROUP BY DATE(timestamp)
            ORDER BY date
        """)
        messages_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Total messages
        cursor.execute("SELECT COUNT(*) as count FROM messages")
        total_messages = cursor.fetchone()['count']
        
        # Response rate (messages with parent_message_id / total messages excluding first)
        cursor.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE parent_message_id IS NOT NULL) * 1.0 / 
                NULLIF(COUNT(*) FILTER (WHERE parent_message_id IS NULL), 0) as response_rate
            FROM messages
        """)
        # SQLite doesn't support FILTER, so use alternative
        cursor.execute("""
            SELECT 
                (SELECT COUNT(*) FROM messages WHERE parent_message_id IS NOT NULL) * 1.0 /
                NULLIF((SELECT COUNT(*) FROM messages WHERE parent_message_id IS NULL), 0) as response_rate
        """)
        response_rate_result = cursor.fetchone()
        response_rate = response_rate_result['response_rate'] if response_rate_result['response_rate'] else 0
        
        # Average response time
        cursor.execute("""
            SELECT 
                AVG((julianday(m2.timestamp) - julianday(m1.timestamp)) * 24 * 60) as avg_minutes
            FROM messages m1
            JOIN messages m2 ON m2.parent_message_id = m1.message_id
            WHERE m2.timestamp > m1.timestamp
        """)
        avg_response_time = cursor.fetchone()['avg_minutes'] or 0
        
        return {
            'messages_by_date': messages_by_date,
            'total_messages': total_messages,
            'response_rate': response_rate * 100,  # Convert to percentage
            'avg_response_time_minutes': avg_response_time
        }
    
    def get_conversation_metrics(self) -> Dict:
        """Get conversation-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Total conversations
        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        total_conversations = cursor.fetchone()['count']
        
        # Conversations by depth
        cursor.execute("""
            SELECT 
                c.conversation_id,
                COUNT(m.message_id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.conversation_id = m.conversation_id
            GROUP BY c.conversation_id
        """)
        conversation_depths = [row['message_count'] for row in cursor.fetchall()]
        
        depth_distribution = {
            '1-5': sum(1 for d in conversation_depths if 1 <= d <= 5),
            '6-15': sum(1 for d in conversation_depths if 6 <= d <= 15),
            '16-30': sum(1 for d in conversation_depths if 16 <= d <= 30),
            '31+': sum(1 for d in conversation_depths if d >= 31)
        }
        
        # Deepest conversation
        max_depth = max(conversation_depths) if conversation_depths else 0
        
        # Active conversations on Dec 27 (last 24 hours)
        cursor.execute("""
            SELECT COUNT(DISTINCT conversation_id) as count
            FROM messages
            WHERE DATE(timestamp) = '2024-12-27'
            AND timestamp >= datetime('2024-12-27 00:00:00', '-24 hours')
        """)
        active_conversations_dec27 = cursor.fetchone()['count']
        
        return {
            'total_conversations': total_conversations,
            'depth_distribution': depth_distribution,
            'max_conversation_depth': max_depth,
            'active_conversations_dec27': active_conversations_dec27
        }
    
    def get_revenue_metrics(self) -> Dict:
        """Get revenue-related metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Monthly Recurring Revenue (MRR)
        cursor.execute("""
            SELECT COUNT(*) * 99 as mrr
            FROM users
            WHERE is_premium = 1
        """)
        mrr = cursor.fetchone()['mrr']
        
        # Premium upgrades by date
        cursor.execute("""
            SELECT DATE(premium_upgrade_timestamp) as date, COUNT(*) as count
            FROM users
            WHERE is_premium = 1 AND premium_upgrade_timestamp IS NOT NULL
            GROUP BY DATE(premium_upgrade_timestamp)
            ORDER BY date
        """)
        upgrades_by_date = {row['date']: row['count'] for row in cursor.fetchall()}
        
        # Lifetime Value (LTV)
        cursor.execute("""
            SELECT AVG(amount_paid) as avg_ltv
            FROM premium_subscriptions
        """)
        avg_ltv = cursor.fetchone()['avg_ltv'] or 0
        
        # Total revenue
        cursor.execute("SELECT SUM(amount_paid) as total FROM premium_subscriptions")
        total_revenue = cursor.fetchone()['total'] or 0
        
        return {
            'mrr': mrr,
            'upgrades_by_date': upgrades_by_date,
            'avg_ltv': avg_ltv,
            'total_revenue': total_revenue
        }
    
    def get_funnel_metrics(self) -> Dict:
        """Get funnel conversion metrics"""
        cursor = self.db.get_connection().cursor()
        
        # Signups
        cursor.execute("SELECT COUNT(*) as count FROM users")
        signups = cursor.fetchone()['count']
        
        # Profile complete
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE profile_image_uploaded = 1")
        profile_complete = cursor.fetchone()['count']
        
        # First vibe sent
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM user_events WHERE event_type = 'first_vibe_sent'")
        first_vibe_sent = cursor.fetchone()['count']
        
        # Match created
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM user_events WHERE event_type = 'match_created'")
        match_created = cursor.fetchone()['count']
        
        # First message
        cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM user_events WHERE event_type = 'first_message'")
        first_message = cursor.fetchone()['count']
        
        return {
            'signups': signups,
            'profile_complete': profile_complete,
            'first_vibe_sent': first_vibe_sent,
            'match_created': match_created,
            'first_message': first_message,
            'conversion_rates': {
                'signup_to_profile': (profile_complete / signups * 100) if signups > 0 else 0,
                'signup_to_vibe': (first_vibe_sent / signups * 100) if signups > 0 else 0,
                'signup_to_match': (match_created / signups * 100) if signups > 0 else 0,
                'signup_to_message': (first_message / signups * 100) if signups > 0 else 0,
                'vibe_to_match': (match_created / first_vibe_sent * 100) if first_vibe_sent > 0 else 0,
                'match_to_message': (first_message / match_created * 100) if match_created > 0 else 0
            }
        }
    
    def get_activity_metrics(self) -> Dict:
        """Get activity heatmap data"""
        cursor = self.db.get_connection().cursor()
        
        # Activity by hour across all days
        cursor.execute("""
            SELECT 
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM (
                SELECT start_timestamp as timestamp FROM sessions
                UNION ALL
                SELECT timestamp FROM vibes
                UNION ALL
                SELECT timestamp FROM messages
            )
            GROUP BY hour
            ORDER BY hour
        """)
        activity_by_hour = {int(row['hour']): row['count'] for row in cursor.fetchall()}
        
        # Activity by date and hour
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                strftime('%H', timestamp) as hour,
                COUNT(*) as count
            FROM (
                SELECT start_timestamp as timestamp FROM sessions
                UNION ALL
                SELECT timestamp FROM vibes
                UNION ALL
                SELECT timestamp FROM messages
            )
            GROUP BY date, hour
            ORDER BY date, hour
        """)
        activity_heatmap = {}
        for row in cursor.fetchall():
            date = row['date']
            hour = int(row['hour'])
            if date not in activity_heatmap:
                activity_heatmap[date] = {}
            activity_heatmap[date][hour] = row['count']
        
        return {
            'activity_by_hour': activity_by_hour,
            'activity_heatmap': activity_heatmap
        }
    
    def get_demographics(self) -> Dict:
        """Get demographic distributions"""
        cursor = self.db.get_connection().cursor()
        
        # Gender distribution
        cursor.execute("""
            SELECT gender, COUNT(*) as count
            FROM users
            GROUP BY gender
        """)
        gender_dist = {row['gender']: row['count'] for row in cursor.fetchall()}
        
        # Academic year distribution
        cursor.execute("""
            SELECT academic_year, COUNT(*) as count
            FROM users
            GROUP BY academic_year
            ORDER BY academic_year
        """)
        academic_dist = {row['academic_year']: row['count'] for row in cursor.fetchall()}
        
        return {
            'gender': gender_dist,
            'academic_year': academic_dist
        }
    
    def get_message_request_metrics(self) -> Dict:
        """Get message request metrics"""
        cursor = self.db.get_connection().cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM message_requests")
        total_requests = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM message_requests WHERE status = 'accepted'")
        accepted = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM message_requests WHERE status = 'declined'")
        declined = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM message_requests WHERE status = 'pending'")
        pending = cursor.fetchone()['count']
        
        acceptance_rate = (accepted / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': total_requests,
            'accepted': accepted,
            'declined': declined,
            'pending': pending,
            'acceptance_rate': acceptance_rate
        }
