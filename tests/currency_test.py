# tests/schema_smoke_test.py
"""
Quick smoke-tests for the currencies / items / transaction_ledger schema.

Run with:   pytest -q
"""

from pprint import pprint

import pytest

from app import db as app_db   # same pattern as select_all_visits_test.py


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

EXPECTED_UNITS = {"cp", "sp", "ep", "gp", "pp"}
CP_FACTOR = {"cp": 1, "sp": 10, "ep": 50, "gp": 100, "pp": 1_000}


def _fetchall(sql: str):
    """Convenience wrapper to execute <sql> and return list[sqlite3.Row]."""
    with app_db.get_connection() as conn:
        return conn.execute(sql).fetchall()


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------

def test_currencies_lookup() -> None:
    """Currencies table has the exact five coin types and correct factors."""
    rows = _fetchall("SELECT unit, value_in_cp FROM currencies ORDER BY value_in_cp")
    pprint(rows, width=80)

    units = {row["unit"] for row in rows}
    assert units == EXPECTED_UNITS, f"Unexpected units in currencies: {units}"

    for row in rows:
        assert row["value_in_cp"] == CP_FACTOR[row["unit"]], (
            f"Bad factor for {row['unit']}: {row['value_in_cp']} (expected "
            f"{CP_FACTOR[row['unit']]})"
        )


def test_items_have_valid_price_unit() -> None:
    """Every item’s price_unit must exist in currencies (FK sanity)."""
    mismatches = _fetchall(
        """
        SELECT item_id, item_name, price_unit
        FROM   items
        WHERE  price_unit NOT IN (SELECT unit FROM currencies)
        """
    )
    if mismatches:
        pprint(mismatches, width=100)
    assert not mismatches, "Some items reference a non-existent currency!"


def test_items_copper_conversion_is_correct() -> None:
    """
    Join items→currencies and check the computed copper value matches the
    Python side arithmetic.
    """
    rows = _fetchall(
        """
        SELECT i.item_id,
               i.item_name,
               i.base_price,
               i.price_unit,
               i.base_price * c.value_in_cp AS price_in_cp_sql
        FROM   items i
        JOIN   currencies c ON c.unit = i.price_unit
        LIMIT  50
        """
    )

    print(f"\n🔍 Checked {len(rows)} items for price conversion accuracy:\n")
    for row in rows[:15]:
        pprint(dict(row), sort_dicts=False, width=100)

    for r in rows:
        price_in_cp_py = r["base_price"] * CP_FACTOR[r["price_unit"]]
        assert r["price_in_cp_sql"] == price_in_cp_py, (
            f"Mismatch for item_id={r['item_id']}: "
            f"{r['price_in_cp_sql']=} vs {price_in_cp_py=}"
        )


def test_transaction_ledger_currency_fk() -> None:
    """Every ledger entry's currency should also exist in currencies."""
    bad_rows = _fetchall(
        """
        SELECT id, currency
        FROM   transaction_ledger
        WHERE  currency NOT IN (SELECT unit FROM currencies)
        """
    )
    if bad_rows:
        pprint(bad_rows, width=80)
    assert not bad_rows, "transaction_ledger contains invalid currency codes"


def test_running_balance_demo() -> None:
    """
    Simple demonstration query: running balance for the first party in
    'parties'.  Test passes as long as the SQL executes and returns rows.
    """
    party_row = _fetchall("SELECT party_id FROM parties LIMIT 1")
    pytest.skip("No parties found") if not party_row else None
    party_id = party_row[0]["party_id"]

    rows = _fetchall(
        f"""
        WITH x AS (
          SELECT l.*,
                 l.amount * c.value_in_cp AS delta_cp
          FROM   transaction_ledger l
          JOIN   currencies c ON c.unit = l.currency
          WHERE  l.party_id = '{party_id}'
          ORDER  BY l.timestamp, l.id
        )
        SELECT id,
               action,
               delta_cp,
               SUM(delta_cp) OVER (ORDER BY timestamp,id) AS balance_cp
        FROM   x
        """
    )

    print(f"\n📒 Running balance for party '{party_id}' ({len(rows)} rows):\n")
    for row in rows[:15]:
        pprint(dict(row), sort_dicts=False, width=100)
    assert rows, "Running-balance query returned no rows"
