"""Tests for POST /expenses and GET /expenses endpoints."""


class TestCreateExpense:
    """POST /expenses"""

    def test_create_expense_success(self, client):
        """Happy path: valid expense is created and returned with an id."""
        payload = {
            "amount": 42.50,
            "category": "Food",
            "note": "Lunch at cafe",
            "date": "2025-09-15",
        }
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] is not None
        assert data["amount"] == 42.50
        assert data["category"] == "food"  # lowercased
        assert data["note"] == "Lunch at cafe"
        assert data["date"] == "2025-09-15"

    def test_create_expense_negative_amount(self, client):
        """Amount must be > 0."""
        payload = {"amount": -10, "category": "Food", "date": "2025-09-15"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_zero_amount(self, client):
        """Amount must be > 0, not just >= 0."""
        payload = {"amount": 0, "category": "Food", "date": "2025-09-15"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_missing_category(self, client):
        """Category is required."""
        payload = {"amount": 10, "date": "2025-09-15"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_blank_category(self, client):
        """Category must not be blank (whitespace-only)."""
        payload = {"amount": 10, "category": "   ", "date": "2025-09-15"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_missing_date(self, client):
        """Date is required."""
        payload = {"amount": 10, "category": "Food"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_invalid_date_format(self, client):
        """Date must be YYYY-MM-DD."""
        payload = {"amount": 10, "category": "Food", "date": "15-09-2025"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 422

    def test_create_expense_note_optional(self, client):
        """Note is optional — omitting it should work fine."""
        payload = {"amount": 25, "category": "Transport", "date": "2025-09-15"}
        resp = client.post("/expenses", json=payload)
        assert resp.status_code == 201
        assert resp.json()["note"] is None


class TestListExpenses:
    """GET /expenses"""

    def _seed(self, client):
        """Helper to insert a few expenses."""
        expenses = [
            {"amount": 100, "category": "Food", "date": "2025-08-01"},
            {"amount": 200, "category": "Transport", "date": "2025-08-15"},
            {"amount": 50, "category": "Food", "date": "2025-09-01"},
            {"amount": 75, "category": "Entertainment", "date": "2025-09-10"},
        ]
        for e in expenses:
            resp = client.post("/expenses", json=e)
            assert resp.status_code == 201

    def test_list_all(self, client):
        """Returns all expenses when no filters are applied."""
        self._seed(client)
        resp = client.get("/expenses")
        assert resp.status_code == 200
        assert len(resp.json()) == 4

    def test_list_empty(self, client):
        """Returns empty list when no expenses exist."""
        resp = client.get("/expenses")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_filter_by_category(self, client):
        """Filter by category returns only matching expenses."""
        self._seed(client)
        resp = client.get("/expenses", params={"category": "food"})
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(e["category"] == "food" for e in data)

    def test_filter_by_category_case_insensitive(self, client):
        """Category filter is case-insensitive."""
        self._seed(client)
        resp = client.get("/expenses", params={"category": "FOOD"})
        assert resp.status_code == 200
        assert len(resp.json()) == 2

    def test_filter_by_date_range(self, client):
        """Filter by date range returns expenses within bounds (inclusive)."""
        self._seed(client)
        resp = client.get(
            "/expenses",
            params={"start_date": "2025-09-01", "end_date": "2025-09-30"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        for e in data:
            assert e["date"] >= "2025-09-01"

    def test_filter_invalid_date_range(self, client):
        """start_date > end_date should return 400."""
        resp = client.get(
            "/expenses",
            params={"start_date": "2025-09-30", "end_date": "2025-09-01"},
        )
        assert resp.status_code == 400

    def test_filter_combined(self, client):
        """Combining category + date range filters."""
        self._seed(client)
        resp = client.get(
            "/expenses",
            params={
                "category": "food",
                "start_date": "2025-09-01",
                "end_date": "2025-09-30",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["category"] == "food"
        assert data[0]["amount"] == 50
