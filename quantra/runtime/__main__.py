"""`python -m quantra.runtime` — race devices and print the hardware plan.

WHAT THIS DOES
--------------
A zero-argument smoke entry point: build the runtime config, run the CPU-vs-GPU
throughput race, size parallelism to ~80%, and print the decision. This is the
first thing to run in Colab (and the M0 acceptance check) to confirm the box is
configured to train cheaply.

HOW IT SERVES FTMO PASSING
--------------------------
Gives the operator an immediate, honest read on cost/speed before committing to a
training run — so paid GPU time is never wasted on a tiny MLP. Rulebook for the
Risk Doctor: ``docs/MLP_INTERPRETABILITY_LAYER.md`` (infrastructure, not learning).
"""

from __future__ import annotations

from .config import RuntimeConfig, ensure_dirs, in_colab
from .optimizer import plan, print_report
from .utilization_monitor import UtilizationMonitor


def main() -> None:
    ensure_dirs()
    cfg = RuntimeConfig()
    print(f"Environment: {'Google Colab' if in_colab() else 'local'}")
    print(f"Symbols    : {', '.join(cfg.symbols)}")
    print(
        f"Challenge  : target {cfg.challenge.daily_target_pct}% / "
        f"risk {cfg.challenge.daily_risk_pct}% trailing | ftmo_mode={cfg.challenge.ftmo_mode}"
    )

    # Measure utilisation across the benchmark itself so the report reflects a
    # real load, not an idle sample.
    with UtilizationMonitor(interval=0.25) as mon:
        hw = plan(state_dim=cfg.nominal_state_dim, hw=cfg.hardware)
    util = mon.stop()

    print_report(hw)
    print(f"Utilisation during race: {util.render()}")
    print(
        "\nNote: the locked net is a 3x256 MLP (~145 inputs). If the GPU row above "
        "is not >= 1.30x the CPU row, a CPU/free Colab runtime is the cheaper, "
        "faster choice - exactly what the optimizer selected."
    )


if __name__ == "__main__":
    main()
