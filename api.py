"""
REST API for Citadel Analytics Demo System
Provides endpoints for dashboard consumption
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from database import Database
from analytics import Analytics
from config import DEMO_MODE, DB_PATH
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')
CORS(app)  # Enable CORS for dashboard access

@app.route('/', methods=['GET'])
def dashboard():
    """Serve the dashboard UI"""
    return send_from_directory('static', 'index.html')

@app.route('/api', methods=['GET'])
def api_info():
    """API information endpoint"""
    return jsonify({
        'message': 'Citadel Analytics Demo API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/api/health',
            'all_metrics': '/api/metrics',
            'users': '/api/metrics/users',
            'sessions': '/api/metrics/sessions',
            'vibes': '/api/metrics/vibes',
            'matches': '/api/metrics/matches',
            'messages': '/api/metrics/messages',
            'conversations': '/api/metrics/conversations',
            'revenue': '/api/metrics/revenue',
            'funnel': '/api/metrics/funnel',
            'activity': '/api/metrics/activity',
            'demographics': '/api/metrics/demographics',
            'events': '/api/events?type=<type>&limit=<n>'
        }
    })

def get_db():
    """Get database connection"""
    return Database(DB_PATH)

def get_analytics():
    """Get analytics instance"""
    db = get_db()
    return Analytics(db), db

@app.route('/api/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'demo_mode': DEMO_MODE
    })

@app.route('/api/metrics', methods=['GET'])
def get_all_metrics():
    """Get all analytics metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_all_metrics()
        metrics['message_requests'] = analytics.get_message_request_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/users', methods=['GET'])
def get_user_metrics():
    """Get user metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_user_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/sessions', methods=['GET'])
def get_session_metrics():
    """Get session metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_session_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/vibes', methods=['GET'])
def get_vibe_metrics():
    """Get vibe metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_vibe_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/matches', methods=['GET'])
def get_match_metrics():
    """Get match metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_match_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/messages', methods=['GET'])
def get_message_metrics():
    """Get message metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_message_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/conversations', methods=['GET'])
def get_conversation_metrics():
    """Get conversation metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_conversation_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/revenue', methods=['GET'])
def get_revenue_metrics():
    """Get revenue metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_revenue_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/funnel', methods=['GET'])
def get_funnel_metrics():
    """Get funnel metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_funnel_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/activity', methods=['GET'])
def get_activity_metrics():
    """Get activity heatmap metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_activity_metrics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/metrics/demographics', methods=['GET'])
def get_demographics():
    """Get demographic metrics"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    try:
        analytics, db = get_analytics()
        metrics = analytics.get_demographics()
        db.close()
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/events', methods=['GET'])
def get_events():
    """Get raw event data (for debugging/verification)"""
    if not DEMO_MODE:
        return jsonify({'error': 'DEMO_MODE not enabled'}), 403
    
    event_type = request.args.get('type', 'all')
    limit = int(request.args.get('limit', 100))
    
    try:
        db = get_db()
        cursor = db.get_connection().cursor()
        
        events = []
        if event_type in ['all', 'sessions']:
            cursor.execute("SELECT * FROM sessions ORDER BY start_timestamp LIMIT ?", (limit,))
            events.extend([dict(row) for row in cursor.fetchall()])
        
        if event_type in ['all', 'vibes']:
            cursor.execute("SELECT * FROM vibes ORDER BY timestamp LIMIT ?", (limit,))
            events.extend([dict(row) for row in cursor.fetchall()])
        
        if event_type in ['all', 'matches']:
            cursor.execute("SELECT * FROM matches ORDER BY created_timestamp LIMIT ?", (limit,))
            events.extend([dict(row) for row in cursor.fetchall()])
        
        if event_type in ['all', 'messages']:
            cursor.execute("SELECT * FROM messages ORDER BY timestamp LIMIT ?", (limit,))
            events.extend([dict(row) for row in cursor.fetchall()])
        
        db.close()
        return jsonify({'events': events, 'count': len(events)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    if not DEMO_MODE:
        print("Warning: DEMO_MODE is not enabled. API will return errors.")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
