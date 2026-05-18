import matplotlib.pyplot as plt


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
    save_path: str | None = None,
) -> None:
    if not errors_per_hour:
        return
    hours = list(errors_per_hour.keys())
    counts = list(errors_per_hour.values())
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
