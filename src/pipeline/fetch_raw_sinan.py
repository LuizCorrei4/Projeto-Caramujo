"""Download SINAN data via pysus and save as parquet."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pipeline.config import PipelineConfig
from pipeline.steps.step00 import fetch_raw

if __name__ == "__main__" and __package__ is None:
	sys.path.append(str(Path(__file__).resolve().parents[1]))


def _parse_dis_codes(raw: str) -> list[str]:
	return [code.strip() for code in raw.split(",") if code.strip()]


def main() -> None:
	parser = argparse.ArgumentParser(description="Baixa dados do SINAN via pysus e salva em parquet")
	parser.add_argument(
		"--output",
		type=str,
		default="data/sinan_esqu_raw.parquet",
		help="Caminho do parquet bruto",
	)
	parser.add_argument(
		"--dis-code",
		type=str,
		default="ESQU",
		help="Codigos da doenca separados por virgula (ex.: ESQU)",
	)
	args = parser.parse_args()

	output_path = Path(args.output)
	dis_codes = _parse_dis_codes(args.dis_code)
	config = PipelineConfig(input_path=output_path)
	stats = fetch_raw(config, dis_codes)
	print(f"Arquivos baixados: {stats.files_downloaded}")
	print(f"Arquivos vazios ignorados: {stats.empty_files}")
	print(f"Arquivos com erro: {stats.failed_files}")
	print(f"Arquivo salvo: {stats.output_path}")
	print(f"Linhas: {stats.rows:,}")


if __name__ == "__main__":
	main()
