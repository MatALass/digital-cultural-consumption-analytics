"""Commande `dcca` : reconstruire les tables ou vérifier qu'elles sont à jour."""

from __future__ import annotations

import argparse
import sys

import pandas as pd

from dcca import config as cfg
from dcca.build import build_tables, load_tables, read_raw, write_tables
from dcca.quality import run_quality_checks


def _build() -> int:
    print(f"Lecture de {cfg.RAW_SURVEY_PATH.name}...")
    tables = build_tables(read_raw())
    failures = run_quality_checks(tables)
    if failures:
        print("Contrôles qualité en échec :")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    for path in write_tables(tables):
        print(f"  écrit : {path.relative_to(cfg.PROJECT_ROOT)}")
    r = tables.respondents
    print(
        f"{len(r)} répondants, {int(r['consommateur'].sum())} consommateurs, "
        f"{len(tables.contents)} lignes contenu."
    )
    return 0


def _check() -> int:
    """Échoue si les fichiers de data/processed ne correspondent plus au brut."""
    fresh = build_tables(read_raw())
    stored = load_tables()
    stale = []
    for name, frame in fresh.as_dict().items():
        try:
            pd.testing.assert_frame_equal(
                frame.reset_index(drop=True),
                stored.as_dict()[name].reset_index(drop=True),
                check_dtype=False,
            )
        except AssertionError:
            stale.append(name)
    if stale:
        print("Tables à reconstruire (lancer `dcca build`) : " + ", ".join(stale))
        return 1
    print("Les tables de data/processed sont à jour.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="dcca", description=__doc__)
    parser.add_argument("commande", choices=["build", "check"])
    args = parser.parse_args(argv)
    return _build() if args.commande == "build" else _check()


if __name__ == "__main__":
    sys.exit(main())
