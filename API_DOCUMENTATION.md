# 🩺 LIWANAG API Documentation

## Overview

The LIWANAG Flask application is a **medical device data collection system** for diabetic foot monitoring. It collects and analyzes sensor data from measurement devices to help healthcare professionals monitor patient health.

### Measured Parameters
- **VPT (Vibration Perception Threshold)** - measured in volts (0-50V)
- **Temperature** - measured in Celsius (25-45°C)  
- **SpO2 (Blood Oxygen Saturation)** - measured as percentage (70-100%)

---

## 🔐 Authentication

All API endpoints require **API Key authentication** using the header:

```
X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
```

---

## 📡 API Endpoints

### 1. Send Measurement Data

**Endpoint:** `POST /api/data-json-send`

**Purpose:** Receives sensor data from measurement devices

**Headers:**
```
Content-Type: application/json
X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
```

**Request Body:**
```json
{
    "vpt": 5.2,           // Voltage reading (0-50V)
    "temp": 31.5,         // Temperature in Celsius (25-45°C) 
    "spo2": 98,           // SpO2 percentage (70-100%)
    "toe": "Right Heel",  // Measurement location (see valid locations below)
    "username": "patient123"  // Patient username (must exist in system)
}
```

**Success Response (201):**
```json
{
    "success": true,
    "message": "Sensor data received successfully",
    "measurement_id": 123,
    "point_name": "Right Heel",
    "data": {
        "vpt": 5.2,
        "temperature": 31.5,
        "spo2": 98,
        "timestamp": "2025-08-22T10:30:45.123456"
    }
}
```

**Error Responses:**
- `400` - Missing required fields or invalid data format
- `401` - Missing or invalid API key
- `404` - User not found
- `500` - Internal server error

---

### 2. Get User Measurements

**Endpoint:** `GET /api/users/{user_id}/measurements`

**Purpose:** Retrieve all measurements for a specific user

**Headers:**
```
X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
```

**Success Response (200):**
```json
{
    "measurements": [
        {
            "id": 123,
            "user_id": 1,
            "point_name": "Right Heel",
            "vpt_voltage": 5.2,
            "temperature": 31.5,
            "spo2": 98,
            "timestamp": "2025-08-22T10:30:45.123456",
            "notes": null,
            "is_valid": true,
            "quality_score": 100
        }
    ]
}
```

---

### 3. Legacy Data Endpoint

**Endpoint:** `POST /api/data`

**Purpose:** Alternative endpoint for backward compatibility

**Request Body:**
```json
{
    "user_id": 1,
    "vpt": 5,
    "temp": 31.2,
    "spo2": 98,
    "toe": "Right Heel"
}
```

---

## 📍 Valid Measurement Points

The system accepts these specific foot measurement locations:

### Right Foot
- `Right Heel`
- `Right In Step`
- `Right 5th MT`
- `Right 3rd MT`
- `Right 1st MT`
- `Right Big Toe`

### Left Foot
- `Left Heel`
- `Left In Step`
- `Left 5th MT`
- `Left 3rd MT`
- `Left 1st MT`
- `Left Big Toe`

**Note:** MT = Metatarsal

---

## 💻 Code Examples

### Using cURL

```bash
curl -X POST http://localhost:2214/api/data-json-send \
  -H "Content-Type: application/json" \
  -H "X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH" \
  -d '{
    "vpt": 7.3,
    "temp": 32.1,
    "spo2": 97,
    "toe": "Right Big Toe",
    "username": "testuser"
  }'
```

### Using Python

```python
import requests
import json

# Configuration
url = "http://localhost:2214/api/data-json-send"
headers = {
    "Content-Type": "application/json",
    "X-API-Key": "LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH"
}

# Measurement data
data = {
    "vpt": 6.8,
    "temp": 30.9,
    "spo2": 99,
    "toe": "Left Heel",
    "username": "patient123"
}

# Send request
response = requests.post(url, headers=headers, data=json.dumps(data))

# Handle response
if response.status_code == 201:
    result = response.json()
    print(f"✅ Success! Measurement ID: {result['measurement_id']}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const url = 'http://localhost:2214/api/data-json-send';
const headers = {
    'Content-Type': 'application/json',
    'X-API-Key': 'LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH'
};

const data = {
    vpt: 5.5,
    temp: 31.8,
    spo2: 96,
    toe: 'Right 1st MT',
    username: 'patient123'
};

axios.post(url, data, { headers })
    .then(response => {
        console.log('✅ Success:', response.data);
    })
    .catch(error => {
        console.error('❌ Error:', error.response?.data || error.message);
    });
```

