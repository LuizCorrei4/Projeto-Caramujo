"""Pipeline configuration for SINAN esquistossomose preprocessing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


IMMEDIATE_DROP_COLUMNS: Tuple[str, ...] = (
	"TP_NOT",
	"ID_AGRAVO",
	"ID_AGRAVP",
	"DT_DIGITA",
	"DT_TRANSUS",
	"DT_TRANSDM",
	"DT_TRANSSM",
	"DT_TRANSRS",
	"DT_TRANSSE",
	"NOPROPIN",
	"NOCOLINF",
	"DS_FORMA",
	"OUTRO_EX",
)

DATE_COLUMNS: Tuple[str, ...] = (
	"DT_NOTIFIC",
	"DT_SIN_PRI",
	"DT_INVEST",
	"DT_COPRO",
	"DT_ENCERRA",
	"DT_OBITO",
	"DTTRAT",
	"DT_RESU3",
)

IGNORED_CODE_COLUMNS: Tuple[str, ...] = (
	"CS_SEXO",
	"CS_GESTANT",
	"CS_RACA",
	"CS_ESCOL_N",
	"OUTROS",
	"TRATAM",
	"TRATANAO",
	"STCURA1",
	"STCURA2",
	"STCURA3",
	"FORMA",
	"TPAUTOCTO",
	"DOENCA_TRA",
	"EVOLUCAO",
	"AN_QUALI",
)

IGNORED_CODE_VALUES: Tuple[str, ...] = (
	"I",
	"9",
	"99",
	"999",
	"9999",
	"Ignorado",
	"IGNORADO",
)

DROP_AFTER_FEATURES: Tuple[str, ...] = (
	"TRATANAO",
	"DT_OBITO",
	"DT_RESU3",
	"ID_REGIONA",
	"ID_MN_RESI",
	"ID_RG_RESI",
	"SEM_NOT",
	"SEM_PRI",
	"NU_ANO",
	"ID_OCUPA_N",
	"COMUNINF",
	"OUTROS",
	"SG_UF_NOT",
	"ID_PAIS",
	"DT_NOTIFIC",
	"DT_SIN_PRI",
	"DT_INVEST",
	"DT_ENCERRA",
	"DTTRAT",
	"DT_COPRO",
	"NU_IDADE_N",
	"ANO_NASC",
	"idade_aprox_no_evento",
	"STCURA1",
	"STCURA2",
	"STCURA3",
	"AN_QUANT",
	"TPAUTOCTO",
	"COPAISINF",
)


@dataclass(slots=True)
class PipelineConfig:
	"""Centralized configuration for preprocessing.

	Attributes:
		input_path: Path to the raw SINAN parquet file.
		output_path: Destination for the processed parquet file.
		apply_positive_filter: Whether to keep only positive cases.
		positive_filter_column: Column used for the positive case filter.
		positive_filter_value: Value that identifies a positive case.
		apply_target_filter: Whether to apply target-based filters.
		target_column: Target column for supervised modeling.
		target_invalid_values: Values to be treated as missing in target.
		target_drop_values: Values to be removed from target (e.g., other causes).
		immediate_drop_columns: Columns discarded immediately.
		date_columns: Columns to parse as datetime.
		ignored_code_columns: Columns with ignored codes to map to NaN.
		ignored_code_values: Values representing ignored/missing codes.
		drop_after_features: Columns removed after feature engineering.
		apply_drop_after_features: Whether to drop columns after features.
		age_min: Minimum plausible age in years.
		age_max: Maximum plausible age in years.
		birth_year_min: Minimum plausible birth year.
		impute_exclude_columns: Extra columns excluded from imputation.
	"""

	input_path: Path = Path("data/sinan_esqu_raw.parquet")
	output_path: Path = Path("data/processed/sinan_esqu_processed.parquet")

	apply_positive_filter: bool = True
	positive_filter_column: str = "AN_QUALI"
	positive_filter_value: str = "1"
	apply_target_filter: bool = True

	target_column: str = "EVOLUCAO"
	target_invalid_values: Tuple[str, ...] = ("", "9", "99", "Ignorado", "IGNORADO")
	target_drop_values: Tuple[str, ...] = ("4",)

	immediate_drop_columns: Tuple[str, ...] = IMMEDIATE_DROP_COLUMNS
	date_columns: Tuple[str, ...] = DATE_COLUMNS
	ignored_code_columns: Tuple[str, ...] = IGNORED_CODE_COLUMNS
	ignored_code_values: Tuple[str, ...] = IGNORED_CODE_VALUES

	drop_after_features: Tuple[str, ...] = DROP_AFTER_FEATURES
	apply_drop_after_features: bool = True

	age_min: int = 0
	age_max: int = 130
	birth_year_min: int = 1900

	impute_exclude_columns: Tuple[str, ...] = ()

	def resolved_impute_exclude_columns(self) -> Tuple[str, ...]:
		"""Return the columns that must not be imputed."""

		ordered = list(self.impute_exclude_columns)
		if self.apply_target_filter:
			ordered.append(self.target_column)
		ordered.extend(self.date_columns)
		return tuple(dict.fromkeys(ordered))
