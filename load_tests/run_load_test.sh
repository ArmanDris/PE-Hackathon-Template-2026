docker compose up -d
docker compose exec web uv run locust --headless --users 50 --spawn-rate 1 -H http://localhost:5000 -f load_tests/traffic.py -t 30s
