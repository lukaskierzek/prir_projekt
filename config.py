from pathlib import Path

# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

# Raw log files
HADOOP_LOG_2K = RAW_DATA_DIR / "Hadoop_2k.log"

# Processed CSV files
HADOOP_CSV_2K = (
        PROCESSED_DATA_DIR / "Hadoop_2k_structured.csv"
)

# Visualization
PLOTS_DIR = PROJECT_ROOT / "plots"

# Benchmark
DEFAULT_ROWS_DISPLAY = 10
