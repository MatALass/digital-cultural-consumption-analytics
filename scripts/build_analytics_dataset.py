from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / 'src'
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from dashboard.utils.io import load_all_sources


def main() -> None:
    sources = load_all_sources()
    analytics = sources['analytics']
    out_dir = PROJECT_ROOT / 'data' / 'processed'
    out_dir.mkdir(parents=True, exist_ok=True)
    output_path = out_dir / 'analytics_dataset_generated.csv'
    analytics.to_csv(output_path, index=False)
    print(f'Wrote {len(analytics):,} rows to {output_path.as_posix()}')


if __name__ == '__main__':
    main()
