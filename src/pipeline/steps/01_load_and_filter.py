"""Step 01: load raw data and apply initial filters and discards."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import pandas as pd

from pipeline.config import PipelineConfig


@dataclass(frozen=True)
class Step01Stats:
	"""Metrics collected during load and filter."""

	rows_initial: int
	rows_after_positive_filter: int
	rows_after_target_filter: int
	rows_after_target_drop: int
	dropped_immediate_columns: Tuple[str, ...]


def load_raw_data(input_path: Path) -> pd.DataFrame:
	"""Load the raw parquet file.

	Args:
		input_path: Path to the raw parquet file.

	Returns:
		DataFrame with raw records.
	"""

	if not input_path.exists():
		raise FileNotFoundError(f"Arquivo nao encontrado: {input_path}")
	return pd.read_parquet(input_path)


def _normalize_string_series(series: pd.Series) -> pd.Series:
	"""Trim strings and convert empty values to NA."""

	return (
		series.astype("string")
		.str.strip()
		.replace({"": pd.NA})
	)


def filter_positive_cases(df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
	"""Filter to keep only positive cases when configured.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		Filtered DataFrame.
	"""

	if not config.apply_positive_filter:
		return df

	col = config.positive_filter_column
	if col not in df.columns:
		return df

	df = df.copy()
	df[col] = _normalize_string_series(df[col])
	return df[df[col] == config.positive_filter_value].copy()


def clean_target_column(df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
	"""Normalize target values and drop invalid codes.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		DataFrame with normalized target column.
	"""

	target = config.target_column
	if target not in df.columns:
		raise KeyError(f"Coluna alvo ausente: {target}")

	df = df.copy()
	df[target] = _normalize_string_series(df[target])
	invalid_map = {value: pd.NA for value in config.target_invalid_values}
	df[target] = df[target].replace(invalid_map)
	return df


def drop_target_values(df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
	"""Drop rows with target values configured for removal."""

	target = config.target_column
	if target not in df.columns or not config.target_drop_values:
		return df
	return df[~df[target].isin(config.target_drop_values)].copy()


def drop_immediate_columns(
	df: pd.DataFrame,
	columns: Tuple[str, ...],
) -> Tuple[pd.DataFrame, Tuple[str, ...]]:
	"""Drop columns that are immediately discarded.

	Args:
		df: Input DataFrame.
		columns: Columns to drop.

	Returns:
		Tuple of cleaned DataFrame and dropped columns.
	"""

	existing = tuple(col for col in columns if col in df.columns)
	if not existing:
		return df, existing
	return df.drop(columns=list(existing)).copy(), existing


def load_and_filter(config: PipelineConfig) -> Tuple[pd.DataFrame, Step01Stats]:
	"""Load, filter, and apply immediate column discards.

	Args:
		config: Pipeline configuration.

	Returns:
		Tuple with filtered DataFrame and step stats.
	"""

	df_raw = load_raw_data(config.input_path)
	rows_initial = len(df_raw)

	df = filter_positive_cases(df_raw, config)
	rows_after_positive = len(df)

	if config.apply_target_filter:
		df = clean_target_column(df, config)
		df = df[df[config.target_column].notna()].copy()
		rows_after_target = len(df)

		df = drop_target_values(df, config)
		rows_after_target_drop = len(df)
	else:
		rows_after_target = len(df)
		rows_after_target_drop = len(df)

	df, dropped_cols = drop_immediate_columns(df, config.immediate_drop_columns)

	stats = Step01Stats(
		rows_initial=rows_initial,
		rows_after_positive_filter=rows_after_positive,
		rows_after_target_filter=rows_after_target,
		rows_after_target_drop=rows_after_target_drop,
		dropped_immediate_columns=dropped_cols,
	)
	return df, stats
