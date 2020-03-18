"""
This module contains multiple generation functions for sampling a domain. All
use (and return) a random stream in ``persis_info``, given by the allocation
function.
"""
import numpy as np
from libensemble.tools import libe_return


def uniform_random_sample_with_different_nodes_and_ranks(H, persis_info, gen_specs, _):
    """
    Generates points uniformly over the domain defined by ``gen_specs['user']['ub']`` and
    ``gen_specs['user']['lb']``. Also randomly requests a different ``number_of_nodes``
    and ``ranks_per_node`` to be used in the evaluation of the generated point.

    .. seealso::
        `test_6-hump_camel_with_different_nodes_uniform_sample.py <https://github.com/Libensemble/libensemble/blob/develop/libensemble/tests/regression_tests/test_6-hump_camel_with_different_nodes_uniform_sample.py>`_ # noqa
    """
    ub = gen_specs['user']['ub']
    lb = gen_specs['user']['lb']
    n = len(lb)

    if len(H) == 0:
        b = gen_specs['user']['initial_batch_size']

        H_o = np.zeros(b, dtype=gen_specs['out'])
        for i in range(0, b):
            x = persis_info['rand_stream'].uniform(lb, ub, (1, n))
            H_o['x'][i] = x
            H_o['num_nodes'][i] = 1
            H_o['ranks_per_node'][i] = 16
            H_o['priority'] = 1

    else:
        H_o = np.zeros(1, dtype=gen_specs['out'])
        H_o['x'] = len(H)*np.ones(n)
        H_o['num_nodes'] = np.random.randint(1, gen_specs['user']['max_num_nodes']+1)
        H_o['ranks_per_node'] = np.random.randint(1, gen_specs['user']['max_ranks_per_node']+1)
        H_o['priority'] = 10*H_o['num_nodes']

    return H_o, persis_info


def uniform_random_sample_obj_components(H, persis_info, gen_specs, _):
    """
    Generates points uniformly over the domain defined by ``gen_specs['user']['ub']``
    and ``gen_specs['user']['lb']`` but requests each ``obj_component`` be evaluated
    separately.

    .. seealso::
        `test_chwirut_uniform_sampling_one_residual_at_a_time.py <https://github.com/Libensemble/libensemble/blob/develop/libensemble/tests/regression_tests/test_chwirut_uniform_sampling_one_residual_at_a_time.py>`_ # noqa
    """
    ub = gen_specs['user']['ub']
    lb = gen_specs['user']['lb']

    n = len(lb)
    m = gen_specs['user']['components']
    b = gen_specs['user']['gen_batch_size']

    H_o = np.zeros(b*m, dtype=gen_specs['out'])
    for i in range(0, b):
        x = persis_info['rand_stream'].uniform(lb, ub, (1, n))

        H_o['x'][i*m:(i+1)*m, :] = np.tile(x, (m, 1))
        H_o['priority'][i*m:(i+1)*m] = persis_info['rand_stream'].uniform(0, 1, m)
        H_o['obj_component'][i*m:(i+1)*m] = np.arange(0, m)

        H_o['pt_id'][i*m:(i+1)*m] = len(H)//m+i

    return H_o, persis_info


def uniform_random_sample(H, persis_info, gen_specs, _):
    """
    Generates ``gen_specs['user']['gen_batch_size']`` points uniformly over the domain
    defined by ``gen_specs['user']['ub']`` and ``gen_specs['user']['lb']``.

    .. seealso::
        `test_6-hump_camel_uniform_sampling.py <https://github.com/Libensemble/libensemble/blob/develop/libensemble/tests/regression_tests/test_6-hump_camel_uniform_sampling.py>`_ # noqa
    """
    ub = gen_specs['user']['ub']
    lb = gen_specs['user']['lb']

    n = len(lb)
    b = gen_specs['user']['gen_batch_size']

    H_o = np.zeros(b, dtype=gen_specs['out'])

    H_o['x'] = persis_info['rand_stream'].uniform(lb, ub, (b, n))

    return H_o, persis_info


def latin_hypercube_sample(H, persis_info, gen_specs, _, event_queue):
    """
    Generates ``gen_specs['user']['gen_batch_size']`` in a Latin hypercube sample over
    the domain defined by ``gen_specs['user']['ub']`` and ``gen_specs['user']['lb']``.
    """

    ub = gen_specs['user']['ub']
    lb = gen_specs['user']['lb']

    n = len(lb)
    b = gen_specs['user']['gen_batch_size']

    H_o = np.zeros(b, dtype=gen_specs['out'])

    A = lhs_sample(n, b)

    H_o['x'] = A*(ub-lb)+lb

    # return H_o, persis_info
    libe_return(H_o, persis_info, event_queue)


def lhs_sample(n, k):

    # Generate the intervals and random values
    intervals = np.linspace(0, 1, k+1)
    rand_source = np.random.uniform(0, 1, (k, n))
    rand_pts = np.zeros((k, n))
    sample = np.zeros((k, n))

    # Add a point uniformly in each interval
    a = intervals[:k]
    b = intervals[1:]
    for j in range(n):
        rand_pts[:, j] = rand_source[:, j]*(b-a) + a

    # Randomly perturb
    for j in range(n):
        sample[:, j] = rand_pts[np.random.permutation(k), j]

    return sample
