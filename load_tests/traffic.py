import csv
import random
import string
from pathlib import Path

from locust import HttpUser, task


class UrlShortenerUser(HttpUser):
    # Cache loaded CSV data once per process
    short_codes = []
    user_ids = []

    @classmethod
    def _load_urls_csv(cls):
        if cls.short_codes:
            return

        csv_path = Path(__file__).resolve().parents[1] / "app" / "assets" / "urls.csv"
        with csv_path.open(newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                is_active_raw = (row.get("is_active") or "").strip().lower()
                is_active = is_active_raw in {"true", "1", "yes", "y", "on"}

                shortcode = (row.get("short_code") or "").strip()
                # Redirect endpoint returns 404 for inactive shortcodes.
                if shortcode and is_active:
                    cls.short_codes.append(shortcode)

                user_id_raw = (row.get("user_id") or "").strip()
                if user_id_raw.isdigit():
                    cls.user_ids.append(int(user_id_raw))

        # Safety fallback so create task can still run
        if not cls.user_ids:
            cls.user_ids = [1]

    def on_start(self):
        self._load_urls_csv()

    @task(8)
    def redirect_existing_short_code(self):
        shortcode = random.choice(self.short_codes)
        # Do not follow to external target URLs; we only measure app redirect behavior.
        self.client.get(f"/{shortcode}", name="/<shortcode>", allow_redirects=False)

    @task(1)
    def create_url(self):
        user_id = random.choice(self.user_ids)
        suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
        payload = {
            "user_id": user_id,
            "original_url": f"https://loadtest.example/{suffix}",
            "title": f"Load test {suffix}",
        }
        self.client.post("/urls", json=payload, name="POST /urls")

    @task(1)
    def list_urls(self):
        self.client.get("/urls", name="GET /urls")
