"""Enrich SINAN processed data with geographic labels from geobr."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

try:
    import geobr
except ImportError as exc:
    raise SystemExit(
        "geobr is required. Install with: pip install geobr geopandas"
    ) from exc


def _load_geobr_municipios(year: int) -> pd.DataFrame:
    gdf = geobr.read_municipality(code_muni="all", year=year)
    gdf = gdf[["code_muni", "name_muni", "abbrev_state", "geometry"]].copy()
    gdf["code_muni_str"] = gdf["code_muni"].astype("string").str[:6]
    gdf = gdf.drop_duplicates(subset=["code_muni_str"])

    gdf_proj = gdf.to_crs(3857)
    centroids = gdf_proj.geometry.centroid.to_crs(4674)
    gdf["longitude_municipio"] = centroids.x
    gdf["latitude_municipio"] = centroids.y
    return gdf


def enrich_geo(
    input_path: Path,
    output_path: Path,
    year: int = 2020,
    id_column: str = "ID_MUNICIP",
    keep_geometry: bool = False,
) -> Path:
    df = pd.read_parquet(input_path)
    if id_column not in df.columns:
        raise KeyError(f"Missing column: {id_column}")

    df = df.copy()
    df[id_column] = df[id_column].astype("string").str.zfill(6)

    gdf = _load_geobr_municipios(year)

    merged = df.merge(
        gdf[[
            "code_muni_str",
            "name_muni",
            "abbrev_state",
            "longitude_municipio",
            "latitude_municipio",
            "geometry",
        ]],
        left_on=id_column,
        right_on="code_muni_str",
        how="left",
    )

    merged = merged.rename(
        columns={
            "name_muni": "nome_municipio",
            "abbrev_state": "uf_sigla",
        }
    )

    if not keep_geometry:
        merged = merged.drop(columns=["geometry"])

    merged = merged.drop(columns=["code_muni_str"])

    missing = int(merged["nome_municipio"].isna().sum())
    print(f"Missing nome_municipio after merge: {missing}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(output_path, index=False)
    return output_path


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enrich SINAN data with geobr labels")
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/sinan_esq_processed_with_dt_notific.parquet",
        help="Input parquet",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/processed/sinan_esq_processed_with_dt_notific_geo.parquet",
        help="Output parquet",
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2020,
        help="geobr municipality year",
    )
    parser.add_argument(
        "--id-column",
        type=str,
        default="ID_MUNICIP",
        help="Column with municipality code (6 digits)",
    )
    parser.add_argument(
        "--keep-geometry",
        action="store_true",
        help="Keep geometry column in output",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    output_path = enrich_geo(
        input_path=Path(args.input),
        output_path=Path(args.output),
        year=args.year,
        id_column=args.id_column,
        keep_geometry=args.keep_geometry,
    )
    print(f"Saved: {output_path}")


if __name__ == "__main__":
    main()
