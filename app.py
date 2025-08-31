from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime, timezone, timedelta
import os
import secrets
import csv
from io import StringIO
from dotenv import load_dotenv
import pytz
from functools import wraps

# Import models and forms
from models import db, User, Measurement, APIKey, MEASUREMENT_POINTS, CHART_COLORS
from forms import LoginForm, RegistrationForm, UpdateProfileForm, ChangePasswordForm
from utils import generate_avatar, create_chart_colors

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///liwanag.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# API Key decorator
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key') or request.args.get('api_key')
        if not api_key:
            return jsonify({'error': 'API key is required'}), 401
        
        if not APIKey.verify_key(api_key):
            return jsonify({'error': 'Invalid API key'}), 401
        
        return f(*args, **kwargs)
    return decorated_function

# Timezone utility
def convert_utc_to_gmt8(utc_datetime):
    """Convert UTC datetime to GMT+8"""
    if utc_datetime is None:
        return None
    utc = pytz.UTC
    gmt8 = pytz.timezone('Asia/Manila')  # GMT+8
    if utc_datetime.tzinfo is None:
        utc_datetime = utc.localize(utc_datetime)
    return utc_datetime.astimezone(gmt8)

# Landing page route
@app.route('/')
def home():
    return render_template('index.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            # Update last login
            user.last_login = datetime.now(timezone.utc)
            
            # Handle remember me
            remember = form.remember_me.data
            if remember:
                token = user.set_remember_token()
                # Store token in secure cookie
                resp = make_response(redirect(url_for('dashboard')))
                resp.set_cookie('remember_token', token, max_age=30*24*60*60, secure=True, httponly=True)
            
            db.session.commit()
            login_user(user, remember=remember)
            flash('Login successful!', 'success')
            
            # Redirect to next page or dashboard
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    
    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            user = User(
                username=form.username.data.lower(),
                first_name=form.first_name.data.strip(),
                surname=form.surname.data.strip(),
                middle_initial=form.middle_initial.data.strip().upper() if form.middle_initial.data else None,
                hospital_name=form.hospital_name.data.strip(),
                hospital_room_no=form.hospital_room_no.data.strip()
            )
            user.set_password(form.password.data)
            user.generate_profile_picture()
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Registration failed. Please try again.', 'danger')
    
    return render_template('auth/register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    # Clear remember token
    if current_user.remember_token:
        current_user.clear_remember_token()
        db.session.commit()
    
    logout_user()
    resp = make_response(redirect(url_for('home')))
    resp.set_cookie('remember_token', '', expires=0)
    flash('You have been logged out.', 'info')
    return resp

# Dashboard routes
@app.route('/dashboard')
@login_required
def dashboard():
    # Get user's recent measurements
    recent_measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                          .order_by(Measurement.timestamp.desc())\
                                          .limit(10).all()
    
    # Get statistics
    total_measurements = Measurement.query.filter_by(user_id=current_user.id).count()
    
    # Get today's measurements count
    today = datetime.now(timezone.utc).date()
    today_measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                         .filter(db.func.date(Measurement.timestamp) == today)\
                                         .count()
    
    return render_template('dashboard/dashboard.html', 
                         recent_measurements=recent_measurements,
                         total_measurements=total_measurements,
                         today_measurements=today_measurements,
                         convert_timezone=convert_utc_to_gmt8)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(obj=current_user)
    
    # Calculate days since account creation
    days_active = 0
    if current_user.created_at:
        days_active = (datetime.utcnow() - current_user.created_at).days
        if days_active < 0:
            days_active = 0
    
    if form.validate_on_submit():
        try:
            current_user.first_name = form.first_name.data.strip()
            current_user.surname = form.surname.data.strip()
            current_user.middle_initial = form.middle_initial.data.strip().upper() if form.middle_initial.data else None
            current_user.hospital_name = form.hospital_name.data.strip()
            current_user.hospital_room_no = form.hospital_room_no.data.strip()
            
            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            flash('Failed to update profile. Please try again.', 'danger')
    
    return render_template('dashboard/profile.html', form=form,
                         convert_timezone=convert_utc_to_gmt8,
                         days_active=days_active)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            try:
                current_user.set_password(form.new_password.data)
                db.session.commit()
                flash('Password changed successfully!', 'success')
                return redirect(url_for('profile'))
            except Exception as e:
                db.session.rollback()
                flash('Failed to change password. Please try again.', 'danger')
        else:
            flash('Current password is incorrect.', 'danger')
    
    return render_template('dashboard/change_password.html', form=form)

@app.route('/avatar/<username>')
def avatar(username):
    """Generate and serve user avatar"""
    from flask import Response
    import base64
    
    user = User.query.filter_by(username=username).first()
    if not user:
        # Generate default avatar
        avatar_data = generate_avatar(username)
    else:
        if not user.profile_picture:
            # Generate and save avatar
            avatar_data = generate_avatar(user.username)
            user.profile_picture = avatar_data
            db.session.commit()
        else:
            # Check if it's already base64 data
            if user.profile_picture.startswith('data:image'):
                avatar_data = user.profile_picture
            else:
                # Old format, regenerate
                avatar_data = generate_avatar(user.username)
                user.profile_picture = avatar_data
                db.session.commit()
    
    # Extract the base64 data from the data URL
    if avatar_data.startswith('data:image/png;base64,'):
        base64_data = avatar_data.split(',')[1]
        image_data = base64.b64decode(base64_data)
        
        return Response(
            image_data,
            mimetype='image/png',
            headers={
                'Cache-Control': 'public, max-age=3600',  # Cache for 1 hour
                'Content-Type': 'image/png'
            }
        )
    else:
        # Fallback - return a simple response
        return Response("Avatar not available", status=404)

# Data visualization routes
@app.route('/my-data')
@login_required
def my_data():
    # Get user's recent measurements
    measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                   .order_by(Measurement.timestamp.desc()).all()
    
    return render_template('dashboard/my_data.html', 
                         measurements=measurements,
                         measurement_points=MEASUREMENT_POINTS,
                         convert_timezone=convert_utc_to_gmt8)

@app.route('/history')
@login_required
def history():
    # Get user's measurements grouped by date
    measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                   .order_by(Measurement.timestamp.desc()).all()
    
    return render_template('dashboard/history.html', 
                         measurements=measurements,
                         convert_timezone=convert_utc_to_gmt8)

@app.route('/measurement/<int:measurement_id>')
@login_required
def view_measurement(measurement_id):
    measurement = Measurement.query.filter_by(id=measurement_id, user_id=current_user.id).first_or_404()
    
    return render_template('dashboard/measurement_detail.html',
                         measurement=measurement,
                         measurement_points=MEASUREMENT_POINTS,
                         convert_timezone=convert_utc_to_gmt8)

# API Routes for device data
@app.route('/api/data', methods=['POST'])
@require_api_key
def receive_data():
    """
    API endpoint to receive data from LIWANAG device
    Expected JSON format:
    {
        "user_id": 1,
        "vpt": 5,
        "temp": 31.2,
        "spo2": 98,
        "toe": "Right Heel"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        required_fields = ['user_id', 'toe']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Validate user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({'error': 'Invalid user_id'}), 400
        
        # Create measurement directly
        measurement = Measurement(
            user_id=user.id,
            point_name=data['toe'],
            vpt_voltage=data.get('vpt'),
            temperature=data.get('temp'),
            spo2=data.get('spo2'),
            timestamp=datetime.now(timezone.utc)  # Server timestamp
        )
        
        db.session.add(measurement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Data received successfully',
            'measurement_id': measurement.id,
            'timestamp': measurement.timestamp.isoformat()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/users/<int:user_id>/measurements')
@require_api_key
def get_user_measurements(user_id):
    """Get all measurements for a user"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    
    measurements = Measurement.query.filter_by(user_id=user_id)\
                                   .order_by(Measurement.timestamp.desc()).all()
    
    return jsonify({
        'measurements': [measurement.to_dict() for measurement in measurements]
    })

# Dashboard API endpoints for charts and tables
@app.route('/api/chart-data')
@login_required
def get_chart_data():
    """Get chart data for VPT and vitals charts"""
    days = request.args.get('days', 7, type=int)
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get user's measurements within date range
    measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                   .filter(Measurement.timestamp >= start_date)\
                                   .filter(Measurement.timestamp <= end_date)\
                                   .order_by(Measurement.timestamp).all()
    
    # Initialize chart data structure
    chart_data = {
        'rightFoot': {
            'labels': [],
            'heel': [], 'instep': [], 'fifth_mt': [], 'third_mt': [], 'first_mt': [], 'big_toe': []
        },
        'leftFoot': {
            'labels': [],
            'heel': [], 'instep': [], 'fifth_mt': [], 'third_mt': [], 'first_mt': [], 'big_toe': []
        },
        'vitals': {
            'labels': [],
            'temperature': [],
            'spo2': []
        }
    }
    
    # If we have very recent data (less than 24 hours), group by hour instead of day
    if measurements:
        latest_measurement = max(measurements, key=lambda x: x.timestamp)
        
        # Ensure timestamp is timezone-aware for comparison
        latest_timestamp = latest_measurement.timestamp
        if latest_timestamp.tzinfo is None:
            latest_timestamp = latest_timestamp.replace(tzinfo=timezone.utc)
        
        time_diff = datetime.now(timezone.utc) - latest_timestamp
        if time_diff.total_seconds() < 24 * 3600:  # Less than 24 hours
            time_format = '%m/%d %H:%M'  # Include time for recent data
        else:
            time_format = '%m/%d'  # Daily grouping for older data
    else:
        time_format = '%m/%d'
    
    # Group measurements by time period
    time_data = {}
    for measurement in measurements:
        time_str = measurement.timestamp.strftime(time_format)
        if time_str not in time_data:
            time_data[time_str] = {
                'timestamp': measurement.timestamp,
                'vpt': {'right': {}, 'left': {}},
                'temp': [], 'spo2': []
            }
        
        # Parse point name (e.g., "Right Heel" -> right_heel)
        point_parts = measurement.point_name.lower().split()
        if len(point_parts) >= 2:
            foot = point_parts[0]  # right/left
            location = '_'.join(point_parts[1:]).replace(' ', '_')
            
            # Map location names
            location_map = {
                'heel': 'heel', 'in_step': 'instep', 'instep': 'instep',
                '5th_mt': 'fifth_mt', 'fifth_mt': 'fifth_mt',
                '3rd_mt': 'third_mt', 'third_mt': 'third_mt', 
                '1st_mt': 'first_mt', 'first_mt': 'first_mt',
                'big_toe': 'big_toe', 'bigtoe': 'big_toe'
            }
            
            mapped_location = location_map.get(location, location)
            
            if foot in ['right', 'left'] and mapped_location in chart_data[f'{foot}Foot']:
                if measurement.vpt_voltage is not None:
                    # Store latest value for this time period and point
                    time_data[time_str]['vpt'][foot][mapped_location] = measurement.vpt_voltage
                
                if measurement.temperature is not None:
                    time_data[time_str]['temp'].append(measurement.temperature)
                
                if measurement.spo2 is not None:
                    time_data[time_str]['spo2'].append(measurement.spo2)
    
    # Convert to chart format (sort by timestamp, not string)
    sorted_time_data = sorted(time_data.items(), key=lambda x: x[1]['timestamp'])
    
    for time_str, time_values in sorted_time_data:
        chart_data['rightFoot']['labels'].append(time_str)
        chart_data['leftFoot']['labels'].append(time_str)
        chart_data['vitals']['labels'].append(time_str)
        
        # Add VPT data for right foot
        for point in ['heel', 'instep', 'fifth_mt', 'third_mt', 'first_mt', 'big_toe']:
            value = time_values['vpt']['right'].get(point, None)
            chart_data['rightFoot'][point].append(value)
            
        # Add VPT data for left foot
        for point in ['heel', 'instep', 'fifth_mt', 'third_mt', 'first_mt', 'big_toe']:
            value = time_values['vpt']['left'].get(point, None)
            chart_data['leftFoot'][point].append(value)
        
        # Add vitals data (average for the time period)
        avg_temp = sum(time_values['temp']) / len(time_values['temp']) if time_values['temp'] else None
        avg_spo2 = sum(time_values['spo2']) / len(time_values['spo2']) if time_values['spo2'] else None
        
        chart_data['vitals']['temperature'].append(avg_temp)
        chart_data['vitals']['spo2'].append(avg_spo2)
    
    return jsonify(chart_data)

@app.route('/api/measurement-timeline')
@login_required
def get_measurement_timeline():
    """Get individual measurement timeline for detailed charts"""
    days = request.args.get('days', 7, type=int)
    point_name = request.args.get('point', None)
    
    # Calculate date range
    end_date = datetime.now(timezone.utc)
    start_date = end_date - timedelta(days=days)
    
    # Get user's measurements within date range
    query = Measurement.query.filter_by(user_id=current_user.id)\
                            .filter(Measurement.timestamp >= start_date)\
                            .filter(Measurement.timestamp <= end_date)
    
    # Filter by specific point if provided
    if point_name:
        query = query.filter(Measurement.point_name == point_name)
    
    measurements = query.order_by(Measurement.timestamp).all()
    
    # Group by measurement point
    timeline_data = {}
    
    for measurement in measurements:
        point = measurement.point_name
        if point not in timeline_data:
            timeline_data[point] = {
                'timestamps': [],
                'vpt_values': [],
                'temp_values': [],
                'spo2_values': []
            }
        
        # Format timestamp for display
        time_str = measurement.timestamp.strftime('%m/%d %H:%M')
        timeline_data[point]['timestamps'].append(time_str)
        timeline_data[point]['vpt_values'].append(measurement.vpt_voltage)
        timeline_data[point]['temp_values'].append(measurement.temperature)
        timeline_data[point]['spo2_values'].append(measurement.spo2)
    
    return jsonify(timeline_data)

@app.route('/api/current-vpt-readings')
@login_required
def get_current_vpt_readings():
    """Get current VPT readings for both feet"""
    
    vpt_data = {
        'right': {},
        'left': {}
    }
    
    measurement_points = ['heel', 'instep', '5th_mt', '3rd_mt', '1st_mt', 'big_toe']
    point_name_map = {
        'heel': 'Heel', 'instep': 'In Step', '5th_mt': '5th MT', 
        '3rd_mt': '3rd MT', '1st_mt': '1st MT', 'big_toe': 'Big Toe'
    }
    
    for foot in ['right', 'left']:
        for point in measurement_points:
            point_name = f"{foot.title()} {point_name_map[point]}"
            
            # Get latest VPT measurement for this point
            latest_measurement = Measurement.query.filter_by(user_id=current_user.id)\
                                                 .filter(Measurement.point_name == point_name)\
                                                 .filter(Measurement.vpt_voltage.isnot(None))\
                                                 .order_by(Measurement.timestamp.desc()).first()
            
            if latest_measurement:
                # Determine status based on voltage thresholds
                thresholds = {'5th_mt': 10, '1st_mt': 10}  # Higher threshold for metatarsals
                threshold = thresholds.get(point, 5)  # Default 5V threshold
                
                if latest_measurement.vpt_voltage <= threshold:
                    status = 'Normal'
                elif latest_measurement.vpt_voltage <= threshold * 1.5:
                    status = 'Elevated'
                else:
                    status = 'High'
                
                vpt_data[foot][point] = {
                    'value': latest_measurement.vpt_voltage,
                    'status': status,
                    'time': latest_measurement.timestamp.strftime('%I:%M %p')
                }
            else:
                vpt_data[foot][point] = {
                    'value': 0,
                    'status': 'No Data',
                    'time': '--'
                }
    
    return jsonify(vpt_data)

@app.route('/api/current-vitals-readings')
@login_required
def get_current_vitals_readings():
    """Get current temperature and SpO2 readings for both feet"""
    
    vitals_data = {
        'right': {},
        'left': {}
    }
    
    measurement_points = ['heel', 'instep', '5th_mt', '3rd_mt', '1st_mt', 'big_toe']
    point_name_map = {
        'heel': 'Heel', 'instep': 'In Step', '5th_mt': '5th MT', 
        '3rd_mt': '3rd MT', '1st_mt': '1st MT', 'big_toe': 'Big Toe'
    }
    
    for foot in ['right', 'left']:
        for point in measurement_points:
            point_name = f"{foot.title()} {point_name_map[point]}"
            
            # Get latest measurement with both temperature and SpO2
            latest_measurement = Measurement.query.filter_by(user_id=current_user.id)\
                                                 .filter(Measurement.point_name == point_name)\
                                                 .filter(Measurement.temperature.isnot(None))\
                                                 .filter(Measurement.spo2.isnot(None))\
                                                 .order_by(Measurement.timestamp.desc()).first()
            
            if latest_measurement:
                temp_value = latest_measurement.temperature
                spo2_value = latest_measurement.spo2
                
                # Determine combined status
                temp_normal = 36.0 <= temp_value <= 37.5
                spo2_normal = 95 <= spo2_value <= 100
                
                if temp_normal and spo2_normal:
                    status = 'Normal'
                elif not temp_normal and spo2_normal:
                    status = 'Temp Abnormal'
                elif temp_normal and not spo2_normal:
                    status = 'SpO2 Abnormal'
                else:
                    status = 'Both Abnormal'
                
                vitals_data[foot][point] = {
                    'temperature': temp_value,
                    'spo2': spo2_value,
                    'status': status,
                    'time': latest_measurement.timestamp.strftime('%I:%M %p')
                }
            else:
                vitals_data[foot][point] = {
                    'temperature': 0,
                    'spo2': 0,
                    'status': 'No Data',
                    'time': '--'
                }
    
    return jsonify(vitals_data)

@app.route('/api/data-json-send', methods=['POST'])
@require_api_key
def receive_sensor_data():
    """Receive sensor data from measurement devices"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
        
        # Validate required fields
        required_fields = ['vpt', 'temp', 'spo2', 'toe', 'username']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        if not user:
            return jsonify({'error': f'User not found: {data["username"]}'}), 404
        
        # Validate toe location format (e.g., "Right Heel")
        toe_name = data['toe'].strip()
        
        # Create a single measurement record with all sensor data
        timestamp = datetime.now(timezone.utc)
        
        measurement = Measurement(
            user_id=user.id,
            point_name=toe_name,
            vpt_voltage=float(data['vpt']),
            temperature=float(data['temp']),
            spo2=int(data['spo2']),
            timestamp=timestamp
        )
        db.session.add(measurement)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Sensor data received successfully',
            'measurement_id': measurement.id,
            'point_name': toe_name,
            'data': {
                'vpt': measurement.vpt_voltage,
                'temperature': measurement.temperature,
                'spo2': measurement.spo2,
                'timestamp': measurement.timestamp.isoformat()
            }
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid numeric value: {str(e)}'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

# Initialize database
def create_tables():
    db.create_all()
    
    # Create default API key if none exists
    if not APIKey.query.first():
        api_key = os.getenv('API_KEY', 'LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH')
        default_key = APIKey(
            key_name='Default Device Key',
            key_hash=APIKey.hash_key(api_key)
        )
        db.session.add(default_key)
        db.session.commit()
        print(f"Default API key created: {api_key}")

# Measurement Management API Routes
@app.route('/api/measurements/export')
@login_required
def export_measurements():
    """Export user's measurement data as CSV"""
    measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                   .order_by(Measurement.timestamp.asc()).all()
    
    # Create CSV content
    csv_content = "Timestamp,Point Name,VPT Voltage,Temperature,SpO2\n"
    for measurement in measurements:
        csv_content += f"{measurement.timestamp.isoformat()},{measurement.point_name},"
        csv_content += f"{measurement.vpt_voltage},{measurement.temperature},{measurement.spo2}\n"
    
    response = make_response(csv_content)
    response.headers["Content-Disposition"] = f"attachment; filename=measurements_{current_user.username}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@app.route('/api/measurements/<int:measurement_id>/export')
@login_required
def export_single_measurement(measurement_id):
    """Export a single measurement as CSV"""
    measurement = Measurement.query.filter_by(id=measurement_id, user_id=current_user.id).first_or_404()
    
    output = StringIO()
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['Measurement ID', 'Point Name', 'Timestamp', 'VPT Voltage', 'Temperature', 'SpO2', 'Notes'])
    
    # Write measurement data
    timestamp_local = convert_utc_to_gmt8(measurement.timestamp)
    writer.writerow([
        measurement.id,
        measurement.point_name,
        timestamp_local.strftime('%Y-%m-%d %H:%M:%S'),
        measurement.vpt_voltage or '',
        measurement.temperature or '',
        measurement.spo2 or '',
        measurement.notes or ''
    ])
    
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=measurement_{measurement_id}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@app.route('/api/measurements/<int:measurement_id>', methods=['DELETE'])
@login_required
def delete_measurement(measurement_id):
    """Delete a measurement"""
    try:
        measurement = Measurement.query.filter_by(id=measurement_id, user_id=current_user.id).first_or_404()
        
        db.session.delete(measurement)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Measurement deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/measurements/<int:measurement_id>/notes', methods=['PUT'])
@login_required
def update_measurement_notes(measurement_id):
    """Update notes for a measurement"""
    try:
        measurement = Measurement.query.filter_by(id=measurement_id, user_id=current_user.id).first_or_404()
        
        data = request.get_json()
        notes = data.get('notes', '')
        
        measurement.notes = notes
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Notes updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# Page Routes  
@app.route('/measurements')
@login_required
def measurements():
    """Measurements page"""
    measurements = Measurement.query.filter_by(user_id=current_user.id)\
                                   .order_by(Measurement.timestamp.desc()).all()
    return render_template('dashboard/measurements.html',
                         measurements=measurements,
                         measurement_points=MEASUREMENT_POINTS)

if __name__ == '__main__':
    with app.app_context():
        create_tables()
    
    app.run(host='0.0.0.0', port=2214)
