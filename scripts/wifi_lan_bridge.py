"""
Al-Khwarizmi Math AI - Wi-Fi / Local Area Network (LAN) HTTP Bridge
Provides rock-solid HTTP proxying so mobile devices (phones, tablets)
connected to the local Wi-Fi can always access the WSL/Windows AI backend.
"""

from __future__ import annotations
import socket
import threading
import uvicorn
from starlette.applications import Starlette
from starlette.responses import Response
from starlette.routing import Route
import httpx

TARGET_BASE_URL = "http://127.0.0.1:8000"


def get_all_lan_ips() -> list[str]:
    ips = set()
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ips.add(s.getsockname()[0])
        s.close()
    except Exception:
        pass
    
    try:
        hostname = socket.gethostname()
        for ip in socket.gethostbyname_ex(hostname)[2]:
            if not ip.startswith("127.") and not ip.startswith("169.254."):
                ips.add(ip)
    except Exception:
        pass
    return list(ips) or ["127.0.0.1"]


_http_client: httpx.AsyncClient | None = None


async def get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(base_url=TARGET_BASE_URL, timeout=30.0)
    return _http_client


async def proxy_all(request):
    client = await get_client()
    url = httpx.URL(path=request.url.path, query=request.url.query.encode("utf-8"))
    content = await request.body()
    headers = dict(request.headers)
    headers.pop("host", None)

    try:
        rp = await client.request(
            method=request.method,
            url=url,
            headers=headers,
            content=content,
        )
        resp_headers = {
            k: v
            for k, v in rp.headers.items()
            if k.lower() not in ("content-length", "content-encoding", "transfer-encoding")
        }
        return Response(
            content=rp.content,
            status_code=rp.status_code,
            headers=resp_headers,
            media_type=rp.headers.get("content-type"),
        )
    except Exception as e:
        return Response(
            content=f'{{"detail": "Wi-Fi Bridge forward error: {e}"}}',
            status_code=502,
            media_type="application/json",
        )


app = Starlette(
    routes=[
        Route("/{path:path}", proxy_all, methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD"]),
    ]
)


def run_server(host: str, port: int):
    try:
        config = uvicorn.Config(app, host=host, port=port, log_level="warning")
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        print(f"[!] Info: {host}:{port} status: {e}")


def main():
    lan_ips = get_all_lan_ips()
    primary_ip = lan_ips[0]
    
    print("=" * 65)
    print("   Al-Khwarizmi Neuro-Symbolic Math AI - Wi-Fi LAN Bridge")
    print("=" * 65)
    print(f"[*] Detected Local PC Network IPs: {', '.join(lan_ips)}")
    print(f"[*] Forwarding traffic to AI Backend: {TARGET_BASE_URL}")
    print(f"[*] Mobile Phone App & Web Browser can connect to:")
    for ip in lan_ips:
        print(f"       ==> http://{ip}:8000")
        print(f"       ==> http://{ip}:8001")
    print("=" * 65)

    # 1. Start universal listener on 0.0.0.0:8001 in background thread
    t_universal = threading.Thread(target=run_server, args=("0.0.0.0", 8001), daemon=True)
    t_universal.start()

    # 2. Start listener on primary_ip:8000
    run_server(primary_ip, 8000)


if __name__ == "__main__":
    main()
