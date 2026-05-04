"""Step 03: create derived features for modeling."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import numpy as np
import pandas as pd

from pipeline.config import PipelineConfig


@dataclass(frozen=True)
class Step03Stats:
	"""Metrics collected during feature engineering."""

	created_features: Tuple[str, ...]
	dropped_after_features: Tuple[str, ...]
	outliers_removed: int
	outlier_columns: Tuple[str, ...]


def _sanitize_duration(series: pd.Series) -> pd.Series:
	"""Convert negative durations to missing values."""

	return series.where(series >= 0, np.nan)


def add_temporal_features(df: pd.DataFrame) -> Tuple[pd.DataFrame, Tuple[str, ...]]:
	"""Create temporal and age-derived features.

	Returns:
		Tuple with DataFrame and names of created features.
	"""

	df = df.copy()
	created = []

	if {"DT_NOTIFIC", "DT_SIN_PRI"}.issubset(df.columns):
		df["delay_notificacao_dias"] = (df["DT_NOTIFIC"] - df["DT_SIN_PRI"]).dt.days
		df["delay_notificacao_dias"] = _sanitize_duration(df["delay_notificacao_dias"])
		created.append("delay_notificacao_dias")

	if {"DT_ENCERRA", "DT_NOTIFIC"}.issubset(df.columns):
		df["tempo_encerramento_dias"] = (df["DT_ENCERRA"] - df["DT_NOTIFIC"]).dt.days
		df["tempo_encerramento_dias"] = _sanitize_duration(df["tempo_encerramento_dias"])
		created.append("tempo_encerramento_dias")

	if {"DT_NOTIFIC", "ANO_NASC"}.issubset(df.columns):
		ano_nasc = pd.to_numeric(df["ANO_NASC"], errors="coerce")
		df["idade_aprox_no_evento"] = df["DT_NOTIFIC"].dt.year - ano_nasc
		df["idade_aprox_no_evento"] = df["idade_aprox_no_evento"].where(
			df["idade_aprox_no_evento"].between(0, 130),
			np.nan,
		)
		created.append("idade_aprox_no_evento")

	return df, tuple(created)


def drop_after_features(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, Tuple[str, ...]]:
	"""Drop columns after feature engineering when configured."""

	if not config.apply_drop_after_features:
		return df, tuple()

	to_drop = tuple(col for col in config.drop_after_features if col in df.columns)
	if not to_drop:
		return df, tuple()

	return df.drop(columns=list(to_drop)).copy(), to_drop


def remove_outliers_iqr_for_columns(
	df: pd.DataFrame,
	columns: Tuple[str, ...],
	multiplier: float,
) -> Tuple[pd.DataFrame, int, Tuple[str, ...]]:
	"""Remove outliers using a conservative IQR rule for selected columns.

	Method: keep values within [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR] for each
	column in the provided list. Rows outside the interval are removed.
	"""

	if not columns:
		return df, 0, tuple()

	existing = [col for col in columns if col in df.columns]
	if not existing:
		return df, 0, tuple()

	mask = pd.Series(True, index=df.index)
	used_cols = []
	for col in existing:
		if not pd.api.types.is_numeric_dtype(df[col]):
			continue
		q1 = df[col].quantile(0.25)
		q3 = df[col].quantile(0.75)
		iqr = q3 - q1
		if pd.isna(iqr) or iqr <= 0:
			continue
		lower = q1 - multiplier * iqr
		upper = q3 + multiplier * iqr
		mask &= df[col].isna() | df[col].between(lower, upper)
		used_cols.append(col)

	removed = int((~mask).sum())
	return df[mask].copy(), removed, tuple(used_cols)


def feature_engineering(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, Step03Stats]:
	"""Run feature engineering and optional column pruning.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		Tuple with DataFrame and step stats.
	"""

	df, created = add_temporal_features(df)
	if config.apply_outlier_filter:
		df, outliers_removed, outlier_columns = remove_outliers_iqr_for_columns(
			df,
			config.post_feature_outlier_columns,
			config.outlier_iqr_multiplier,
		)
	else:
		outliers_removed, outlier_columns = 0, tuple()
	
	df, dropped = drop_after_features(df, config)

	stats = Step03Stats(
		created_features=created,
		dropped_after_features=dropped,
		outliers_removed=outliers_removed,
		outlier_columns=outlier_columns,
	)
	return df, stats
