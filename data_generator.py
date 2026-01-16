"""
Deterministic data generator for Citadel Analytics Demo System
All data generation is deterministic and reproducible
"""
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from config import (
    DEMO_START_DATE, DEMO_END_DATE, IST_OFFSET,
    USER_SIGNUP_DISTRIBUTION, GENDER_DISTRIBUTION, ACADEMIC_YEAR_DISTRIBUTION,
    DAILY_ACTIVE_USERS, DAILY_SESSIONS, DAILY_VIBES, DAILY_MATCHES, DAILY_MESSAGES,
    PREMIUM_UPGRADES, POSITIVE_ADJECTIVES, NEGATIVE_ADJECTIVES,
    ACTIVITY_PEAKS, PREMIUM_PRICE_MONTHLY, PREMIUM_AVG_LIFETIME_MONTHS,
    CONVERSATION_DEPTH_DISTRIBUTION, TOTAL_MESSAGE_REQUESTS,
    MESSAGE_REQUESTS_ACCEPTED, MESSAGE_REQUESTS_DECLINED,
    FUNNEL_TARGETS, AVG_SESSIONS_PER_USER_PER_DAY, AVG_SESSION_DURATION_MINUTES,
    AVG_VIBE_TO_MATCH_TIME_MINUTES, AVG_RESPONSE_TIME_MINUTES,
    VIBE_TO_MATCH_RATE, RESPONSE_RATE, MESSAGE_REQUEST_ACCEPTANCE_RATE
)
from database import Database

# Set seed for deterministic generation
random.seed(42)

