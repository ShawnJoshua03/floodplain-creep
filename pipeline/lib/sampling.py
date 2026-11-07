"""Draw the validation sample of cells inside the flood zone."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import numpy.typing as npt

RANDOM = "random"
FLAGGED = "flagged"


@dataclass(frozen=True)
class SampledCell:
    cell_id: str
    row: int
    col: int
    sample_type: str
    change: float


@dataclass(frozen=True)
class SampleDesign:
    n_random: int
    n_flagged: int
    flag_threshold: float
    seed: int


def make_cell_id(row: int, col: int) -> str:
    return f"r{row:03d}c{col:03d}"


def draw_sample(
    eligible: npt.NDArray[np.bool_], change: npt.NDArray[np.float64], design: SampleDesign
) -> list[SampledCell]:
    """Random cells from the eligible set, plus extra cells the algorithm flags as an increase.

    The result is shuffled so the order carries no information about the sample type.
    """
    rng = np.random.default_rng(design.seed)
    positions = np.argwhere(eligible)
    if len(positions) < design.n_random:
        raise ValueError(f"Only {len(positions)} eligible cells, need {design.n_random}")
    picked = rng.choice(len(positions), size=design.n_random, replace=False)
    chosen = {(int(positions[i][0]), int(positions[i][1])) for i in picked}
    pool = [(int(r), int(c)) for r, c in positions if change[r, c] >= design.flag_threshold and (r, c) not in chosen]
    if len(pool) < design.n_flagged:
        raise ValueError(f"Only {len(pool)} flagged cells left, need {design.n_flagged}")
    extra = [pool[i] for i in rng.choice(len(pool), size=design.n_flagged, replace=False)]
    cells = [SampledCell(make_cell_id(r, c), r, c, RANDOM, float(change[r, c])) for r, c in sorted(chosen)]
    cells += [SampledCell(make_cell_id(r, c), r, c, FLAGGED, float(change[r, c])) for r, c in extra]
    order = rng.permutation(len(cells))
    return [cells[i] for i in order]


def flagged_pool_size(eligible: npt.NDArray[np.bool_], change: npt.NDArray[np.float64], flag_threshold: float) -> int:
    return int((eligible & (change >= flag_threshold)).sum())


def sampling_note(design: SampleDesign, eligible_cells: int, flagged_cells: int) -> str:
    return (
        f"Cells are 100 m squares inside the modeled 100-year flood zone and inside a kept neighborhood "
        f"({eligible_cells} cells). The sample has {design.n_random} cells drawn at random, plus "
        f"{design.n_flagged} extra cells drawn at random from the {flagged_cells} cells where the algorithm "
        f"shows an increase of at least {design.flag_threshold:g} buildings between the first and last year, "
        f"so that enough real increases are present. Because of this oversampling, precision and recall describe "
        f"this sample, not the whole city. Random seed {design.seed}."
    )
