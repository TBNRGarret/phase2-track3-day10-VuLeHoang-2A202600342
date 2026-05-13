import argparse
import sys
from pathlib import Path

# Add src to sys.path to allow running from root without PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent / "src"))

from reliability_lab.chaos import load_queries, run_simulation
from reliability_lab.config import load_config


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="configs/default.yaml")
    parser.add_argument("--out", default="reports/metrics.json")
    args = parser.parse_args()
    config = load_config(args.config)
    metrics = run_simulation(config, load_queries())
    metrics.write_json(args.out)
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
