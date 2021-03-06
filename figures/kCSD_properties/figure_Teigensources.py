"""
@author: mbejtka
"""

import os
import numpy as np
from figure_properties import *
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import scipy

import targeted_basis as tb

__abs_file__ = os.path.abspath(__file__)


def set_axis(ax, letter=None):
    """
    Formats the plot's caption.

    Parameters
    ----------
    ax: Axes object.
    letter: string
        Caption of the plot.
        Default: None.

    Returns
    -------
    ax: modyfied Axes object.
    """
    ax.text(
        -0.15,
        1.05,
        letter,
        fontsize=18,
        weight='bold',
        transform=ax.transAxes)
    return ax


def make_subplot(ax, true_csd, est_csd, estm_x, title=None, ele_pos=None,
                 xlabel=False, ylabel=False, letter='', t_max=None,
                 est_csd_LC=None, anihilator=None):

    """
    Parameters
    ----------
    ax: Axes object.
    true_csd: numpy array
        Values of generated CSD.
    est_csd: numpy array
        Reconstructed csd.
    estm_x: numpy array
        Locations at which CSD is requested.
    title: string
        Title of the plot.
        Default: None.
    ele_pos: numpy array
        Positions of electrodes.
        Default: None.
    xlabel: string
        Caption of the x axis.
        Default: False.
    ylabel: string
        Caption of the y axis.
        Default: False.
    letter: string
        Caption of the plot.
        Default: ''.
    t_max:
        Default: None.
    est_csd_LC: numpy array
        CSD reconstructed with L-curve method.
        Default: None.

    Returns
    -------
    ax: modyfied Axes object.
    """

    x = np.linspace(0, 1, 100)
    l1 = ax.plot(x, true_csd, label='True CSD', lw=2.)
    if est_csd_LC is not None:
        l2 = ax.plot(estm_x, est_csd, '--', label='Projection', lw=2.)
        l3 = ax.plot(estm_x, est_csd_LC, '.', label='Error', lw=2.)
    else:
        l2 = ax.plot(estm_x, est_csd, '--', label='Projection', lw=2.)
    if anihilator is not None:
        l4 = ax.plot(estm_x, anihilator, '.', label='Anihilator', lw=2.)
    ax.set_xlim([0, 1])
    if xlabel:
        ax.set_xlabel('Depth ($mm$)')
    if ylabel:
        ax.set_ylabel('CSD ($mA/mm$)')
    if title is not None:
        ax.set_title(title)
    if np.max(est_csd) < 1.2:
        ax.set_ylim(-0.2, 1.2)
        s1 = ax.scatter(ele_pos, np.zeros(len(ele_pos))-0.2, 17, 'k', label='Electrodes')
        s1.set_clip_on(False)
    elif np.max(est_csd) < 1.7:
        ax.set_ylim(-10000, 10000)
        s3 = ax.scatter(ele_pos, np.zeros(len(ele_pos))-10000, 17, 'k', label='Electrodes')
        s3.set_clip_on(False)
        ax.set_yticks([-7000, 0, 7000])
    if np.max(est_csd) > 500:
        ax.set_ylim(-7000, 7000)
        s3 = ax.scatter(ele_pos, np.zeros(len(ele_pos))-7000, 17, 'k', label='Electrodes')
        s3.set_clip_on(False)
        ax.set_yticks([-5000, 0, 5000])
    elif np.max(est_csd) > 50:
        ax.set_ylim(-100, 100)
        s2 = ax.scatter(ele_pos, np.zeros(len(ele_pos))-100, 17, 'k', label='Electrodes')
        s2.set_clip_on(False)
        ax.set_yticks([-70, 0, 70])
    ax.set_xticks([0, 0.5, 1])
    set_axis(ax, letter=letter)
    # ax.legend(frameon=False, loc='upper center', ncol=3)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    return ax


def csd_into_eigensource_projection(csd, eigensources):
    orthn = scipy.linalg.orth(eigensources)
    return np.dot(np.dot(csd, orthn), orthn.T)


def calculate_eigensources(cross_kernel, eigenvectors):
    return np.dot(cross_kernel, eigenvectors)


def calculate_projection(csd, k, eigenvectors):
    eigensources = calculate_eigensources(k.k_interp_cross, eigenvectors)
    return csd_into_eigensource_projection(csd, eigensources)


def calculate_diff(csd, projection):
    # return np.abs(csd - projection)/np.max(csd)
    return csd - projection

def calculate_eigenvectors(k):
    eigenvalues, eigenvectors = np.linalg.eigh(k.k_pot + np.identity(k.k_pot.shape[0])
                                                   * k.lambd)
    idx = eigenvalues.argsort()[::-1]
    eigenvalues = eigenvalues[idx]
    eigenvectors = eigenvectors[:, idx]
    return eigenvectors


