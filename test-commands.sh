#!/bin/bash
# Test commands for Assignment 2 - Task Manager API
BASE_URL="http://localhost:5001"

echo "=== Testing Category Endpoints ==="

echo -e "\n--- POST /categories (create Work) ---"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work", "color": "#FF5733"}' | python3 -m json.tool

echo -e "\n--- POST /categories (create Personal) ---"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Personal", "color": "#33FF57"}' | python3 -m json.tool

echo -e "\n--- POST /categories (duplicate name - should fail) ---"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Work"}' | python3 -m json.tool

echo -e "\n--- POST /categories (bad color - should fail) ---"
curl -s -X POST "$BASE_URL/categories" \
  -H "Content-Type: application/json" \
  -d '{"name": "Health", "color": "red"}' | python3 -m json.tool

echo -e "\n--- GET /categories ---"
curl -s "$BASE_URL/categories" | python3 -m json.tool

echo -e "\n--- GET /categories/1 ---"
curl -s "$BASE_URL/categories/1" | python3 -m json.tool

echo -e "\n=== Testing Task Endpoints ==="

echo -e "\n--- POST /tasks (create task with category) ---"
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Finish report", "description": "Complete the quarterly report", "category_id": 1}' | python3 -m json.tool

echo -e "\n--- POST /tasks (create task with due date soon - triggers notification) ---"
# Due in 1 hour from now
DUE_SOON=$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) + timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Urgent task\", \"due_date\": \"$DUE_SOON\", \"category_id\": 1}" | python3 -m json.tool

echo -e "\n--- POST /tasks (create task with far due date - no notification) ---"
DUE_FAR=$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) + timedelta(days=7)).strftime('%Y-%m-%dT%H:%M:%SZ'))")
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"Later task\", \"due_date\": \"$DUE_FAR\", \"category_id\": 2}" | python3 -m json.tool

echo -e "\n--- POST /tasks (validation error - no title) ---"
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"description": "Missing title"}' | python3 -m json.tool

echo -e "\n--- POST /tasks (validation error - title too long) ---"
LONG_TITLE=$(python3 -c "print('A' * 101)")
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d "{\"title\": \"$LONG_TITLE\"}" | python3 -m json.tool

echo -e "\n--- POST /tasks (bad category_id) ---"
curl -s -X POST "$BASE_URL/tasks" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test", "category_id": 999}' | python3 -m json.tool

echo -e "\n--- GET /tasks ---"
curl -s "$BASE_URL/tasks" | python3 -m json.tool

echo -e "\n--- GET /tasks?completed=false ---"
curl -s "$BASE_URL/tasks?completed=false" | python3 -m json.tool

echo -e "\n--- GET /tasks/1 ---"
curl -s "$BASE_URL/tasks/1" | python3 -m json.tool

echo -e "\n--- GET /tasks/999 (not found) ---"
curl -s "$BASE_URL/tasks/999" | python3 -m json.tool

echo -e "\n--- PUT /tasks/1 (mark completed) ---"
curl -s -X PUT "$BASE_URL/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{"completed": true}' | python3 -m json.tool

echo -e "\n--- GET /tasks?completed=true ---"
curl -s "$BASE_URL/tasks?completed=true" | python3 -m json.tool

echo -e "\n--- GET /categories (should show task counts) ---"
curl -s "$BASE_URL/categories" | python3 -m json.tool

echo -e "\n--- GET /categories/1 (should show tasks) ---"
curl -s "$BASE_URL/categories/1" | python3 -m json.tool

echo -e "\n--- DELETE /categories/1 (should fail - has tasks) ---"
curl -s -X DELETE "$BASE_URL/categories/1" | python3 -m json.tool

echo -e "\n--- DELETE /tasks/1 ---"
curl -s -X DELETE "$BASE_URL/tasks/1" | python3 -m json.tool

echo -e "\n--- DELETE /tasks/999 (not found) ---"
curl -s -X DELETE "$BASE_URL/tasks/999" | python3 -m json.tool

echo -e "\nDone!"
