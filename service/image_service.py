from typing import Optional
import httpx

http_client: Optional[httpx.AsyncClient] = None

async def get_http_client():
    global http_client
    if http_client is None:
        http_client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20)
        )
    return http_client

async def fetch_data_from_url(url: str) -> Optional[bytes]:
    try:
        client = await get_http_client()
        response = await client.get(url)
        
        if response.status_code == 200:
            return response.content
        return None
    except Exception as e:
        print(f"✗ Fetch error: {e}")
        return None
