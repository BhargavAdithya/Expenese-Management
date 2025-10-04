#!/bin/bash

echo "=========================================="
echo "Expense Management Backend Setup"
echo "=========================================="

# Step 1: Stop current server if running
echo "Step 1: Stopping any running servers..."
pkill -f "python3 app.py" 2>/dev/null
pkill -f "flask run" 2>/dev/null
sleep 2

# Step 2: Activate virtual environment
echo "Step 2: Activating virtual environment..."
source venv/bin/activate

# Step 3: Install missing dependencies
echo "Step 3: Installing dependencies..."
pip install requests werkzeug --quiet

# Step 4: Recreate database tables
echo "Step 4: Recreating database tables..."
python3 << EOF
from app import create_app, db

app = create_app()
with app.app_context():
    # Drop all tables and recreate
    db.drop_all()
    db.create_all()
    print("✓ Database tables recreated successfully!")
EOF

# Step 5: Start the server in background
echo "Step 5: Starting Flask server..."
python3 app.py &
SERVER_PID=$!
sleep 3

# Step 6: Test endpoints
echo ""
echo "=========================================="
echo "Testing API Endpoints"
echo "=========================================="

# Test health endpoint
echo "1. Testing Health Endpoint..."
curl -s http://localhost:5000/health | python3 -m json.tool

echo ""
echo ""

# Test root endpoint
echo "2. Testing Root Endpoint..."
curl -s http://localhost:5000/ | python3 -m json.tool

echo ""
echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo "Server is running on http://localhost:5000"
echo "Server PID: $SERVER_PID"
echo ""
echo "To stop the server: kill $SERVER_PID"
echo "To view logs: tail -f nohup.out"
echo ""
echo "Next steps:"
echo "1. Test signup: curl -X POST http://localhost:5000/api/auth/signup -H 'Content-Type: application/json' -d '{\"email\":\"admin@test.com\",\"password\":\"password123\",\"full_name\":\"Admin User\",\"country\":\"India\"}'"
echo "2. Test login after signup"
echo "3. Start implementing expense routes"
echo "=========================================="