import matplotlib.pyplot as plt

def plot(title: str, x_label: str, y_label: str, title_legend: str, bbox=(0.95, 1) ):
    """sets the parameters for the plot

    Args:
        title (str): the title of the plot
        x_label (str): the x label of the plot
        y_label (str): the y label of the plot
        title_legend (str): the name of the legend
        bbox (tuple, optional): the size of the legend. Defaults to (0.95, 1).
    """
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.ylim(ymin=0)
    plt.xlim(xmin=0)
    plt.title(title)
    plt.legend(title=title_legend, bbox_to_anchor=bbox, loc="upper left")
    plt.show()

def get_measure(task: str, measure_classification: str, measure_regression: str):
    """look for the task and return the str with the measurement

    Args:
        task (str): the task
        measure_classification (str): the string of the classification measurement
        measure_regression (str): the string of the regression measurement

    Returns:
        str: the str of the measurement for the task
    """
    if task == ":tabular_classification":
        return measure_classification
    if task == ":tabular_regression":
        return measure_regression

def divide(n: float, d: float):
    """ devide n and d and returns 0 if the d is 0
    Args:
        n (float): the nominator
        d (float): the devidator

    Returns:
        float: the value of the dividation
    """
    if d == 0:
        return 0
    else:
        return n / d
