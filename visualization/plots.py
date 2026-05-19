import matplotlib.pyplot as plt
from datetime import datetime


def print_dataframe(
    dataframe,
    rows: int = 10,
):
    print(dataframe.head(rows).to_string(index=False))


def plot_series(
    series,
    title: str,
    xlabel: str,
    ylabel: str,
    save_path: str | None = None,
):
    series.plot(kind="bar")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return
    plt.show()


def plot_errors_per_hour(
    errors_per_hour: dict[str, int],
    title: str = "Errors Per Hour",
    hour_from: str | None = None,
    hour_to: str | None = None,
    max_points: int | None = None,
    save_path: str | None = None,
) -> None:
    if not errors_per_hour:
        print("plot_errors_per_hour: no data to plot (empty errors_per_hour).")
        return

    items = sorted(errors_per_hour.items(), key=lambda x: x[0])

    def parse_hour(value: str) -> datetime:
        return datetime.strptime(value, "%Y-%m-%d %H:00")

    try:
        if hour_from:
            dt_from = parse_hour(hour_from)
            items = [(h, c) for h, c in items if parse_hour(h) >= dt_from]
        if hour_to:
            dt_to = parse_hour(hour_to)
            items = [(h, c) for h, c in items if parse_hour(h) <= dt_to]
    except ValueError as exc:
        raise ValueError(
            "hour_from/hour_to must use format 'YYYY-MM-DD HH:00'"
        ) from exc
    if max_points is not None and max_points > 0:
        items = items[:max_points]
    if not items:
        first_hour = min(errors_per_hour.keys())
        last_hour = max(errors_per_hour.keys())
        print(
            "plot_errors_per_hour: no points after filtering. "
            f"Available range: {first_hour} .. {last_hour}"
        )
        return

    hours = [h for h, _ in items]
    counts = [c for _, c in items]
    plt.figure(figsize=(10, 4))
    plt.bar(hours, counts)
    plt.title(title)
    plt.xlabel("Hour")
    plt.ylabel("Errors")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path)
        plt.close()
        return
    plt.show()
