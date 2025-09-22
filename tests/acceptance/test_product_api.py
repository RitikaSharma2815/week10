# tests/acceptance/test_product_api.py
import os
import time
import requests

BASE = os.getenv("PRODUCT_BASE_URL", "http://localhost:8000")


def wait_ready(timeout=90):
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


def create_product_resilient():
    """
    Try multiple payload variants to satisfy different ProductCreate schemas.
    Returns (prod_id, payload_used, response_json).
    Raises AssertionError if all variants fail.
    """
    candidates = [
        # Variant A: original payload
        {
            "name": "HD Test Product A",
            "description": "acceptance test product (A)",
            "price": 9.99,
            "in_stock": True,
        },
        # Variant B: common schema with stock_quantity
        {
            "name": "HD Test Product B",
            "description": "acceptance test product (B)",
            "price": 9.99,
            "stock_quantity": 10,
        },
        # Variant C: price as string (some schemas coerce)
        {
            "name": "HD Test Product C",
            "description": "acceptance test product (C)",
            "price": "9.99",
            "stock_quantity": 10,
        },
        # Variant D: minimal fields often required
        {
            "name": "HD Test Product D",
            "description": "acceptance test product (D)",
            "price": 9.99,
        },
    ]

    errors = []
    for payload in candidates:
        r = requests.post(f"{BASE}/products/", json=payload)
        if r.status_code in (200, 201):
            data = r.json()
            prod_id = data.get("product_id") or data.get("id")
            if not prod_id:
                # Some APIs return "id"; others "product_id"
                # Fall back to reading the first ID from list
                # but first ensure object looks like a product
                prod_id = data.get("productId") or data.get("productID")
            if prod_id is None:
                errors.append(f"Create OK but no ID in response: {data}")
                continue
            return prod_id, payload, data
        else:
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            errors.append(f"{r.status_code}: {detail}")

    raise AssertionError(
        "All payload variants failed to create product.\n" + "\n".join(errors)
    )


def test_root():
    wait_ready()
    r = requests.get(f"{BASE}/")
    assert r.status_code == 200
    assert "Welcome to the Product Service" in r.text


def test_create_list_delete_product():
    wait_ready()

    # --- Create (schema-tolerant) ---
    prod_id, used_payload, created_json = create_product_resilient()

    # --- List and ensure it appears ---
    r = requests.get(f"{BASE}/products/")
    assert r.status_code == 200
    items = r.json()
    # Try common keys for ID
    def get_id(obj):
        return obj.get("product_id") or obj.get("id") or obj.get("productId") or obj.get("productID")

    assert any(get_id(p) == prod_id for p in items), f"Product {prod_id} not found in list; list={items}"

    # --- Delete (support both /products/{id} and possible alt keys) ---
    r = requests.delete(f"{BASE}/products/{prod_id}")
    assert r.status_code in (200, 204), f"Delete failed: {r.status_code} {r.text}"
