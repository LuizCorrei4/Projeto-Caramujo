"""Step 02: clean data types, handle missing values, and domain rules."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Tuple

import numpy as np
import pandas as pd

from pipeline.config import PipelineConfig


@dataclass(frozen=True)
class Step02Stats:
	"""Metrics collected during cleaning and imputation."""

	invalid_age_count: int
	invalid_birth_year_count: int
	invalid_an_quant_count: int
	numeric_imputed_values: int
	categorical_imputed_values: int
	outliers_removed: int
	outlier_columns: Tuple[str, ...]


def standardize_missing_values(df: pd.DataFrame) -> pd.DataFrame:
	"""Standardize blank strings and trim text columns.

	Args:
		df: Input DataFrame.

	Returns:
		DataFrame with standardized missing values.
	"""

	df = df.copy()
	df = df.replace(r"^\s*$", pd.NA, regex=True)

	text_cols = df.select_dtypes(include=["object", "string"]).columns
	for col in text_cols:
		df[col] = (
			df[col]
			.astype("string")
			.str.strip()
			.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "NaT": pd.NA})
		)
	return df


def normalize_cs_escol_n(df: pd.DataFrame) -> pd.DataFrame:
	"""Normalize CS_ESCOL_N codes to 0-10 without leading zeros."""

	if "CS_ESCOL_N" not in df.columns:
		return df

	df = df.copy()
	s = (
		df["CS_ESCOL_N"]
		.astype("string")
		.str.strip()
		.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "NaT": pd.NA})
		.str.replace(r"\.0+$", "", regex=True)
	)

	num = pd.to_numeric(s, errors="coerce")
	num = num.where(num.notna() & (num % 1 == 0))
	num = num.astype("Int64")
	num = num.where(num.between(0, 10))

	df["CS_ESCOL_N"] = num.astype("string")
	return df


def parse_date_robust(series: pd.Series) -> pd.Series:
	"""Parse dates using multiple strategies.

	Args:
		series: Input series with heterogeneous date formats.

	Returns:
		Series of datetime values.
	"""

	s = (
		series.astype("string")
		.str.strip()
		.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA, "NaT": pd.NA})
	)

	date_iso = pd.to_datetime(s, format="%Y-%m-%d", errors="coerce")

	s_no_decimal = s.str.replace(r"\.0+$", "", regex=True)
	date_num_str = pd.to_datetime(s_no_decimal, format="%Y%m%d", errors="coerce")

	s_num = pd.to_numeric(s_no_decimal.str.replace(",", ".", regex=False), errors="coerce")
	s_num_int = pd.Series(pd.array(np.floor(s_num), dtype="Int64"), index=s.index).astype("string")
	date_num_float = pd.to_datetime(s_num_int, format="%Y%m%d", errors="coerce")

	return date_iso.fillna(date_num_str).fillna(date_num_float)


def convert_date_columns(df: pd.DataFrame, columns: Iterable[str]) -> pd.DataFrame:
	"""Convert date columns using a robust parser."""

	df = df.copy()
	for col in columns:
		if col in df.columns:
			df[col] = parse_date_robust(df[col])
	return df


def process_sinan_age(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, int]:
	"""Convert SINAN age encoding into years and clean invalid values.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		Tuple of DataFrame and count of invalid ages.
	"""

	if "NU_IDADE_N" not in df.columns:
		return df, 0

	df = df.copy()
	idade_raw = pd.to_numeric(df["NU_IDADE_N"], errors="coerce")
	unidade = (idade_raw // 1000).fillna(0).astype(int)
	valor = (idade_raw % 1000).fillna(0)

	condlist = [
		(unidade == 4).values,
		(unidade == 3).values,
		(unidade < 3).values,
	]
	choicelist = [
		valor,
		valor / 12,
		0,
	]

	idade_processada = np.select(condlist, choicelist, default=np.nan)
	idade_series = pd.Series(idade_processada, index=df.index)

	mask_invalid = (idade_series < config.age_min) | (idade_series > config.age_max)
	invalid_count = int(mask_invalid.sum())
	idade_series = idade_series.mask(mask_invalid)

	df["IDADE_PROCESSADA"] = idade_series
	df["NU_IDADE_N"] = idade_series
	return df, invalid_count


def apply_domain_rules(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, int, int, int]:
	"""Apply domain consistency rules for age, birth year, and AN_QUANT."""

	df, invalid_age = process_sinan_age(df, config)

	invalid_birth_year = 0
	if "ANO_NASC" in df.columns:
		df = df.copy()
		ano = pd.to_numeric(df["ANO_NASC"], errors="coerce")
		ano_atual = pd.Timestamp.today().year
		mask_ano = (ano < config.birth_year_min) | (ano > ano_atual)
		invalid_birth_year = int(mask_ano.sum())
		df["ANO_NASC"] = ano.mask(mask_ano)

	invalid_an_quant = 0
	if "AN_QUANT" in df.columns:
		df = df.copy()
		an_quant = pd.to_numeric(df["AN_QUANT"], errors="coerce")
		mask_negativo = an_quant < 0
		invalid_an_quant = int(mask_negativo.sum())
		df["AN_QUANT"] = an_quant.mask(mask_negativo)

	return df, invalid_age, invalid_birth_year, invalid_an_quant


def map_ignored_codes(df: pd.DataFrame, config: PipelineConfig) -> pd.DataFrame:
	"""Map ignored codes to missing values for selected columns."""

	df = df.copy()
	ignored_map = {value: pd.NA for value in config.ignored_code_values}
	for col in config.ignored_code_columns:
		if col in df.columns:
			df[col] = (
				df[col]
				.astype("string")
				.str.strip()
				.replace(ignored_map)
			)
	return df


def impute_missing_values(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, int, int]:
	"""Impute missing values for numeric and categorical columns.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		Tuple of DataFrame, numeric filled count, and categorical filled count.
	"""

	df = df.copy()
	exclude = set(config.resolved_impute_exclude_columns())

	datetime_cols = set(df.select_dtypes(include=["datetime64[ns]"]).columns)
	numeric_cols = [
		col
		for col in df.select_dtypes(include=["number"]).columns
		if col not in exclude
	]

	categorical_cols = [
		col
		for col in df.columns
		if col not in exclude
		and col not in numeric_cols
		and col not in datetime_cols
	]

	numeric_filled = 0
	for col in numeric_cols:
		before = int(df[col].isna().sum())
		if before == 0:
			continue
		median = df[col].median()
		if pd.notna(median):
			df[col] = df[col].fillna(median)
			after = int(df[col].isna().sum())
			numeric_filled += before - after

	categorical_filled = 0
	for col in categorical_cols:
		before = int(df[col].isna().sum())
		if before == 0:
			continue
		mode = df[col].mode(dropna=True)
		if not mode.empty:
			df[col] = df[col].fillna(mode.iloc[0])
			after = int(df[col].isna().sum())
			categorical_filled += before - after

	return df, numeric_filled, categorical_filled


def remove_outliers_iqr(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, int, Tuple[str, ...]]:
	"""Remove outliers using a conservative IQR rule.

	Method: keep values within [Q1 - 1.5 * IQR, Q3 + 1.5 * IQR] for each
	numeric column (excluding configured columns). Rows outside the interval
	are removed.
	"""

	if not config.apply_outlier_filter:
		return df, 0, tuple()

	exclude = set(config.outlier_exclude_columns)
	exclude.add(config.target_column)

	numeric_cols = [
		col
		for col in df.select_dtypes(include=["number"]).columns
		if col not in exclude
	]
	if not numeric_cols:
		return df, 0, tuple()

	mask = pd.Series(True, index=df.index)
	used_cols = []
	for col in numeric_cols:
		q1 = df[col].quantile(0.25)
		q3 = df[col].quantile(0.75)
		iqr = q3 - q1
		if pd.isna(iqr) or iqr <= 0:
			continue
		lower = q1 - config.outlier_iqr_multiplier * iqr
		upper = q3 + config.outlier_iqr_multiplier * iqr
		mask &= df[col].isna() | df[col].between(lower, upper)
		used_cols.append(col)

	removed = int((~mask).sum())
	return df[mask].copy(), removed, tuple(used_cols)


def clean_and_impute(df: pd.DataFrame, config: PipelineConfig) -> Tuple[pd.DataFrame, Step02Stats]:
	"""Run cleaning, domain rules, and missing value handling.

	Args:
		df: Input DataFrame.
		config: Pipeline configuration.

	Returns:
		Tuple with cleaned DataFrame and step stats.
	"""

	df = standardize_missing_values(df)
	df = normalize_cs_escol_n(df)
	df = convert_date_columns(df, config.date_columns)

	df, invalid_age, invalid_birth_year, invalid_an_quant = apply_domain_rules(df, config)
	df = map_ignored_codes(df, config)

	df, numeric_filled, categorical_filled = impute_missing_values(df, config)
	df, outliers_removed, outlier_columns = remove_outliers_iqr(df, config)

	stats = Step02Stats(
		invalid_age_count=invalid_age,
		invalid_birth_year_count=invalid_birth_year,
		invalid_an_quant_count=invalid_an_quant,
		numeric_imputed_values=numeric_filled,
		categorical_imputed_values=categorical_filled,
		outliers_removed=outliers_removed,
		outlier_columns=outlier_columns,
	)
	return df, stats
