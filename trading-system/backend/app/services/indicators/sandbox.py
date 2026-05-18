"""Docker Socket Mount sandbox spawn (§9.1).

M1 PoC: prove the backend can spawn the sandbox image with all hard
limits and get JSON back over stdin/stdout within the timeout.
"""
import asyncio
import json

from app.config import settings


async def run_in_sandbox(code: str, candles_json: list, params: dict) -> dict:
    payload = json.dumps(
        {"code": code, "candles_json": candles_json, "params": params}
    )

    args = [
        "docker", "run", "--rm", "-i",
        "--network", "none",
        "--memory", settings.sandbox_memory,
        "--cpus", settings.sandbox_cpus,
        "--read-only",
        "--tmpfs", "/tmp:size=10m",
        "--user", "nobody",
        "--pids-limit", "50",
        "--cap-drop", "ALL",
        settings.sandbox_image,
    ]

    proc = await asyncio.create_subprocess_exec(
        *args,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(
            proc.communicate(payload.encode()),
            timeout=settings.sandbox_timeout_sec,
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise TimeoutError(
            f"Sandbox exceeded {settings.sandbox_timeout_sec}s timeout"
        )

    if proc.returncode != 0 and not stdout:
        raise RuntimeError(f"Sandbox failed: {stderr.decode()[:500]}")
    return json.loads(stdout.decode())
