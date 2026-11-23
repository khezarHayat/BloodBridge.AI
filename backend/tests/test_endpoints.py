import asyncio
import sys
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import health_check, root
from app.api.public import get_blood_groups_info, get_supported_areas


async def run_tests():
    print("=== TESTING FASTAPI ROUTE HANDLERS ===", flush=True)

    h = await health_check()
    print(f"[PASS] /health probe: {h['status']} ({h['service']}) in {h['city']}", flush=True)
    assert h["status"] == "healthy"

    r = await root()
    print(f"[PASS] / root metadata: {r['platform']} - '{r['tagline']}'", flush=True)
    assert r["platform"] == "BloodBridge"

    c = await get_blood_groups_info()
    compat = c.get("compatibility", {})
    print(f"[PASS] /api/public/blood-groups: {len(compat)} blood groups, Universal Donor: {c.get('universal_donor')}", flush=True)
    assert len(compat) == 8
    assert c.get("universal_donor") == "O-"
    assert c.get("universal_recipient") == "AB+"

    areas = await get_supported_areas()
    print(f"[PASS] /api/public/areas: {len(areas)} Peshawar localities ({', '.join([a['name'] for a in areas[:4]])}...)", flush=True)
    assert len(areas) >= 5

    print("=== ALL 4 ROUTE CHECKS PASSED SUCCESSFULLY ===", flush=True)


if __name__ == "__main__":
    asyncio.run(run_tests())