def generate_figure(R, MU, n_src, true_csd_xlims, total_ele,
                    method='cross-validation', Rs=None, lambdas=None,
                    noise=0):
    """
    Generates figure for targeted basis investigation.

    Parameters
    ----------
    R: float
        Thickness of the groundtruth source.
        Default: 0.2.
    MU: float
        Central position of Gaussian source
        Default: 0.25.
    nr_src: int
        Number of basis sources.
    true_csd_xlims: list
        Boundaries for ground truth space.
    total_ele: int
        Number of electrodes.
    save_path: string
        Directory.
    method: string
        Determines the method of regularization.
        Default: cross-validation.
    Rs: numpy 1D array
        Basis source parameter for crossvalidation.
        Default: None.
    lambdas: numpy 1D array
        Regularization parameter for crossvalidation.
        Default: None.
    noise: float
        Determines the level of noise in the data.
        Default: 0.

    Returns
    -------
    None
    """

    ele_lims = [0, 1.]
    csd_at, true_csd, ele_pos, pots, val = tb.simulate_data(tb.csd_profile,
                                                            true_csd_xlims, R,
                                                            MU, total_ele,
                                                            ele_lims,
                                                            noise=noise)
    print(true_csd.shape)
    fig = plt.figure(figsize=(15, 12))
    widths = [1, 1, 1]
    heights = [1, 1, 1]
    gs = gridspec.GridSpec(3, 3, height_ratios=heights, width_ratios=widths,
                            hspace=0.45, wspace=0.3)

    ax = fig.add_subplot(gs[0, 0])
    xmin = 0
    xmax = 1
    ext_x = 0
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd, obj, eigenvectors)
    error = calculate_diff(true_csd, projection)
    anihilator = calculate_diff(true_csd.reshape(obj.values('CSD').shape), obj.values('CSD'))
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title='Basis limits = [0, 1]', xlabel=False, ylabel=True,
                  letter='A', est_csd_LC=error)

    ax = fig.add_subplot(gs[0, 1])
    xmin = -0.5
    xmax = 1
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    csd_at_2 = np.linspace(-0.5, 1, 150)
    true_csd_2 = tb.csd_profile(csd_at_2, [R, MU])
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_2, obj, eigenvectors)
    error = calculate_diff(true_csd_2, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title='Basis limits = [0, 0.5]', xlabel=False, ylabel=False,
                  letter='B', est_csd_LC=error)

    ax = fig.add_subplot(gs[0, 2])
    xmin = 0
    xmax = 1.5
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src,  h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    csd_at_3 = np.linspace(0., 1.5, 150)
    true_csd_3 = tb.csd_profile(csd_at_3, [R, MU])
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_3, obj, eigenvectors)
    error = calculate_diff(true_csd_3, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title='Basis limits = [0.5, 1]', xlabel=False, ylabel=False,
                  letter='C', est_csd_LC=error)

    ele_lims = [0, 0.5]
#    total_ele = 6
    csd_at, true_csd, ele_pos, pots, val = tb.simulate_data(tb.csd_profile,
                                                            true_csd_xlims, R,
                                                            MU, total_ele,
                                                            ele_lims,
                                                            noise=noise)
    ax = fig.add_subplot(gs[1, 0])
    xmin = 0
    xmax = 1
    ext_x = 0
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd, obj, eigenvectors)
    error = calculate_diff(true_csd, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title=None, xlabel=False, ylabel=True, letter='D', est_csd_LC=error)

    ax = fig.add_subplot(gs[1, 1])
    xmin = -0.5
    xmax = 1
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_2, obj, eigenvectors)
    error = calculate_diff(true_csd_2, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title=None, xlabel=False, ylabel=False, letter='E', est_csd_LC=error)

    ax = fig.add_subplot(gs[1, 2])
    xmin = 0
    xmax = 1.5
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_3, obj, eigenvectors)
    error = calculate_diff(true_csd_3, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title=None, xlabel=False, ylabel=False, letter='F', est_csd_LC=error)

    ele_lims = [0.5, 1.]
    csd_at, true_csd, ele_pos, pots, val = tb.simulate_data(tb.csd_profile,
                                                            true_csd_xlims, R,
                                                            MU, total_ele,
                                                            ele_lims,
                                                            noise=noise)
    ax = fig.add_subplot(gs[2, 0])
    xmin = 0
    xmax = 1
    ext_x = 0
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd, obj, eigenvectors)
    error = calculate_diff(true_csd, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title=None, xlabel=True, ylabel=True, letter='G', est_csd_LC=error)

    ax = fig.add_subplot(gs[2, 1])
    xmin = -0.5
    xmax = 1
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_2, obj, eigenvectors)
    error = calculate_diff(true_csd_2, projection)
    make_subplot(ax, true_csd, projection, obj.estm_x, ele_pos=ele_pos,
                  title=None, xlabel=True, ylabel=False, letter='H', est_csd_LC=error)

    ax = fig.add_subplot(gs[2, 2])
    xmin = 0
    xmax = 1.5
    ext_x = -0.5
    obj = tb.modified_bases(val, pots, ele_pos, n_src, h=0.25,
                            sigma=0.3, gdx=0.01, ext_x=ext_x, xmin=xmin,
                            xmax=xmax, method=method, Rs=Rs, lambdas=lambdas)
    eigenvectors = calculate_eigenvectors(obj)
    projection = calculate_projection(true_csd_3, obj, eigenvectors)
    error = calculate_diff(true_csd_3, projection)
    ax = make_subplot(ax, true_csd, projection, obj.estm_x,
                      ele_pos=ele_pos, title=None, xlabel=True, ylabel=False,
                      letter='I', est_csd_LC=error)
    handles, labels = ax.get_legend_handles_labels()
    fig.legend(handles, labels, loc='lower center', ncol=4, frameon=False)

    fig.savefig(os.path.join('targeted_basis_eigensource_projection' + '.png'), dpi=300)
    plt.show()


if __name__ == '__main__':
    N_SRC = 64
    TRUE_CSD_XLIMS = [0., 1.]
    TOTAL_ELE = 12
    R = 0.2
    MU = 0.25
    method = 'cross-validation'  # L-curve
#    method = 'L-curve'
    Rs = np.array([0.2])
    lambdas = np.zeros(1)
    generate_figure(R, MU, N_SRC, TRUE_CSD_XLIMS, TOTAL_ELE,
                    method=method, Rs=Rs, lambdas=lambdas, noise=0)

