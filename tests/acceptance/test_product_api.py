# tests/acceptance/test_product_api.py
import os
import time
import requests

BASE = os.getenv("PRODUCT_BASE_URL", "http://localhost:8000")

def wait_ready(timeout=60):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE}/", timeout=3)
            if r.status_code == 200:
                return
        except Exception:
            pass
        time.sleep(2)
    raise RuntimeError("Product API not ready")

def test_root():
    wait_ready()
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200
    assert "Welcome to the Product Service" in r.text

def test_create_list_delete_product():
    wait_ready()

    payload = {
        "name": "HD Test Product",
        "description": "for acceptance tests",
        "price": 9.99,
        "in_stock": True
    }
    # create
    r = requests.post(f"{BASE}/products/", json=payload)
    assert r.status_code in (200, 201)
    prod = r.json()
    prod_id = prod["id"]

    # list
    r = requests.get(f"{BASE}/products/")
    assert r.status_code == 200
    items = r.json()
    assert any(p["id"] == prod_id for p in items)

    # delete
    r = requests.delete(f"{BASE}/products/{prod_id}")
    assert r.status_code in (200, 204)
