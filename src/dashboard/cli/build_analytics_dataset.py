from __future__ import annotations

from pathlib import Path

from dashboard.utils.io import load_all_sources

PROJECT_ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    sources = load_all_sources()
    analytics = sources["analytics"]

    out_dir = PROJECT_ROOT / "data" / "processed"
    out_dir.mkdir(parents=True, exist_ok=True)

    output_path = out_dir / "analytics_dataset_generated.csv"
    analytics.to_csv(output_path, index=False)

    print(f"Wrote {len(analytics):,} rows to {output_path.as_posix()}")


if __name__ == "__main__":
    main()