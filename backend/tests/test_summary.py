"""Tests for GET /summary endpoint."""


class TestSummary:
    """GET /summary"""

    def _seed(self, client, expenses):
        for e in expenses:
            resp = client.post("/expenses", json=e)
            assert resp.status_code == 201

    def test_summary_empty(self, client):
        """Summary with no expenses returns zeroes and empty lists."""
        resp = client.get("/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_spend"] == 0.0
        assert data["by_category"] == []
        assert data["month_over_month"] == []
        assert data["alerts"] == []

    def test_summary_totals(self, client):
        """Total spend and by_category are calculated correctly."""
        self._seed(
            client,
            [
                {"amount": 100, "category": "Food", "date": "2025-08-01"},
                {"amount": 200, "category": "Transport", "date": "2025-08-15"},
                {"amount": 50, "category": "Food", "date": "2025-09-01"},
            ],
        )
        resp = client.get("/summary")
        data = resp.json()

        assert data["total_spend"] == 350.0

        cats = {c["category"]: c["total"] for c in data["by_category"]}
        assert cats["food"] == 150.0
        assert cats["transport"] == 200.0

    def test_month_over_month(self, client):
        """Month-over-month correctly computes percentage changes."""
        self._seed(
            client,
            [
                {"amount": 100, "category": "Food", "date": "2025-07-01"},
                {"amount": 200, "category": "Food", "date": "2025-08-01"},
                {"amount": 150, "category": "Food", "date": "2025-09-01"},
            ],
        )
        resp = client.get("/summary")
        data = resp.json()

        mom = data["month_over_month"]
        assert len(mom) == 3

        # First month has no change
        assert mom[0]["month"] == "2025-07"
        assert mom[0]["change_pct"] is None

        # Second month: (200 - 100) / 100 = 100%
        assert mom[1]["month"] == "2025-08"
        assert mom[1]["change_pct"] == 100.0

        # Third month: (150 - 200) / 200 = -25%
        assert mom[2]["month"] == "2025-09"
        assert mom[2]["change_pct"] == -25.0

    def test_alert_fires_on_spike(self, client):
        """An alert is generated when a category's spend increases >20% month-over-month."""
        self._seed(
            client,
            [
                # Food: Aug = 100, Sep = 200 → 100% increase → alert
                {"amount": 100, "category": "Food", "date": "2025-08-01"},
                {"amount": 200, "category": "Food", "date": "2025-09-01"},
                # Transport: Aug = 100, Sep = 110 → 10% increase → no alert
                {"amount": 100, "category": "Transport", "date": "2025-08-15"},
                {"amount": 110, "category": "Transport", "date": "2025-09-15"},
            ],
        )
        resp = client.get("/summary")
        data = resp.json()
        alerts = data["alerts"]

        assert len(alerts) == 1
        assert alerts[0]["category"] == "food"
        assert alerts[0]["change_pct"] == 100.0

    def test_no_alert_when_spend_decreases(self, client):
        """No alert when spending decreases."""
        self._seed(
            client,
            [
                {"amount": 200, "category": "Food", "date": "2025-08-01"},
                {"amount": 100, "category": "Food", "date": "2025-09-01"},
            ],
        )
        resp = client.get("/summary")
        data = resp.json()
        assert data["alerts"] == []

    def test_no_alert_single_month(self, client):
        """No alerts when there's only one month of data."""
        self._seed(
            client,
            [
                {"amount": 500, "category": "Food", "date": "2025-09-01"},
            ],
        )
        resp = client.get("/summary")
        data = resp.json()
        assert data["alerts"] == []
