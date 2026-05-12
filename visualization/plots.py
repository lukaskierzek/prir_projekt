import matplotlib.pyplot as plt

def print_dataframe(
    dataframe,
    rows: int = 10,
):

    print(
        dataframe.head(rows).to_string(index=False)
    )

def plot_series(
        series,
        title: str,
        xlabel: str,
        ylabel: str,
):
    series.plot(kind="bar")

    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)

    plt.tight_layout()

    plt.show()
