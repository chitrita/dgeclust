from __future__ import division

import numpy as np
import numpy.random as rn

import dgeclust.stats as st

########################################################################################################################


def _compute_loglik(alpha, beta, counts, lib_sizes):
    """Computes the log-likelihood of each element of counts for each element of phi and mu"""

    ## prepare data
    counts = counts.T
    counts = counts[:, :, np.newaxis]

    lib_sizes = lib_sizes.T
    lib_sizes = lib_sizes[:, :, np.newaxis]

    ## return
    return st.bbinomln(counts, lib_sizes, alpha, beta)


########################################################################################################################


def compute_loglik(j, data, state):
    """Computes the log-likelihood of each element of counts for each element of theta"""

    ## read data
    group = data.groups.values()[j]
    counts = data.counts[group].values
    lib_sizes = data.lib_sizes[group].values

    ## read theta
    alpha = state.pars[:, 0]
    beta = state.pars[:, 1]

    ## return
    return _compute_loglik(alpha, beta, counts, lib_sizes)

########################################################################################################################


def compute_logprior(alpha, beta, mu_alpha, s2_alpha, mu_beta, s2_beta):
    """Computes the log-density of the prior of theta"""

    ## compute log-priors for phi and mu
    logprior_alpha = st.lognormalln(alpha, mu_alpha, s2_alpha)
    logprior_beta = st.lognormalln(beta, mu_beta, s2_beta)

    ## return
    return logprior_alpha + logprior_beta

########################################################################################################################


def sample_prior(size, mu_alpha, s2_alpha, mu_beta, s2_beta):
    """Samples alpha and beta from their priors, log-normal in both cases"""

    ## sample alpha and beta
    alpha = np.exp(rn.randn(size, 1) * np.sqrt(s2_alpha) + mu_alpha)
    beta = np.exp(rn.randn(size, 1) * np.sqrt(s2_beta) + mu_beta)

    ## return
    return np.hstack((alpha, beta))
    
########################################################################################################################


def sample_hpars(pars, *args, **kargs):
    """Samples the mean and var of the log-normal from the posterior, given phi"""

    alpha = np.log(pars[:, 0])
    beta = np.log(pars[:, 1])

    ## compute S1_phi, S2_phi, S1_mu, S2_mu and n
    n = alpha.size

    s1_alpha = alpha.sum()
    s1_beta = beta.sum()

    s2_alpha = np.sum(alpha**2)
    s2_beta = np.sum(beta**2)

    mu_alpha, s2_alpha = st.sample_normal_mean_var(s1_alpha, s2_alpha, n)
    mu_beta, s2_beta = st.sample_normal_mean_var(s1_beta, s2_beta, n)

    ## return
    return mu_alpha, s2_alpha, mu_beta, s2_beta

########################################################################################################################


def sample_posterior(idx, data, state):
    """Sample alpha and beta from their posterior, using Metropolis"""

    ## fetch all data points that belong to cluster idx
    groups = data.groups.values()
    counts = [data.counts[group][zz == idx].values for group, zz in zip(groups, state.zz)]
    lib_sizes = [data.lib_sizes[group].values for group in groups]

    ## read theta
    alpha, beta = state.pars[idx]

    ## propose theta
    alpha_, beta_ = (alpha, beta) * np.exp(0.01 * rn.randn(2))

    ## compute log-likelihoods
    loglik = np.sum([_compute_loglik(alpha, beta, cnts, libszs).sum() for cnts, libszs in zip(counts, lib_sizes)])
    loglik_ = np.sum([_compute_loglik(alpha_, beta_, cnts, libszs).sum() for cnts, libszs in zip(counts, lib_sizes)])

    ## compute log-priors
    logprior = compute_logprior(alpha, beta, *state.hpars)
    logprior_ = compute_logprior(alpha_, beta_, *state.hpars)

    ## compute log-posteriors
    logpost = loglik + logprior
    logpost_ = loglik_ + logprior_

    ## do Metropolis step
    if (logpost_ > logpost) or (rn.rand() < np.exp(logpost_ - logpost)):    # do Metropolis step
        alpha = alpha_
        beta = beta_

    ## return
    return alpha, beta

########################################################################################################################
