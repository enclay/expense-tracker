import time
from collections import defaultdict

_hits = defaultdict(list)

def allow(user_id: int, limit: int = 5, window: int = 60) -> bool:
    now = time.time()
    _hits[user_id] = [t for t in _hits[user_id] if now - t < window]
    if len(_hits[user_id]) >= limit:
        return False
    _hits[user_id].append(now)
    return True