class DataGenerator:
    def __init__(self, db: Database):
        self.db = db
        self.users: List[Dict] = []
        self.user_id_counter = 1
        self.vibe_id_counter = 1
        self.match_id_counter = 1
        self.conversation_id_counter = 1
        self.message_id_counter = 1
        self.request_id_counter = 1
        self.subscription_id_counter = 1
        
    def generate_all(self):
        """Generate all demo data"""
        print("Generating users...")
        self.generate_users()
        
        print("Generating premium subscriptions...")
        self.generate_premium_subscriptions()
        
        print("Generating sessions...")
        self.generate_sessions()
        
        print("Generating vibes...")
        self.generate_vibes()
        
        print("Generating matches...")
        self.generate_matches()
        
        print("Generating message requests...")
        self.generate_message_requests()
        
        print("Generating conversations and messages...")
        self.generate_conversations_and_messages()
        
        print("Generating user events...")
        self.generate_user_events()
        
        print("Data generation complete!")
    
    def generate_users(self):
        """Generate 100 users with specified signup distribution"""
        cursor = self.db.get_connection().cursor()
        
        # Create user pool with gender distribution
        gender_pool = []
        for gender, count in GENDER_DISTRIBUTION.items():
            gender_pool.extend([gender] * count)
        random.shuffle(gender_pool)
        
        # Create academic year pool
        academic_pool = []
        for year, count in ACADEMIC_YEAR_DISTRIBUTION.items():
            academic_pool.extend([year] * count)
        random.shuffle(academic_pool)
        
        user_idx = 0
        for date_str, count in USER_SIGNUP_DISTRIBUTION.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            
            # Distribute signups throughout the day with peak at 5-6 PM
            for i in range(count):
                # Signup time weighted towards afternoon/evening
                hour = self._get_weighted_hour([(14, 20, 0.6), (9, 14, 0.3), (20, 24, 0.1)])
                minute = random.randint(0, 59)
                signup_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                
                user = {
                    'user_id': self.user_id_counter,
                    'signup_timestamp': signup_time.isoformat(),
                    'gender': gender_pool[user_idx],
                    'academic_year': academic_pool[user_idx],
                    'profile_image_uploaded': 1,
                    'is_premium': 0,
                    'premium_upgrade_timestamp': None
                }
                
                cursor.execute("""
                    INSERT INTO users (user_id, signup_timestamp, gender, academic_year, 
                                    profile_image_uploaded, is_premium, premium_upgrade_timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    user['user_id'], user['signup_timestamp'], user['gender'],
                    user['academic_year'], user['profile_image_uploaded'],
                    user['is_premium'], user['premium_upgrade_timestamp']
                ))
                
                self.users.append(user)
                self.user_id_counter += 1
                user_idx += 1
        
        self.db.get_connection().commit()
    
    def generate_premium_subscriptions(self):
        """Generate premium subscriptions with specified distribution"""
        cursor = self.db.get_connection().cursor()
        
        premium_users = []
        for date_str, count in PREMIUM_UPGRADES.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            
            # Select users who signed up on or before this date
            eligible_users = [u for u in self.users 
                            if datetime.fromisoformat(u['signup_timestamp']) <= date]
            eligible_users = [u for u in eligible_users if u['user_id'] not in premium_users]
            
            selected = random.sample(eligible_users, min(count, len(eligible_users)))
            
            for user in selected:
                # Upgrade time during afternoon/evening
                hour = self._get_weighted_hour([(14, 20, 0.7), (9, 14, 0.3)])
                minute = random.randint(0, 59)
                upgrade_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                
                # Update user to premium
                cursor.execute("""
                    UPDATE users SET is_premium = 1, premium_upgrade_timestamp = ?
                    WHERE user_id = ?
                """, (upgrade_time.isoformat(), user['user_id']))
                
                user['is_premium'] = 1
                user['premium_upgrade_timestamp'] = upgrade_time.isoformat()
                premium_users.append(user['user_id'])
                
                # Create subscription record
                end_time = upgrade_time + timedelta(days=30 * PREMIUM_AVG_LIFETIME_MONTHS)
                cursor.execute("""
                    INSERT INTO premium_subscriptions 
                    (subscription_id, user_id, start_timestamp, end_timestamp, amount_paid, status)
                    VALUES (?, ?, ?, ?, ?, 'active')
                """, (
                    self.subscription_id_counter,
                    user['user_id'],
                    upgrade_time.isoformat(),
                    end_time.isoformat(),
                    PREMIUM_PRICE_MONTHLY * PREMIUM_AVG_LIFETIME_MONTHS
                ))
                
                self.subscription_id_counter += 1
        
        self.db.get_connection().commit()
    
    def generate_sessions(self):
        """Generate sessions with specified daily counts and activity patterns"""
        cursor = self.db.get_connection().cursor()
        
        for date_str, target_sessions in DAILY_SESSIONS.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            dau = DAILY_ACTIVE_USERS[date_str]
            
            # Get active users for this day (signed up on or before)
            eligible_users = [u for u in self.users 
                          if datetime.fromisoformat(u['signup_timestamp']) <= date]
            # Ensure we select exactly DAU users (or all if fewer)
            if len(eligible_users) >= dau:
                active_users = random.sample(eligible_users, dau)
            else:
                active_users = eligible_users
            
            # Distribute sessions among active users
            sessions_per_user = self._distribute_sessions(len(active_users), target_sessions)
            
            for user, num_sessions in zip(active_users, sessions_per_user):
                for _ in range(num_sessions):
                    # Session start time following activity peaks
                    start_hour = self._get_weighted_hour(ACTIVITY_PEAKS)
                    start_minute = random.randint(0, 59)
                    start_time = date.replace(hour=start_hour, minute=start_minute, 
                                            second=random.randint(0, 59))
                    
                    # Session duration: average 3.2 minutes with variance
                    duration_seconds = int((AVG_SESSION_DURATION_MINUTES + 
                                          random.gauss(0, 1.5)) * 60)
                    duration_seconds = max(30, min(duration_seconds, 600))  # 30s to 10min
                    
                    end_time = start_time + timedelta(seconds=duration_seconds)
                    
                    # Ensure end_time doesn't exceed day boundary
                    if end_time.date() > date.date():
                        end_time = date.replace(hour=23, minute=59, second=59)
                        duration_seconds = int((end_time - start_time).total_seconds())
                    
                    cursor.execute("""
                        INSERT INTO sessions (user_id, start_timestamp, 
                                           end_timestamp, duration_seconds)
                        VALUES (?, ?, ?, ?)
                    """, (user['user_id'], start_time.isoformat(),
                         end_time.isoformat(), duration_seconds))
        
        self.db.get_connection().commit()
    
    def generate_vibes(self):
        """Generate vibes with specified daily counts and adjective distribution"""
        cursor = self.db.get_connection().cursor()
        
        # Create adjective pool
        adjective_pool = []
        for adj, count in POSITIVE_ADJECTIVES.items():
            adjective_pool.extend([adj] * count)
        for adj, count in NEGATIVE_ADJECTIVES.items():
            adjective_pool.extend([adj] * count)
        random.shuffle(adjective_pool)
        
        vibe_pool_idx = 0
        
        # Track vibes created per day to ensure we hit targets
        vibes_created_by_date = defaultdict(int)
        
        # Track pairs for reciprocal vibes (to ensure matches)
        reciprocal_pairs = defaultdict(list)  # (date, user1_id, user2_id, adjective) -> list of vibe_ids
        
        for date_str, target_vibes in DAILY_VIBES.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            dau = DAILY_ACTIVE_USERS[date_str]
            target_matches = DAILY_MATCHES.get(date_str, 0)
            
            # Get active users
            eligible_users = [u for u in self.users 
                          if datetime.fromisoformat(u['signup_timestamp']) <= date]
            # Ensure we select exactly DAU users (or all if fewer)
            if len(eligible_users) >= dau:
                active_users = random.sample(eligible_users, dau)
            else:
                active_users = eligible_users
            
            # First, create reciprocal vibes to ensure matches
            # We need target_matches * 2 vibes for matches (one each direction)
            if len(active_users) >= 2 and target_matches > 0:
                # Create enough reciprocal pairs to guarantee matches
                reciprocal_vibes_needed = target_matches * 2
                # But don't exceed available vibe budget
                if reciprocal_vibes_needed > target_vibes:
                    reciprocal_vibes_needed = target_vibes - (target_vibes % 2)  # Make it even
                pairs_created = 0
                
                # Create exactly target_matches reciprocal pairs (each pair = 2 vibes)
                for _ in range(target_matches):
                    # Check if we have room for 2 more vibes
                    if vibes_created_by_date[date_str] + 2 > target_vibes:
                        break
                    
                    if len(active_users) < 2:
                        break
                    
                    # Pick two different users
                    user1, user2 = random.sample(active_users, 2)
                    # Pick an adjective (use same adjective for both)
                    adjective = adjective_pool[vibe_pool_idx]
                    vibe_pool_idx = (vibe_pool_idx + 1) % len(adjective_pool)
                    
                    # Create vibe from user1 to user2
                    hour = self._get_weighted_hour(ACTIVITY_PEAKS)
                    minute = random.randint(0, 59)
                    vibe1_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                    expires_at1 = vibe1_time + timedelta(hours=24)
                    
                    cursor.execute("""
                        INSERT INTO vibes (vibe_id, sender_id, receiver_id, adjective, timestamp, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.vibe_id_counter, user1['user_id'], user2['user_id'],
                         adjective, vibe1_time.isoformat(), expires_at1.isoformat()))
                    self.vibe_id_counter += 1
                    vibes_created_by_date[date_str] += 1
                    
                    # Create reciprocal vibe from user2 to user1 (slightly later, same day)
                    vibe2_time = vibe1_time + timedelta(minutes=random.randint(1, 30))
                    # Ensure it's still on the same day
                    if vibe2_time.date() != date.date():
                        vibe2_time = date.replace(hour=23, minute=random.randint(0, 59), second=random.randint(0, 59))
                    expires_at2 = vibe2_time + timedelta(hours=24)
                    
                    cursor.execute("""
                        INSERT INTO vibes (vibe_id, sender_id, receiver_id, adjective, timestamp, expires_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (self.vibe_id_counter, user2['user_id'], user1['user_id'],
                         adjective, vibe2_time.isoformat(), expires_at2.isoformat()))
                    self.vibe_id_counter += 1
                    vibes_created_by_date[date_str] += 1
                    
                    pairs_created += 1
            
            # Premium users send 2.5x more vibes
            premium_users = [u for u in active_users if u['is_premium']]
            free_users = [u for u in active_users if not u['is_premium']]
            
            # Distribute remaining vibes: premium users get more
            remaining_vibes = target_vibes - vibes_created_by_date[date_str]
            if len(premium_users) == 0:
                premium_vibes = 0
                free_vibes = remaining_vibes
            else:
                total_weight = len(free_users) + len(premium_users) * 2.5
                if total_weight > 0:
                    premium_vibes = int(remaining_vibes * (len(premium_users) * 2.5 / total_weight))
                    free_vibes = remaining_vibes - premium_vibes
                else:
                    premium_vibes = 0
                    free_vibes = remaining_vibes
            
            # Generate vibes from premium users
            if len(premium_users) > 0 and premium_vibes > 0:
                premium_vibes_per_user = self._distribute_sessions(len(premium_users), premium_vibes)
                for user, num_vibes in zip(premium_users, premium_vibes_per_user):
                    for _ in range(num_vibes):
                        if vibes_created_by_date[date_str] >= target_vibes:
                            break
                        self._create_vibe(cursor, user, active_users, date, adjective_pool, vibe_pool_idx)
                        vibe_pool_idx = (vibe_pool_idx + 1) % len(adjective_pool)
                        vibes_created_by_date[date_str] += 1
            
            # Generate vibes from free users
            if len(free_users) > 0 and free_vibes > 0:
                free_vibes_per_user = self._distribute_sessions(len(free_users), free_vibes)
                for user, num_vibes in zip(free_users, free_vibes_per_user):
                    for _ in range(num_vibes):
                        if vibes_created_by_date[date_str] >= target_vibes:
                            break
                        self._create_vibe(cursor, user, active_users, date, adjective_pool, vibe_pool_idx)
                        vibe_pool_idx = (vibe_pool_idx + 1) % len(adjective_pool)
                        vibes_created_by_date[date_str] += 1
        
        self.db.get_connection().commit()
    
    def _create_vibe(self, cursor, sender, active_users, date, adjective_pool, pool_idx):
        """Create a single vibe"""
        # Select receiver (not self)
        receiver = random.choice([u for u in active_users if u['user_id'] != sender['user_id']])
        
        # Vibe time following activity peaks
        hour = self._get_weighted_hour(ACTIVITY_PEAKS)
        minute = random.randint(0, 59)
        vibe_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
        
        # Expires after 24 hours
        expires_at = vibe_time + timedelta(hours=24)
        
        adjective = adjective_pool[pool_idx]
        
        cursor.execute("""
            INSERT INTO vibes (vibe_id, sender_id, receiver_id, adjective, timestamp, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (self.vibe_id_counter, sender['user_id'], receiver['user_id'],
             adjective, vibe_time.isoformat(), expires_at.isoformat()))
        
        self.vibe_id_counter += 1
    
    def generate_matches(self):
        """Generate matches from vibes with ~18.5% match rate"""
        cursor = self.db.get_connection().cursor()
        
        # Get all vibes
        cursor.execute("SELECT vibe_id, sender_id, receiver_id, adjective, timestamp FROM vibes ORDER BY timestamp")
        all_vibes = [dict(row) for row in cursor.fetchall()]
        
        # Create a map of (sender_id, receiver_id, adjective) -> list of vibes
        vibe_map = defaultdict(list)
        for vibe in all_vibes:
            key = (vibe['sender_id'], vibe['receiver_id'], vibe['adjective'])
            vibe_map[key].append(vibe)
        
        # Track which vibes have been matched
        matched_vibes = set()
        
        for date_str, target_matches in DAILY_MATCHES.items():
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            date_end = date + timedelta(days=1)
            
            matches_created = 0
            
            # Find potential matches: when user A vibes user B and user B vibes user A with same adjective
            for vibe1 in all_vibes:
                if matches_created >= target_matches:
                    break
                
                if vibe1['vibe_id'] in matched_vibes:
                    continue
                
                vibe1_time = datetime.fromisoformat(vibe1['timestamp'])
                if not (date <= vibe1_time < date_end):
                    continue
                
                # Look for reciprocal vibe: receiver vibes sender with same adjective
                reciprocal_key = (vibe1['receiver_id'], vibe1['sender_id'], vibe1['adjective'])
                
                if reciprocal_key in vibe_map:
                    for vibe2 in vibe_map[reciprocal_key]:
                        if vibe2['vibe_id'] in matched_vibes:
                            continue
                        
                        if vibe2['vibe_id'] == vibe1['vibe_id']:
                            continue
                        
                        vibe2_time = datetime.fromisoformat(vibe2['timestamp'])
                        # Both vibes should be on the same day
                        if not (date <= vibe2_time < date_end):
                            continue
                        
                        # Create match
                        match_time = max(vibe1_time, vibe2_time) + timedelta(
                            minutes=int(AVG_VIBE_TO_MATCH_TIME_MINUTES + random.gauss(0, 20))
                        )
                        match_time = max(match_time, vibe2_time + timedelta(minutes=1))
                        
                        # Ensure match time is within the date range
                        if match_time >= date_end:
                            match_time = date.replace(hour=23, minute=59, second=0)
                        
                        expires_at = match_time + timedelta(hours=24)
                        
                        cursor.execute("""
                            INSERT INTO matches 
                            (match_id, user1_id, user2_id, vibe1_id, vibe2_id, 
                             adjective, created_timestamp, expires_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            self.match_id_counter,
                            min(vibe1['sender_id'], vibe2['sender_id']),
                            max(vibe1['sender_id'], vibe2['sender_id']),
                            vibe1['vibe_id'],
                            vibe2['vibe_id'],
                            vibe1['adjective'],
                            match_time.isoformat(),
                            expires_at.isoformat()
                        ))
                        
                        matched_vibes.add(vibe1['vibe_id'])
                        matched_vibes.add(vibe2['vibe_id'])
                        matches_created += 1
                        self.match_id_counter += 1
                        break
        
        self.db.get_connection().commit()
    
    def generate_message_requests(self):
        """Generate message requests with specified acceptance rate"""
        cursor = self.db.get_connection().cursor()
        
        # Only premium users can send requests
        premium_users = [u for u in self.users if u['is_premium']]
        
        # Distribute requests across days
        requests_per_day = TOTAL_MESSAGE_REQUESTS // 3
        remaining = TOTAL_MESSAGE_REQUESTS % 3
        
        request_counts = [requests_per_day] * 3
        for i in range(remaining):
            request_counts[i] += 1
        
        accepted_counts = [MESSAGE_REQUESTS_ACCEPTED // 3] * 3
        accepted_remaining = MESSAGE_REQUESTS_ACCEPTED % 3
        for i in range(accepted_remaining):
            accepted_counts[i] += 1
        
        request_idx = 0
        for day_idx, date_str in enumerate(['2024-12-25', '2024-12-26', '2024-12-27']):
            date = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=IST_OFFSET)
            num_requests = request_counts[day_idx]
            num_accepted = accepted_counts[day_idx]
            
            # Get active users
            active_users = [u for u in self.users 
                          if datetime.fromisoformat(u['signup_timestamp']) <= date]
            
            for i in range(num_requests):
                sender = random.choice(premium_users)
                possible_receivers = [u for u in active_users if u['user_id'] != sender['user_id']]
                if not possible_receivers:
                    # Skip if no possible receivers
                    continue
                receiver = random.choice(possible_receivers)
                
                hour = self._get_weighted_hour(ACTIVITY_PEAKS)
                minute = random.randint(0, 59)
                request_time = date.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                
                # Determine acceptance
                is_accepted = (request_idx < MESSAGE_REQUESTS_ACCEPTED)
                status = 'accepted' if is_accepted else 'declined'
                responded_at = None
                
                if is_accepted:
                    responded_at = request_time + timedelta(minutes=random.randint(5, 60))
                
                cursor.execute("""
                    INSERT INTO message_requests 
                    (request_id, sender_id, receiver_id, timestamp, status, responded_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    self.request_id_counter,
                    sender['user_id'],
                    receiver['user_id'],
                    request_time.isoformat(),
                    status,
                    responded_at.isoformat() if responded_at else None
                ))
                
                request_idx += 1
                self.request_id_counter += 1
        
        self.db.get_connection().commit()
    
    def generate_conversations_and_messages(self):
        """Generate conversations and messages with specified depth distribution"""
        cursor = self.db.get_connection().cursor()
        
        # Get all matches and accepted message requests
        cursor.execute("SELECT match_id, user1_id, user2_id, created_timestamp FROM matches")
        matches = cursor.fetchall()
        
        cursor.execute("""
            SELECT request_id, sender_id, receiver_id, responded_at 
            FROM message_requests WHERE status = 'accepted'
        """)
        accepted_requests = cursor.fetchall()
        
        # Create conversations from matches
        conversations_from_matches = []
        for match in matches:
            match_time = datetime.fromisoformat(match['created_timestamp'])
            conversations_from_matches.append({
                'match_id': match['match_id'],
                'user1_id': match['user1_id'],
                'user2_id': match['user2_id'],
                'created_timestamp': match_time,
                'message_request_id': None
            })
        
        # Create conversations from accepted message requests
        conversations_from_requests = []
        for req in accepted_requests:
            req_time = datetime.fromisoformat(req['responded_at'])
            conversations_from_requests.append({
                'match_id': None,
                'user1_id': req['sender_id'],
                'user2_id': req['receiver_id'],
                'created_timestamp': req_time,
                'message_request_id': req['request_id']
            })
        
        all_conversations = conversations_from_matches + conversations_from_requests
        random.shuffle(all_conversations)
        
        # Assign depth distribution
        depth_assignments = []
        for (min_depth, max_depth), count in CONVERSATION_DEPTH_DISTRIBUTION.items():
            for _ in range(count):
                if max_depth == 100:  # Special case for 31+
                    depth = random.randint(31, 47)  # Max 47 messages
                else:
                    depth = random.randint(min_depth, max_depth)
                depth_assignments.append(depth)
        
        # Ensure we have enough conversations
        while len(depth_assignments) < len(all_conversations):
            depth_assignments.append(random.randint(1, 5))
        
        depth_assignments = depth_assignments[:len(all_conversations)]
        random.shuffle(depth_assignments)
        
        # Track daily message counts and targets
        daily_message_counts = defaultdict(int)
        daily_targets = {date: count for date, count in DAILY_MESSAGES.items()}
        
        # Create conversations and messages
        for conv_data, depth in zip(all_conversations, depth_assignments):
            # Create conversation
            cursor.execute("""
                INSERT INTO conversations 
                (conversation_id, user1_id, user2_id, match_id, message_request_id, created_timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                self.conversation_id_counter,
                conv_data['user1_id'],
                conv_data['user2_id'],
                conv_data['match_id'],
                conv_data['message_request_id'],
                conv_data['created_timestamp'].isoformat()
            ))
            
            conv_id = self.conversation_id_counter
            self.conversation_id_counter += 1
            
            # Determine who initiates (premium user or user1)
            user1 = next(u for u in self.users if u['user_id'] == conv_data['user1_id'])
            user2 = next(u for u in self.users if u['user_id'] == conv_data['user2_id'])
            
            if user1['is_premium']:
                initiator_id = conv_data['user1_id']
                replier_id = conv_data['user2_id']
            elif user2['is_premium']:
                initiator_id = conv_data['user2_id']
                replier_id = conv_data['user1_id']
            else:
                # If neither is premium, user1 initiates (from match)
                initiator_id = conv_data['user1_id']
                replier_id = conv_data['user2_id']
            
            # Generate messages for this conversation
            current_time = conv_data['created_timestamp']
            last_message_time = current_time
            
            # First message from initiator (5-15 min after conversation start for requests)
            if conv_data['message_request_id']:
                current_time = current_time + timedelta(minutes=random.randint(5, 15))
            
            # Limit messages based on daily targets
            messages_for_conv = []
            for msg_idx in range(depth):
                # Determine sender (alternate, but initiator starts)
                if msg_idx == 0:
                    sender_id = initiator_id
                else:
                    # Alternate, but respect response rate
                    if random.random() < RESPONSE_RATE:
                        sender_id = replier_id if (msg_idx % 2 == 1) else initiator_id
                    else:
                        # No response, conversation ends
                        break
                
                # Message time following activity pattern
                hour = self._get_weighted_hour(ACTIVITY_PEAKS)
                minute = random.randint(0, 59)
                msg_time = current_time.replace(hour=hour, minute=minute, second=random.randint(0, 59))
                
                # Ensure message time progresses
                if msg_idx > 0:
                    msg_time = last_message_time + timedelta(
                        minutes=int(AVG_RESPONSE_TIME_MINUTES + random.gauss(0, 5))
                    )
                    msg_time = max(msg_time, last_message_time + timedelta(minutes=1))
                
                # Ensure within date range
                if msg_time >= DEMO_END_DATE:
                    break
                
                msg_date_str = msg_time.date().strftime('%Y-%m-%d')
                target_for_date = daily_targets.get(msg_date_str, 0)
                current_count = daily_message_counts.get(msg_date_str, 0)
                
                # Check if we've exceeded daily target (allow small overflow)
                if current_count >= target_for_date + 5:
                    break
                
                parent_id = self.message_id_counter - 1 if msg_idx > 0 else None
                
                messages_for_conv.append({
                    'message_id': self.message_id_counter,
                    'sender_id': sender_id,
                    'content': f"Message {msg_idx + 1}",
                    'timestamp': msg_time.isoformat(),
                    'parent_id': parent_id
                })
                
                daily_message_counts[msg_date_str] = daily_message_counts.get(msg_date_str, 0) + 1
                last_message_time = msg_time
                current_time = msg_time
                self.message_id_counter += 1
            
            # Insert all messages for this conversation
            for msg_data in messages_for_conv:
                cursor.execute("""
                    INSERT INTO messages 
                    (message_id, conversation_id, sender_id, content, timestamp, parent_message_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    msg_data['message_id'],
                    conv_id,
                    msg_data['sender_id'],
                    msg_data['content'],
                    msg_data['timestamp'],
                    msg_data['parent_id']
                ))
            
            # Update conversation last_message_timestamp
            cursor.execute("""
                UPDATE conversations SET last_message_timestamp = ?
                WHERE conversation_id = ?
            """, (last_message_time.isoformat(), conv_id))
        
        self.db.get_connection().commit()
    
    def generate_user_events(self):
        """Generate user events for funnel tracking"""
        cursor = self.db.get_connection().cursor()
        
        # Track first actions
        first_vibe_senders = set()
        first_match_users = set()
        first_message_users = set()
        
        # First vibe sent
        cursor.execute("""
            SELECT DISTINCT sender_id, MIN(timestamp) as first_vibe
            FROM vibes GROUP BY sender_id
        """)
        for row in cursor.fetchall():
            first_vibe_senders.add(row['sender_id'])
            cursor.execute("""
                INSERT INTO user_events (user_id, event_type, timestamp)
                VALUES (?, 'first_vibe_sent', ?)
            """, (row['sender_id'], row['first_vibe']))
        
        # First match
        cursor.execute("""
            SELECT user1_id, user2_id, created_timestamp FROM matches
            UNION
            SELECT user2_id, user1_id, created_timestamp FROM matches
            ORDER BY created_timestamp
        """)
        seen_users = set()
        for row in cursor.fetchall():
            for user_id in [row['user1_id'], row['user2_id']]:
                if user_id not in seen_users:
                    seen_users.add(user_id)
                    cursor.execute("""
                        INSERT INTO user_events (user_id, event_type, timestamp)
                        VALUES (?, 'match_created', ?)
                    """, (user_id, row['created_timestamp']))
        
        # First message
        cursor.execute("""
            SELECT sender_id, MIN(timestamp) as first_message
            FROM messages GROUP BY sender_id
        """)
        for row in cursor.fetchall():
            cursor.execute("""
                INSERT INTO user_events (user_id, event_type, timestamp)
                VALUES (?, 'first_message', ?)
            """, (row['sender_id'], row['first_message']))
        
        self.db.get_connection().commit()
    
    def _get_weighted_hour(self, peaks: List[Tuple[int, int, float]]) -> int:
        """Get a random hour weighted by activity peaks"""
        # Create cumulative distribution
        weights = []
        hours = []
        for start_hour, end_hour, weight in peaks:
            for hour in range(start_hour, end_hour):
                hours.append(hour)
                weights.append(weight / (end_hour - start_hour))
        
        # Fill in remaining hours with low weight
        for hour in range(24):
            if hour not in hours:
                hours.append(hour)
                weights.append(0.05)
        
        # Normalize weights
        total_weight = sum(weights)
        weights = [w / total_weight for w in weights]
        
        # Sample
        return random.choices(hours, weights=weights)[0]
    
    def _distribute_sessions(self, num_users: int, target_total: int) -> List[int]:
        """Distribute sessions among users to reach target total"""
        if num_users == 0:
            return []
        
        # Each user gets at least 3 sessions
        base_sessions = [3] * num_users
        remaining = target_total - sum(base_sessions)
        
        if remaining <= 0:
            # If target is less than minimum, distribute proportionally
            if target_total < num_users * 3:
                base_sessions = [target_total // num_users] * num_users
                extra = target_total % num_users
                for i in range(extra):
                    base_sessions[i] += 1
            return base_sessions[:num_users]
        
        # Distribute remaining sessions
        while remaining > 0 and num_users > 0:
            user_idx = random.randint(0, num_users - 1)
            base_sessions[user_idx] += 1
            remaining -= 1
        
        return base_sessions
