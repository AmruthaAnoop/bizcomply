#!/bin/bash

# Test 1: Send a test alert to Alertmanager
echo "Sending test alert to Alertmanager..."
curl -X POST http://localhost:9093/api/v2/alerts -d '
[{
  "status": "firing",
  "labels": {
    "alertname": "TestAlert",
    "service": "test-service",
    "severity":"warning",
    "instance": "test-instance"
  },
  "annotations": {
    "summary": "This is a test alert",
    "description": "This is a test alert to verify the notification setup"
  },
  "generatorURL": "http://prometheus:9090/graph?g0.expr=up+%3D%3D+0&g0.tab=1"
}]'

echo -e "\nTest alert sent. Check your email and Slack for notifications."
echo "Alertmanager UI: http://localhost:9093"
echo "Prometheus Alerts: http://localhost:9090/alerts"

# Test 2: Check Prometheus alert rules
echo -e "\nChecking Prometheus alert rules..."
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[].name'

# Test 3: Check Alertmanager status
echo -e "\nChecking Alertmanager status..."
curl -s http://localhost:9093/api/v2/status | jq
