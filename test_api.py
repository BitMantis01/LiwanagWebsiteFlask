#!/usr/bin/env python3
"""
LIWANAG API Test Script
Tests the API endpoints and automatically generates test data for demonstration
"""

import requests
import json
import time
import random
from datetime import datetime, timezone
import sys

# Configuration
API_BASE_URL = "http://localhost:5000/api"
WEB_BASE_URL = "http://localhost:5000"
API_KEY = "LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH"

# Request headers
headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Measurement points for testing
MEASUREMENT_POINTS = [
    "Right Heel", "Right In Step", "Right 5th MT", "Right 3rd MT", "Right 1st MT", "Right Big Toe",
    "Left Heel", "Left In Step", "Left 5th MT", "Left 3rd MT", "Left 1st MT", "Left Big Toe"
]

class APITester:
    def __init__(self):
        self.session_counter = 1
        self.created_sessions = []
        
    def check_server_health(self):
        """Check if the Flask server is running"""
        try:
            response = requests.get(WEB_BASE_URL, timeout=5)
            if response.status_code == 200:
                print("✅ Server is running and accessible")
                return True
            else:
                print(f"❌ Server responded with status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to server. Make sure Flask app is running on http://localhost:5000")
            return False
        except requests.exceptions.Timeout:
            print("❌ Server connection timed out")
            return False
    
    def create_test_user(self):
        """Create a test user via the registration endpoint"""
        print("\n📝 Creating test user...")
        
        # First check if we can access the registration page
        try:
            reg_response = requests.get(f"{WEB_BASE_URL}/register")
            if reg_response.status_code != 200:
                print("❌ Cannot access registration page")
                return None
        except:
            print("❌ Failed to access registration page")
            return None
        
        print("ℹ️  Please create a test user manually by visiting: http://localhost:5000/register")
        print("   Use these test credentials:")
        print("   - Username: testuser")
        print("   - Password: TestPass123!")
        print("   - First Name: Test")
        print("   - Surname: User")
        print("   - Hospital: Test Hospital")
        print("   - Room: 101")
        
        input("Press Enter after creating the test user...")
        return "testuser"
    
    def generate_realistic_measurement(self, point_name):
        """Generate realistic measurement data for different foot points"""
        
        # Base values with realistic ranges
        base_values = {
            "vpt": {
                "normal_range": (2.0, 8.0),
                "elevated_range": (8.0, 15.0),
                "high_range": (15.0, 25.0)
            },
            "temp": {
                "normal_range": (29.0, 33.0),
                "fever_range": (33.0, 37.0)
            },
            "spo2": {
                "excellent_range": (98, 100),
                "good_range": (95, 97),
                "poor_range": (90, 94)
            }
        }
        
        # Simulate different conditions
        condition = random.choice(["normal", "mild_issue", "concerning"])
        
        if condition == "normal":
            vpt = round(random.uniform(*base_values["vpt"]["normal_range"]), 1)
            temp = round(random.uniform(*base_values["temp"]["normal_range"]), 1)
            spo2 = random.randint(*base_values["spo2"]["excellent_range"])
        elif condition == "mild_issue":
            vpt = round(random.uniform(*base_values["vpt"]["elevated_range"]), 1)
            temp = round(random.uniform(*base_values["temp"]["normal_range"]), 1)
            spo2 = random.randint(*base_values["spo2"]["good_range"])
        else:  # concerning
            vpt = round(random.uniform(*base_values["vpt"]["high_range"]), 1)
            temp = round(random.uniform(*base_values["temp"]["fever_range"]), 1)
            spo2 = random.randint(*base_values["spo2"]["poor_range"])
        
        return {
            "vpt": vpt,
            "temp": temp,
            "spo2": spo2,
            "toe": point_name,
            "username": "testuser"
        }
    
    def test_single_measurement(self):
        """Test sending a single measurement"""
        print("\n🧪 Testing single measurement...")
        
        measurement_data = self.generate_realistic_measurement("Right Heel")
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/data-json-send",
                headers=headers,
                data=json.dumps(measurement_data)
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Single measurement successful!")
                print(f"   Session ID: {result.get('session_id')}")
                print(f"   Measurement ID: {result.get('measurement_id')}")
                print(f"   Point: {result.get('point_name')}")
                print(f"   VPT: {result.get('data', {}).get('vpt')}V")
                print(f"   Temp: {result.get('data', {}).get('temperature')}°C")
                print(f"   SpO2: {result.get('data', {}).get('spo2')}%")
                return result.get('session_id')
            else:
                print(f"❌ Failed to send measurement: {response.status_code}")
                print(f"   Response: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ Error sending measurement: {str(e)}")
            return None
    
    def test_full_session(self, num_points=6):
        """Test a complete measurement session"""
        print(f"\n🔬 Testing full session with {num_points} measurement points...")
        
        session_id = None
        successful_measurements = 0
        
        # Select random measurement points
        selected_points = random.sample(MEASUREMENT_POINTS, num_points)
        
        for i, point in enumerate(selected_points):
            print(f"   📍 Measuring {point} ({i+1}/{num_points})...")
            
            measurement_data = self.generate_realistic_measurement(point)
            
            try:
                response = requests.post(
                    f"{API_BASE_URL}/data-json-send",
                    headers=headers,
                    data=json.dumps(measurement_data)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if session_id is None:
                        session_id = result.get('session_id')
                    successful_measurements += 1
                    print(f"      ✅ VPT: {result.get('data', {}).get('vpt')}V, "
                          f"Temp: {result.get('data', {}).get('temperature')}°C, "
                          f"SpO2: {result.get('data', {}).get('spo2')}%")
                else:
                    print(f"      ❌ Failed: {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Error: {str(e)}")
            
            # Small delay between measurements to simulate real device timing
            time.sleep(0.5)
        
        print(f"\n📊 Session completed: {successful_measurements}/{num_points} measurements successful")
        if session_id:
            self.created_sessions.append(session_id)
            return session_id
        return None
    
    def test_complete_session(self, session_id):
        """Test completing a session"""
        if not session_id:
            print("❌ No session ID provided for completion")
            return False
        
        print(f"\n✅ Completing session {session_id}...")
        
        # Determine status based on some logic (simulate device assessment)
        status_options = ["Low", "Normal", "High"]
        status = random.choice(status_options)
        
        completion_data = {
            "session_id": session_id,
            "plantar_pressure_status": status
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/session/complete",
                headers=headers,
                data=json.dumps(completion_data)
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Session completed successfully!")
                print(f"   Status: {status}")
                print(f"   Session details: {result.get('session', {}).get('session_name')}")
                return True
            else:
                print(f"❌ Failed to complete session: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error completing session: {str(e)}")
            return False
    
    def test_get_user_sessions(self, user_id=1):
        """Test getting user sessions"""
        print(f"\n📋 Getting sessions for user {user_id}...")
        
        try:
            response = requests.get(
                f"{API_BASE_URL}/users/{user_id}/sessions",
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                sessions = result.get('sessions', [])
                print(f"✅ Retrieved {len(sessions)} sessions")
                
                for session in sessions[-3:]:  # Show last 3 sessions
                    print(f"   📅 {session.get('session_name')} - "
                          f"Status: {session.get('status')} - "
                          f"Measurements: {session.get('measurement_count')}")
                return True
            else:
                print(f"❌ Failed to get sessions: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting sessions: {str(e)}")
            return False
    
    def run_stress_test(self, num_sessions=3):
        """Run a stress test with multiple sessions"""
        print(f"\n🏃‍♂️ Running stress test with {num_sessions} sessions...")
        
        successful_sessions = 0
        
        for i in range(num_sessions):
            print(f"\n--- Session {i+1}/{num_sessions} ---")
            
            # Create session with random number of points (4-12)
            num_points = random.randint(4, 12)
            session_id = self.test_full_session(num_points)
            
            if session_id:
                # Complete the session
                if self.test_complete_session(session_id):
                    successful_sessions += 1
            
            # Short delay between sessions
            time.sleep(1)
        
        print(f"\n🎯 Stress test completed: {successful_sessions}/{num_sessions} sessions successful")
    
    def generate_sample_data(self):
        """Generate comprehensive sample data for demonstration"""
        print("\n🎯 Generating comprehensive sample data...")
        
        # Create different types of sessions
        session_types = [
            {"name": "Morning Screening", "points": ["Right Heel", "Right Big Toe", "Left Heel", "Left Big Toe"]},
            {"name": "Full Assessment", "points": MEASUREMENT_POINTS[:8]},
            {"name": "Follow-up Check", "points": ["Right 1st MT", "Right 3rd MT", "Left 1st MT", "Left 3rd MT"]},
            {"name": "Diabetic Screening", "points": MEASUREMENT_POINTS},
        ]
        
        for session_type in session_types:
            print(f"\n📋 Creating {session_type['name']}...")
            
            session_id = None
            for point in session_type['points']:
                measurement_data = self.generate_realistic_measurement(point)
                
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/data-json-send",
                        headers=headers,
                        data=json.dumps(measurement_data)
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if session_id is None:
                            session_id = result.get('session_id')
                        print(f"   ✅ {point}: VPT={result.get('data', {}).get('vpt')}V")
                    
                except Exception as e:
                    print(f"   ❌ Error with {point}: {str(e)}")
                
                time.sleep(0.3)  # Simulate device timing
            
            # Complete the session
            if session_id:
                self.test_complete_session(session_id)
                time.sleep(1)
    
    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 LIWANAG API Testing Suite")
        print("=" * 50)
        
        # Check server health
        if not self.check_server_health():
            print("\nExiting: Server not accessible")
            return
        
        # Create test user (manual step)
        username = self.create_test_user()
        if not username:
            print("\nExiting: Could not set up test user")
            return
        
        print(f"\n🔧 Testing with user: {username}")
        
        # Run tests
        print("\n" + "=" * 50)
        print("RUNNING API TESTS")
        print("=" * 50)
        
        # Test single measurement
        session_id = self.test_single_measurement()
        
        # Test full session
        session_id = self.test_full_session(6)
        if session_id:
            self.test_complete_session(session_id)
        
        # Test getting user sessions
        self.test_get_user_sessions()
        
        # Generate sample data
        self.generate_sample_data()
        
        # Run stress test
        self.run_stress_test(2)
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS COMPLETED!")
        print("=" * 50)
        print(f"✅ Created {len(self.created_sessions)} sessions")
        print("🌐 Visit http://localhost:5000/login to view the dashboard")
        print("📊 Login with your test user to see the generated data")

def main():
    """Main function to run tests"""
    tester = APITester()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "health":
            tester.check_server_health()
        elif command == "single":
            if tester.check_server_health():
                tester.test_single_measurement()
        elif command == "session":
            if tester.check_server_health():
                session_id = tester.test_full_session()
                if session_id:
                    tester.test_complete_session(session_id)
        elif command == "stress":
            if tester.check_server_health():
                tester.run_stress_test(5)
        elif command == "data":
            if tester.check_server_health():
                tester.generate_sample_data()
        else:
            print("Available commands:")
            print("  health  - Check server health")
            print("  single  - Test single measurement")
            print("  session - Test full session")
            print("  stress  - Run stress test")
            print("  data    - Generate sample data")
            print("  (no args) - Run all tests")
    else:
        # Run all tests
        tester.run_all_tests()

if __name__ == "__main__":
    main()
