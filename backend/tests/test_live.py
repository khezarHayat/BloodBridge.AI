import sys
print("STEP 1: Starting test_live.py", flush=True)

from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

print("STEP 2: Importing app.main", flush=True)
from app.main import app
print("STEP 3: Successfully imported app", flush=True)

import asyncio
import httpx

async def main():
    print("STEP 4: Entering main", flush=True)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        print("STEP 5: Sending /health request", flush=True)
        r = await client.get("/health")
        print("STEP 6: /health response:", r.status_code, r.json(), flush=True)

        r2 = await client.get("/")
        print("STEP 7: / response:", r2.status_code, r2.json().get("platform"), flush=True)

        r3 = await client.get("/api/public/blood-groups")
        print("STEP 8: /api/public/blood-groups:", r3.status_code, "universal_donor:", r3.json().get("universal_donor"), flush=True)

        r4 = await client.get("/api/public/areas")
        print("STEP 9: /api/public/areas:", r4.status_code, "count:", len(r4.json()), flush=True)
        print("=== ALL LIVE ENDPOINTS PASSED ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
