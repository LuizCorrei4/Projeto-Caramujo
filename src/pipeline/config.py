"""Pipeline configuration for SINAN esquistossomose preprocessing."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple


IMMEDIATE_DROP_COLUMNS: Tuple[str, ...] = (
	"TP_NOT",
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

IMMEDIATE_DROP_COLUMN_ALIASES = {
	"ID_AGRAVP": "ID_AGRAVP",
}

UNSUPERVISED_COHORT_DROP_COLUMNS: Tuple[str, ...] = (
	"AN_QUALI",
)

UNSUPERVISED_COHORT_DROP_VALUES: Tuple[str, ...] = (
	"2",
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
	""
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
	"ID_PAIS",
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

# é a lista de colunas que não entram no filtro de outliers por IQR pois são identificadores
OUTLIER_EXCLUDE_COLUMNS: Tuple[str, ...] = (
	"ID_MUNICIP",
	"ID_UNIDADE",
)

POST_FEATURE_OUTLIER_COLUMNS: Tuple[str, ...] = (
	"delay_notificacao_dias",
	"tempo_encerramento_dias",
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
		cohort_drop_columns: Columns where selected values will be removed.
		cohort_drop_values: Values removed from the configured cohort columns.
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
		apply_outlier_filter: Whether to remove outliers using IQR.
		outlier_iqr_multiplier: IQR multiplier for outlier bounds.
		outlier_exclude_columns: Columns excluded from outlier filtering.
		post_feature_outlier_columns: Columns filtered by IQR after features.
		age_min: Minimum plausible age in years.
		age_max: Maximum plausible age in years.
		birth_year_min: Minimum plausible birth year.
		impute_exclude_columns: Extra columns excluded from imputation.
	"""

	input_path: Path = Path("data/raw/sinan_esqu_raw.parquet")
	output_path: Path = Path("data/processed/sinan_esqu_processed.parquet")

	apply_positive_filter: bool = True
	positive_filter_column: str = "AN_QUALI"
	positive_filter_value: str = "1"
	cohort_drop_columns: Tuple[str, ...] = ()
	cohort_drop_values: Tuple[str, ...] = ()
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
	apply_outlier_filter: bool = True
	outlier_iqr_multiplier: float = 1.5
	outlier_exclude_columns: Tuple[str, ...] = OUTLIER_EXCLUDE_COLUMNS
	post_feature_outlier_columns: Tuple[str, ...] = POST_FEATURE_OUTLIER_COLUMNS

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

	def resolved_immediate_drop_columns(self) -> Tuple[str, ...]:
		"""Return the immediate-drop columns normalized to raw field names."""

		resolved = [
			IMMEDIATE_DROP_COLUMN_ALIASES.get(column, column)
			for column in self.immediate_drop_columns
		]
		return tuple(dict.fromkeys(resolved))

	@classmethod
	def unsupervised_ml(cls, **kwargs: object) -> "PipelineConfig":
		"""Create a config for the non-supervised ML cohort."""

		config_kwargs = dict(kwargs)
		config_kwargs.setdefault(
			"output_path",
			Path("data/processed/sinan_esqu_unsup.parquet"),
		)
		config_kwargs["apply_positive_filter"] = False
		config_kwargs["cohort_drop_columns"] = UNSUPERVISED_COHORT_DROP_COLUMNS
		config_kwargs["cohort_drop_values"] = UNSUPERVISED_COHORT_DROP_VALUES
		config_kwargs["apply_target_filter"] = False
		config_kwargs["impute_exclude_columns"] = ("EVOLUCAO", "AN_QUALI")
		return cls(**config_kwargs)

	@classmethod
	def immediate_only(cls, **kwargs: object) -> "PipelineConfig":
		"""Create a config that keeps only the immediate discard stage."""

		config_kwargs = dict(kwargs)
		config_kwargs["apply_drop_after_features"] = False
		config_kwargs["drop_after_features"] = tuple()
		return cls(**config_kwargs)
