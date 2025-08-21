#!/usr/bin/env python3
"""
Quick API Test - Auto Data Generator
Quickly generates test data for LIWANAG API without user interaction
"""

import requests
import json
import random
import time
from datetime import datetime

# Configuration
API_BASE_URL = "http://localhost:5000/api"
API_KEY = "LIWANAG_API_KEY_2025_SECURE_DEVICE_AUTH"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Measurement points
POINTS = [
    "Right Heel", "Right In Step", "Right 5th MT", "Right 3rd MT", "Right 1st MT", "Right Big Toe",
    "Left Heel", "Left In Step", "Left 5th MT", "Left 3rd MT", "Left 1st MT", "Left Big Toe"
]

def generate_measurement():
    """Generate realistic measurement data"""
    return {
        "vpt": round(random.uniform(2.0, 20.0), 1),
        "temp": round(random.uniform(29.0, 35.0), 1), 
        "spo2": random.randint(90, 100),
        "toe": random.choice(POINTS),
        "username": "bitmantis"  # Change this to your test username
    }

def send_measurement():
    """Send a single measurement"""
    data = generate_measurement()
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/data-json-send",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ {data['toe']}: VPT={data['vpt']}V, Temp={data['temp']}°C, SpO2={data['spo2']}%")
            return result.get('session_id')
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def quick_test(count=10):
    """Send multiple measurements quickly"""
    print(f"🚀 Sending {count} quick measurements...")
    
    for i in range(count):
        print(f"  {i+1}/{count}: ", end="")
        send_measurement()
        time.sleep(0.5)  # Small delay
    
    print("✅ Quick test completed!")

def full_foot_scan():
    """Simulate a complete foot scan"""
    print("🦶 Performing full foot scan...")
    
    session_id = None
    for point in POINTS:
        data = generate_measurement()
        data['toe'] = point  # Use specific point
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/data-json-send",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                if session_id is None:
                    session_id = result.get('session_id')
                print(f"  ✅ {point}: VPT={data['vpt']}V")
            else:
                print(f"  ❌ {point}: Error {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ {point}: {e}")
        
        time.sleep(0.3)
    
    # Complete the session
    if session_id:
        complete_session(session_id)

def complete_session(session_id):
    """Mark session as complete"""
    data = {
        "session_id": session_id,
        "plantar_pressure_status": random.choice(["Low", "Normal", "High"])
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/session/complete",
            headers=headers,
            json=data
        )
        
        if response.status_code == 200:
            print(f"  ✅ Session {session_id} completed with status: {data['plantar_pressure_status']}")
        else:
            print(f"  ❌ Failed to complete session: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Error completing session: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "quick":
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            quick_test(count)
        elif sys.argv[1] == "scan":
            full_foot_scan()
        elif sys.argv[1] == "single":
            send_measurement()
        else:
            print("Usage:")
            print("  python quick_test.py quick [count] - Send quick measurements")
            print("  python quick_test.py scan          - Full foot scan")
            print("  python quick_test.py single        - Single measurement")
    else:
        print("🎯 LIWANAG Quick API Test")
        print("=" * 30)
        quick_test(5)
        print()
        full_foot_scan()
        print("\n🎉 All tests completed!")
        print("Visit http://localhost:5000/login to view data")
