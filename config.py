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

# Analysis defaults
DEFAULT_PHRASES = ("ERROR", "WARNING", "INFO")
DEFAULT_LEVELS: tuple[str, ...] = ()
DEFAULT_INPUT_LOG = HADOOP_LOG_2K
DATETIME_INPUT_FORMAT = "%Y-%m-%d %H:%M:%S"
DATE_ONLY_INPUT_FORMAT = "%Y-%m-%d"

# Reports
REPORTS_DIR = PROJECT_ROOT / "reports"
