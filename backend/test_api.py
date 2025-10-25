"""Simple API tests for CodeXray"""

import requests
import time

BASE_URL = "http://localhost:5050/api"

def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print("✅ Health check passed")

def test_register_and_login():
    """Test registration and login"""
    # Register
    register_data = {
        "username": f"testuser_{int(time.time())}",
        "password": "testpass123"
    }
    
    response = requests.post(f"{BASE_URL}/register", json=register_data)
    assert response.status_code == 200
    print("✅ Registration successful")
    
    # Login
    response = requests.post(f"{BASE_URL}/login", json=register_data)
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    print("✅ Login successful")
    
    return data["token"]

def test_authenticated_endpoints(token):
    """Test endpoints requiring authentication"""
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test metrics
    response = requests.get(f"{BASE_URL}/metrics", headers=headers)
    assert response.status_code == 200
    print("✅ Metrics endpoint working")
    
    # Test summary
    response = requests.get(f"{BASE_URL}/summary", headers=headers)
    assert response.status_code == 200
    print("✅ Summary endpoint working")
    
    # Test alerts
    response = requests.get(f"{BASE_URL}/alerts", headers=headers)
    assert response.status_code == 200
    print("✅ Alerts endpoint working")

if __name__ == "__main__":
    print("🧪 Running API Tests...\n")
    
    try:
        test_health()
        token = test_register_and_login()
        
        # Wait for some metrics to be collected
        print("\n⏳ Waiting 10 seconds for metrics collection...")
        time.sleep(10)
        
        test_authenticated_endpoints(token)
        
        print("\n✅ All tests passed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")