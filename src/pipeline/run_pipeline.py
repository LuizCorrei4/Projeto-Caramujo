"""Pipeline entrypoint for SINAN esquistossomose preprocessing."""

from __future__ import annotations

import argparse
import importlib.util
import sys
from pathlib import Path

if __name__ == "__main__" and __package__ is None:
	sys.path.append(str(Path(__file__).resolve().parents[1]))

from pipeline.config import PipelineConfig


def _load_step_module(file_name: str, module_name: str):
	"""Load a step module from a file name inside the steps folder."""

	steps_dir = Path(__file__).parent / "steps"
	module_path = steps_dir / file_name
	if not module_path.exists():
		raise FileNotFoundError(f"Step file nao encontrado: {module_path}")

	spec = importlib.util.spec_from_file_location(module_name, module_path)
	if spec is None or spec.loader is None:
		raise ImportError(f"Falha ao carregar step: {module_path}")
	module = importlib.util.module_from_spec(spec)
	sys.modules[module_name] = module
	spec.loader.exec_module(module)
	return module


def _print_step01(stats) -> None:
	print("\n[Step 01] Load and filter")
	print(f"Registros iniciais: {stats.rows_initial:,}")
	print(f"Apos filtro positivo: {stats.rows_after_positive_filter:,}")
	print(f"Apos filtro alvo valido: {stats.rows_after_target_filter:,}")
	print(f"Apos remover valores do alvo: {stats.rows_after_target_drop:,}")
	print(f"Colunas descartadas (imediato): {len(stats.dropped_immediate_columns)}")
	if stats.dropped_immediate_columns:
		print(list(stats.dropped_immediate_columns))


def _print_step00(stats) -> None:
	print("\n[Step 00] Download raw")
	print(f"Arquivos baixados: {stats.files_downloaded}")
	print(f"Arquivos vazios ignorados: {stats.empty_files}")
	print(f"Arquivos com erro: {stats.failed_files}")
	print(f"Arquivo salvo: {stats.output_path}")
	print(f"Linhas: {stats.rows:,}")


def _print_step02(stats) -> None:
	print("\n[Step 02] Clean and impute")
	print(f"Idades invalidas limpas: {stats.invalid_age_count}")
	print(f"Anos de nascimento invalidos: {stats.invalid_birth_year_count}")
	print(f"AN_QUANT negativo ajustado: {stats.invalid_an_quant_count}")
	print(f"Valores imputados (numericos): {stats.numeric_imputed_values}")
	print(f"Valores imputados (categoricos): {stats.categorical_imputed_values}")
	print(f"Outliers removidos (IQR): {stats.outliers_removed}")
	if stats.outlier_columns:
		print(f"Colunas usadas no IQR: {list(stats.outlier_columns)}")


def _print_step03(stats) -> None:
	print("\n[Step 03] Feature engineering")
	print(f"Features criadas: {list(stats.created_features)}")
	print(f"Colunas removidas apos features: {len(stats.dropped_after_features)}")
	print(f"Outliers removidos (IQR pos-features): {stats.outliers_removed}")
	if stats.outlier_columns:
		print(f"Colunas IQR pos-features: {list(stats.outlier_columns)}")


def _print_step04(stats) -> None:
	print("\n[Step 04] Export")
	print(f"Arquivo salvo: {stats.output_path}")
	print(f"Linhas: {stats.rows:,} | Colunas: {stats.columns}")


def run_pipeline(
	config: PipelineConfig,
	download_raw: bool = False,
	dis_codes: list[str] | None = None,
) -> Path:
	"""Run the preprocessing pipeline end-to-end."""

	if download_raw:
		step00 = _load_step_module("00_fetch_raw.py", "pipeline.steps.step00")
		stats00 = step00.fetch_raw(config, dis_codes or ["ESQU"])
		_print_step00(stats00)

	step01 = _load_step_module("01_load_and_filter.py", "pipeline.steps.step01")
	step02 = _load_step_module("02_clean_and_impute.py", "pipeline.steps.step02")
	step03 = _load_step_module("03_feature_engineering.py", "pipeline.steps.step03")
	step04 = _load_step_module("04_export.py", "pipeline.steps.step04")

	df, stats01 = step01.load_and_filter(config)
	_print_step01(stats01)

	df, stats02 = step02.clean_and_impute(df, config)
	_print_step02(stats02)

	df, stats03 = step03.feature_engineering(df, config)
	_print_step03(stats03)

	stats04 = step04.export_step(df, config)
	_print_step04(stats04)

	return stats04.output_path


def _parse_dis_codes(raw: str) -> list[str]:
	codes = [code.strip() for code in raw.split(",") if code.strip()]
	if not codes:
		raise ValueError("Informe ao menos um codigo em --dis-code")
	return codes


def _parse_args() -> argparse.Namespace:
	default_config = PipelineConfig()
	parser = argparse.ArgumentParser(description="Pipeline de preprocessamento SINAN ESQU")
	parser.add_argument(
		"--input",
		type=str,
		default=str(default_config.input_path),
		help="Caminho do parquet bruto",
	)
	parser.add_argument(
		"--output",
		type=str,
		default=str(default_config.output_path),
		help="Caminho do parquet processado",
	)
	parser.add_argument(
		"--download-raw",
		action="store_true",
		help="Baixa dados via pysus antes de rodar o pipeline",
	)
	parser.add_argument(
		"--dis-code",
		type=str,
		default="ESQU",
		help="Codigos da doenca separados por virgula (ex.: ESQU)",
	)
	parser.add_argument(
		"--no-positive-filter",
		action="store_true",
		help="Desativa filtro de casos positivos",
	)
	parser.add_argument(
		"--positive-column",
		type=str,
		default=default_config.positive_filter_column,
		help="Coluna para filtro de positivos",
	)
	parser.add_argument(
		"--positive-value",
		type=str,
		default=default_config.positive_filter_value,
		help="Valor considerado positivo",
	)
	parser.add_argument(
		"--no-drop-after-features",
		action="store_true",
		help="Desativa descarte apos feature engineering",
	)
	parser.add_argument(
		"--no-target-filter",
		action="store_true",
		help="Desativa filtro baseado no alvo",
	)
	return parser.parse_args()


def _config_from_args(args: argparse.Namespace) -> PipelineConfig:
	return PipelineConfig(
		input_path=Path(args.input),
		output_path=Path(args.output),
		apply_positive_filter=not args.no_positive_filter,
		positive_filter_column=args.positive_column,
		positive_filter_value=args.positive_value,
		apply_drop_after_features=not args.no_drop_after_features,
		apply_target_filter=not args.no_target_filter,
	)


if __name__ == "__main__":
	args = _parse_args()
	config = _config_from_args(args)
	dis_codes = _parse_dis_codes(args.dis_code)
	run_pipeline(config, download_raw=args.download_raw, dis_codes=dis_codes)