---

## 🧪 Testing the API

### Using the Test Script

The project includes a comprehensive test script (`test_api.py`):

```bash
# Run all tests
python test_api.py

# Check server health only
python test_api.py health

# Test single measurement
python test_api.py single

# Generate sample data
python test_api.py data

# Run stress test
python test_api.py stress
```

### Manual Testing Steps

1. **Start the Flask server:**
   ```bash
   python app.py
   ```

2. **Create a test user:**
   - Visit: `http://localhost:2214/register`
   - Create account with username: `testuser`

3. **Send test measurement:**
   ```bash
   curl -X POST http://localhost:2214/api/data-json-send \
     -H "Content-Type: application/json" \
     -H "X-API-Key: LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH" \
     -d '{"vpt": 5.0, "temp": 32.0, "spo2": 98, "toe": "Right Heel", "username": "testuser"}'
   ```

4. **View results:**
   - Login at: `http://localhost:2214/login`
   - Check dashboard: `http://localhost:2214/dashboard`

---

## 🌐 Web Dashboard Access

After sending data via API, users can view results through the web interface:

| Page | URL | Description |
|------|-----|-------------|
| **Login** | `/login` | User authentication |
| **Dashboard** | `/dashboard` | Overview and recent measurements |
| **Data Charts** | `/my-data` | Visual charts and graphs |
| **History** | `/history` | Measurement history timeline |
| **Profile** | `/profile` | User profile management |

---

## 📊 Data Validation

The system automatically validates incoming data:

### VPT Voltage (0-50V)
- **Normal:** 0-8V
- **Elevated:** 8-15V  
- **High:** 15V+

### Temperature (25-45°C)
- **Normal:** 29-33°C
- **Fever:** 33-37°C+

### SpO2 (70-100%)
- **Excellent:** 98-100%
- **Good:** 95-97%
- **Poor:** 90-94%
- **Critical:** <90%

Invalid data will be flagged but still stored for review.

---

## 🔧 Server Configuration

### Default Settings
- **Host:** `0.0.0.0` (all interfaces)
- **Port:** `2214`
- **Database:** SQLite (`instance/liwanag.db`)
- **Environment:** Development

### Environment Variables
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///liwanag.db
API_KEY=LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH
```

---

## 🚨 Error Handling

### Common Error Codes

| Code | Description | Solution |
|------|-------------|----------|
| `400` | Bad Request - Missing/invalid data | Check required fields and data format |
| `401` | Unauthorized - Invalid API key | Verify API key in request header |
| `404` | Not Found - User doesn't exist | Create user account first |
| `500` | Internal Server Error | Check server logs |

### Example Error Response
```json
{
    "error": "Missing required field: username",
    "success": false
}
```

---

## 📈 Data Export

### Export User Measurements
**Endpoint:** `GET /api/measurements/export`

Returns CSV file with all user measurements (requires login).

### Export Single Measurement
**Endpoint:** `GET /api/measurements/{id}/export`

Returns CSV file for specific measurement.

---

## 🔒 Security Features

- **API Key Authentication** - All endpoints protected
- **User Authentication** - Web interface requires login
- **Data Validation** - Input sanitization and range checking
- **CSRF Protection** - Forms protected against cross-site attacks
- **Password Hashing** - Bcrypt encryption for user passwords

---

## 📝 Changelog

### Version 1.0
- Initial API implementation
- Basic measurement data collection
- Web dashboard interface
- User authentication system
- Data validation and export features

---

## 📞 Support

For technical support or questions about this API:

1. Check the test script output for common issues
2. Verify server is running on correct port
3. Ensure API key is correctly configured
4. Check user exists in system before sending data

**Server Health Check:** `http://localhost:2214/`
