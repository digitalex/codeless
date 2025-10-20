#!/bin/bash
echo "Starting backend server..."
python server.py > backend.log 2>&1 &
echo "Backend server started in the background. Logs are in backend.log"

echo "Starting frontend development server..."
cd frontend
npm run dev
