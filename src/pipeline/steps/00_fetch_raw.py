"""Step 00: download raw SINAN data via pysus and save as parquet."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import pysus

from pipeline.config import PipelineConfig


@dataclass(frozen=True)
class Step00Stats:
	"""Metrics collected during raw data download."""

	output_path: Path
	files_downloaded: int
	empty_files: int
	failed_files: int
	rows: int


def fetch_raw(config: PipelineConfig, dis_codes: Iterable[str]) -> Step00Stats:
	"""Download raw SINAN data and persist it to the input path.

	Args:
		config: Pipeline configuration.
		dis_codes: Disease codes used in pysus download.

	Returns:
		Step00Stats with download summary.
	"""

	codes = [code for code in dis_codes if code]
	if not codes:
		raise ValueError("Informe ao menos um codigo de doenca")

	sinan = pysus.SINAN().load()
	files = sinan.get_files(dis_code=codes)
	parquets = sinan.download(files)

	dfs: list[pd.DataFrame] = []
	empty_files = 0
	failed_files = 0

	for p in parquets:
		try:
			df_chunk = p.to_dataframe()
			if not df_chunk.empty:
				dfs.append(df_chunk)
			else:
				empty_files += 1
				print(f"Skipping empty DataFrame from {p}")
		except ValueError as exc:
			failed_files += 1
			print(f"Error processing {p}: {exc}. Skipping this file.")
		except Exception as exc:
			failed_files += 1
			print(f"An unexpected error occurred while processing {p}: {exc}. Skipping this file.")

	if dfs:
		df_raw = pd.concat(dfs, ignore_index=True)
	else:
		print("Warning: No valid dataframes were processed. File will be empty.")
		df_raw = pd.DataFrame()

	output_path = config.input_path
	output_path.parent.mkdir(parents=True, exist_ok=True)
	df_raw.to_parquet(output_path, index=False)

	return Step00Stats(
		output_path=output_path,
		files_downloaded=len(parquets),
		empty_files=empty_files,
		failed_files=failed_files,
		rows=len(df_raw),
	)
