from flask import Blueprint, jsonify
from app import db

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    health_status = {
        'status': 'healthy',
        'database': check_database(),
        'disk_usage': check_disk_usage(),
        'memory_usage': check_memory_usage()
    }
    return jsonify(health_status)

def check_database():
    try:
        db.session.execute('SELECT 1')
        return 'connected'
    except Exception as e:
        return f'error: {str(e)}'

def check_disk_usage():
    import psutil
    disk = psutil.disk_usage('/')
    return {
        'total': disk.total,
        'used': disk.used,
        'free': disk.free,
        'percent': disk.percent
    }

def check_memory_usage():
    import psutil
    memory = psutil.virtual_memory()
    return {
        'total': memory.total,
        'available': memory.available,
        'percent': memory.percent
    } 