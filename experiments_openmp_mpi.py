import argparse

from best_comparison import main as run_best_comparison

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Deprecated entrypoint. Use best_comparison.py options."
    )
    parser.parse_args()
    run_best_comparison()
