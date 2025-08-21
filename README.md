# RalphWebsite - LIWANAG Diabetic Foot Assessment System

A comprehensive web application for diabetic foot assessment using Vibration Perception Threshold (VPT) testing, temperature monitoring, and SpO2 measurements. This system is designed to work with the LIWANAG medical device for collecting and analyzing foot health data.

## 📋 Table of Contents

- [Features](#features)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
- [Usage Guide](#usage-guide)
- [Development](#development)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### Core Functionality
- **User Authentication & Management**: Secure user registration, login, and profile management
- **Session Management**: Create, manage, and track measurement sessions
- **Real-time Data Collection**: Receive data from LIWANAG measurement devices via API
- **Multi-point Measurements**: Support for 12 foot measurement points (6 per foot)
- **Data Visualization**: Interactive charts for VPT trends and vital signs
- **Session Protocols**: Pre-defined measurement protocols for different assessment types

### Medical Assessment Features
- **VPT Testing**: Vibration Perception Threshold voltage measurements
- **Temperature Monitoring**: Foot temperature tracking in Celsius
- **SpO2 Measurements**: Blood oxygen saturation monitoring
- **Plantar Pressure Assessment**: Automated status determination (Low/Normal/High)
- **Progress Tracking**: Session completion progress and missing point identification

### Data Management
- **Export Functionality**: Export session data as CSV files
- **Session History**: Complete history of all user sessions
- **Data Validation**: Automatic validation of measurement ranges
- **Quality Scoring**: Data quality assessment based on completeness and validity

### Web Interface
- **Responsive Design**: Mobile-friendly interface for all devices
- **Dashboard**: Comprehensive overview of user data and statistics
- **Profile Management**: User profile updates and password changes
- **Avatar Generation**: Automatic profile picture generation based on usernames

## 🔧 System Requirements

### Software Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Database**: SQLite (default) or PostgreSQL (production)
- **Web Browser**: Modern browser with JavaScript support

### Hardware Requirements
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 1GB free space
- **Network**: Internet connection for device communication

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/BitMantis01/LiwanagWebsiteFlask
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables
Create a `.env` file in the project root:
```env
SECRET_KEY=your_super_secret_key_here
DATABASE_URL=sqlite:///liwanag.db
API_KEY=LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
FLASK_ENV=development
FLASK_APP=app.py
```

### 5. Initialize Database
```bash
python -c "from app import app, create_tables; app.app_context().push(); create_tables()"
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `SECRET_KEY` | Flask secret key for sessions | Auto-generated |
| `DATABASE_URL` | Database connection string | `sqlite:///liwanag.db` |
| `API_KEY` | API key for device authentication | `LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH` |
| `FLASK_ENV` | Flask environment mode | `production` |
| `FLASK_APP` | Flask application entry point | `app.py` |

### Database Configuration
- **SQLite** (Development): Automatic setup, no additional configuration required
- **PostgreSQL** (Production): Update `DATABASE_URL` with PostgreSQL connection string

### API Configuration
The system uses API keys for device authentication. The default API key is created automatically on first run.

## 🏃‍♂️ Running the Application

### Development Mode
```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Run the application
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode
```bash
# Using Gunicorn (recommended for production)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 📚 API Documentation

### Authentication
All API endpoints require authentication via API key in the header:
```http
X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
```

### Core Endpoints

#### POST /api/data
Receive measurement data from LIWANAG device.

**Request Body:**
```json
{
    "user_id": 1,
    "session_id": 1,
    "vpt": 5.2,
    "temp": 31.2,
    "spo2": 98,
    "toe": "Right Heel"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Data received successfully",
    "measurement_id": 123,
    "session_id": 1,
    "timestamp": "2025-08-21T10:30:00Z"
}
```

#### POST /api/data-json-send
Alternative endpoint for sensor data reception.

**Request Body:**
```json
{
    "vpt": 5.2,
    "temp": 31.2,
    "spo2": 98,
    "toe": "Right Heel",
    "username": "patient001"
}
```

#### POST /api/session/complete
Mark a session as completed.

**Request Body:**
```json
{
    "session_id": 1,
    "plantar_pressure_status": "Normal"
}
```

#### GET /api/users/{user_id}/sessions
Retrieve all sessions for a specific user.

**Response:**
```json
{
    "sessions": [
        {
            "id": 1,
            "session_name": "Morning Assessment",
            "status": "completed",
            "created_at": "2025-08-21T10:00:00Z",
            "measurement_count": 12
        }
    ]
}
```

### Dashboard API Endpoints

#### GET /api/chart-data
Get chart data for visualization (requires login).

**Parameters:**
- `days`: Number of days of data to retrieve (default: 7)

#### GET /api/current-vpt-readings
Get current VPT readings for both feet (requires login).

#### GET /api/current-vitals-readings
Get current temperature and SpO2 readings (requires login).

## 📁 Project Structure

```
RalphWebsite/
├── app.py                  # Main Flask application
├── models.py              # Database models and schemas
├── forms.py               # WTForms for user input validation
├── utils.py               # Utility functions (avatar generation, etc.)
├── requirements.txt       # Python dependencies
├── quick_test.py         # Quick testing script
├── test_api.py           # API testing utilities
├── .env                  # Environment variables (create this)
├── README.md             # This file
├── static/               # Static assets
│   ├── css/             # Stylesheets
│   │   ├── style.css    # Main stylesheet
│   │   ├── auth.css     # Authentication page styles
│   │   └── dashboard.css # Dashboard styles
│   └── js/              # JavaScript files
│       ├── script.js    # Main JavaScript
│       └── dashboard.js # Dashboard functionality
└── templates/           # Jinja2 templates
    ├── base.html       # Base template
    ├── index.html      # Landing page
    ├── auth/          # Authentication templates
    │   ├── login.html
    │   └── register.html
    └── dashboard/     # Dashboard templates
        ├── base.html
        ├── dashboard.html
        ├── profile.html
        ├── my_data.html
        ├── history.html
        ├── new_session.html
        ├── session_detail.html
        └── change_password.html
```

## 🗄️ Database Schema

### Users Table
- **id**: Primary key
- **username**: Unique username (indexed)
- **password_hash**: Bcrypt hashed password
- **first_name**, **surname**, **middle_initial**: User's full name
- **hospital_name**, **hospital_room_no**: Hospital information
- **profile_picture**: Base64 encoded avatar
- **created_at**, **last_login**: Timestamps
- **is_active**: Account status
- **remember_token**: For "remember me" functionality

### Sessions Table
- **id**: Primary key
- **user_id**: Foreign key to Users
- **session_name**: User-defined session name
- **session_type**: Type of session (manual, auto, template)
- **protocol**: Assessment protocol used
- **created_at**, **completed_at**: Session timestamps
- **status**: Session status (active, completed, cancelled, paused)
- **plantar_pressure_status**: Overall assessment result
- **notes**: Optional session notes
- **expected_points**: JSON array of expected measurement points

### Measurements Table
- **id**: Primary key
- **session_id**: Foreign key to Sessions
- **point_name**: Measurement location (e.g., "Right Heel")
- **vpt_voltage**: VPT measurement in volts
- **temperature**: Temperature in Celsius
- **spo2**: SpO2 percentage
- **timestamp**: Measurement timestamp
- **notes**: Optional measurement notes
- **is_valid**: Data validity flag
- **retry_count**: Number of retries for this measurement

### API Keys Table
- **id**: Primary key
- **key_name**: Human-readable key name
- **key_hash**: SHA-256 hash of the API key
- **is_active**: Key status
- **created_at**, **last_used**: Usage timestamps
- **usage_count**: Number of times key has been used

## 📖 Usage Guide

### For Healthcare Providers

#### 1. User Registration
1. Navigate to `/register`
2. Fill in patient information including hospital details
3. Create secure username and password
4. Complete registration and login

#### 2. Starting a New Session
1. Go to Dashboard → New Session
2. Choose assessment protocol:
   - **Diabetic Foot Screening**: Comprehensive 12-point assessment
   - **Quick Assessment**: 6-point basic screening
   - **Research Protocol**: Full measurement with all parameters
   - **Single Foot**: Right or left foot only
3. Name your session and start measurement

#### 3. Data Collection
1. Connect LIWANAG device to the system
2. Follow the protocol to measure each designated point
3. Device automatically sends data to the web application
4. Monitor real-time progress in the dashboard

#### 4. Reviewing Results
1. View live data in "My Data" section
2. Analyze trends with interactive charts
3. Export data as CSV for external analysis
4. Review session history for patient progress

### For Developers

#### 1. Adding New Measurement Points
Edit `models.py` to add new points to `MEASUREMENT_POINTS` dictionary:
```python
MEASUREMENT_POINTS = {
    'right': [
        'Right Heel',
        'Right New Point',  # Add new point here
        # ... existing points
    ]
}
```

#### 2. Creating Custom Protocols
Add new protocols to `SESSION_PROTOCOLS` in `models.py`:
```python
SESSION_PROTOCOLS['custom_protocol'] = {
    'name': 'Custom Assessment',
    'description': 'Custom protocol description',
    'points': ['Right Heel', 'Left Heel'],
    'required_measurements': ['vpt_voltage'],
    'optional_measurements': ['temperature', 'spo2'],
    'estimated_duration': 5
}
```

#### 3. API Integration
Use the provided API endpoints to integrate with external systems:
```python
import requests

# Send measurement data
data = {
    'vpt': 5.2,
    'temp': 31.2,
    'spo2': 98,
    'toe': 'Right Heel',
    'username': 'patient001'
}

response = requests.post(
    'http://localhost:5000/api/data-json-send',
    json=data,
    headers={'X-API-Key': 'your_api_key'}
)
```

## 🔧 Development

### Setting Up Development Environment
1. Follow installation steps above
2. Set `FLASK_ENV=development` in `.env`
3. Enable debug mode for hot reloading

### Code Style
- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Comment complex logic thoroughly

### Testing
Run the test suite:
```bash
python test_api.py
```

For quick testing of specific functionality:
```bash
python quick_test.py
```

### Database Migrations
For schema changes:
1. Modify models in `models.py`
2. Create backup of existing database
3. Run migration script or recreate database for development

## 🚀 Deployment

### Production Deployment

#### 1. Environment Setup
```bash
# Production environment variables
export FLASK_ENV=production
export SECRET_KEY="your-super-secret-production-key"
export DATABASE_URL="postgresql://user:pass@localhost/liwanag_prod"
```

#### 2. Using Gunicorn
```bash
# Install Gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 3. Using Docker (Optional)
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### 4. Nginx Configuration
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Considerations
- Change default API keys in production
- Use HTTPS for all communications
- Implement rate limiting for API endpoints
- Regular security updates and monitoring
- Secure database with proper authentication

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Commit your changes: `git commit -m 'Add some feature'`
5. Push to the branch: `git push origin feature-name`
6. Submit a pull request

### Coding Standards
- Write unit tests for new features
- Update documentation for any API changes
- Follow existing code style and conventions
- Ensure backward compatibility when possible

### Bug Reports
When reporting bugs, please include:
- Python version and operating system
- Steps to reproduce the issue
- Expected vs. actual behavior
- Any error messages or logs

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

### Common Issues

#### Database Connection Errors
- Ensure database file permissions are correct
- Check DATABASE_URL environment variable
- Verify SQLite installation

#### API Authentication Failures
- Verify API key is correctly set in headers
- Check API key is active in database
- Ensure key format matches expected pattern

#### Device Communication Issues
- Verify network connectivity
- Check API endpoint URLs
- Validate JSON data format

### Getting Help
- Review this documentation thoroughly
- Check the issues section for similar problems
- Contact the development team for technical support

### Performance Optimization
- Use PostgreSQL for production databases
- Implement database indexing for large datasets
- Consider Redis for session storage in high-traffic environments
- Monitor memory usage and optimize queries as needed

---

**Version**: 1.0.0  
**Last Updated**: August 21, 2025  
**Developed for**: LIWANAG Diabetic Foot Assessment System
