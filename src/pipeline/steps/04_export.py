"""Step 04: export the final curated dataset."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from pipeline.config import PipelineConfig


@dataclass(frozen=True)
class Step04Stats:
	"""Metrics collected during export."""

	output_path: Path
	rows: int
	columns: int


def export_dataset(df: pd.DataFrame, output_path: Path) -> Path:
	"""Export DataFrame to parquet.

	Args:
		df: DataFrame to persist.
		output_path: Destination path.

	Returns:
		Path to the exported file.
	"""

	output_path.parent.mkdir(parents=True, exist_ok=True)
	df.to_parquet(output_path, index=False)
	return output_path


def export_step(df: pd.DataFrame, config: PipelineConfig) -> Step04Stats:
	"""Run export step and return stats."""

	output_path = export_dataset(df, config.output_path)
	return Step04Stats(
		output_path=output_path,
		rows=len(df),
		columns=len(df.columns),
	)
