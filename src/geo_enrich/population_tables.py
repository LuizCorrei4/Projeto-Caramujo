"""Generate population tables by year using IBGE/SIDRA."""

from __future__ import annotations

import ssl
import argparse
import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd

SIDRA_BASE_URL = "https://apisidra.ibge.gov.br/values"
SIDRA_TABLE = 6579
SIDRA_VARIABLE = 9324
AVAILABLE_YEARS = [2008, 2009, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2024, 2025]

def _sidra_url(year: int) -> str:
    return (
        f"{SIDRA_BASE_URL}/"
        f"t/{SIDRA_TABLE}/n3/all/v/{SIDRA_VARIABLE}/p/{year}"
    )


def _read_sidra(url: str) -> pd.DataFrame:
    # WORKAROUND: certificado do servidor api.sidra.ibge.gov.br tem hostname mismatch.
    # Problema no lado do IBGE. Dados são públicos, risco de MITM é aceitável aqui.
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        with urlopen(url, timeout=60, context=ctx) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="ignore")
        raise RuntimeError(
            f"SIDRA request failed ({exc.code}). URL: {url}. Detail: {detail[:400]}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"SIDRA request failed. URL: {url}. Error: {exc}") from exc
    df = pd.DataFrame(payload)
    if df.empty:
        raise RuntimeError(f"No data returned from SIDRA: {url}")
    if "V" in df.columns:
        df = df[df["V"] != "Valor"].copy()
    return df


def _select_code_col(df: pd.DataFrame) -> str | None:
    candidates = [c for c in df.columns if c.startswith("D") and c.endswith("C")]
    for col in candidates:
        sample = df[col].astype("string").head(50)
        if sample.empty:
            continue
        ratio = sample.str.match(r"^\d{1,2}$").mean()
        if ratio >= 0.8:
            return col
    return candidates[0] if candidates else None


def _fetch_population_ufs(year: int) -> pd.DataFrame:
    df = _read_sidra(_sidra_url(year))
    code_col = _select_code_col(df)
    if not code_col:
        raise RuntimeError("Could not locate UF code column in SIDRA response")
    name_col = code_col.replace("C", "N")
    if name_col not in df.columns:
        name_col = None

    out = pd.DataFrame()
    out["code_state"] = df[code_col].astype("string")
    if name_col:
        out["nome_uf"] = df[name_col].astype("string")

    pop = df["V"].astype("string")
    pop = pop.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    out["populacao"] = pd.to_numeric(pop, errors="coerce")
    out["ano"] = year
    out = out.dropna(subset=["code_state", "populacao"]).copy()
    out["populacao"] = out["populacao"].astype("int64")
    return out


def _resolve_years(input_path: Path, years_arg: str | None) -> list[int]:
    if years_arg:
        years = [int(y.strip()) for y in years_arg.split(",") if y.strip()]
        if not years:
            raise ValueError("No valid years provided")
        return sorted(set(years))

    df = pd.read_parquet(input_path, columns=["DT_NOTIFIC"])
    dt = pd.to_datetime(df["DT_NOTIFIC"], errors="coerce")
    dataset_years = set(dt.dropna().dt.year.unique().tolist())

    years = sorted(dataset_years & set(AVAILABLE_YEARS))
    if not years:
        raise RuntimeError("No overlapping years between dataset and SIDRA available years")
    print(f"Years to fetch: {years}")
    return years


def generate_population_tables(
    input_path: Path,
    output_dir: Path,
    years: list[int] | None = None,
) -> None:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    years = years or _resolve_years(input_path, None)

    for year in years:
        print(f"Fetching population for year {year}...")
        pop_ufs = _fetch_population_ufs(year)

        uf_path = output_dir / f"pop_ufs_{year}.parquet"
        pop_ufs.to_parquet(uf_path, index=False)
        print(f"Saved: {uf_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate population tables by year (UFs only)"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/processed/sinan_esq_processed_with_dt_notific_geo.parquet",
        help="Input parquet with DT_NOTIFIC",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/populacao/ufs",
        help="Output directory for population tables",
    )
    parser.add_argument(
        "--years",
        type=str,
        default="",
        help="Comma-separated list of years (optional)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    years = _resolve_years(Path(args.input), args.years or None)
    generate_population_tables(
        input_path=Path(args.input),
        output_dir=Path(args.output_dir),
        years=years,
    )


if __name__ == "__main__":
    main()