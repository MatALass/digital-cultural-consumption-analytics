from __future__ import annotations

import sys
import types


def _cache_data(*args, **kwargs):
    def decorator(func):
        return func

    return decorator


streamlit = types.SimpleNamespace(
    cache_data=_cache_data,
)

sys.modules.setdefault("streamlit", streamlit)
