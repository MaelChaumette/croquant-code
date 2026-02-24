import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from matplotlib import rc

C_LIST = sns.color_palette("colorblind", 8)
C_LIST_DARK = sns.color_palette("dark", 8)


def configure_plt(fontsize=12):
    rc('font', **{'family': 'sans-serif',
                  'sans-serif': ['Computer Modern Roman']})
    params = {'axes.labelsize': fontsize,
              'font.size': fontsize,
              'legend.fontsize': fontsize,
              'xtick.labelsize': fontsize - 2,
              'ytick.labelsize': fontsize - 2,
              'text.usetex': True,
              'figure.figsize': (8, 6)}
    plt.rcParams.update(params)

    sns.set_palette('colorblind')
    sns.set_style("ticks")
