from __future__ import division

import os
import sys
import multiprocessing as mp
import argparse as ap
import numpy as np

import dgeclust.gibbs.post as post
import dgeclust.config as cfg

########################################################################################################################


## parse command-line arguments
parser = ap.ArgumentParser(prog='simmat', description='Compute similarity matrix')
parser.add_argument('-i', type=str, dest='indir', help='input directory', default=cfg.fnames['clust'])
parser.add_argument('-t0', type=int, dest='t0', help='first sample to process', default=cfg.post['t0'])
parser.add_argument('-tend', type=int, dest='tend', help='last sample to process', default=cfg.post['tend'])
parser.add_argument('-dt', type=int, dest='dt', help='process every dt samples', default=cfg.post['dt'])
parser.add_argument('-c', dest='comp', help='compare features, not groups', action='store_true',
                    default=cfg.post['compareFeatures'])
parser.add_argument('-o', type=str, dest='outfile', help='output file', default=cfg.fnames['simmat'])
parser.add_argument('-r', type=int, dest='nthreads', help='number of threads', default=cfg.nthreads)

args = parser.parse_args()

args.cc = os.path.join(args.indir, cfg.fnames['cc'])   # input directory
args.nthreads = args.nthreads if args.nthreads > 0 else mp.cpu_count()

########################################################################################################################

## use multiple cores
pool = mp.Pool(processes=args.nthreads)

## compute similarity matrix ...
simmat, nsamples = post.compute_similarity_matrix(args.cc, args.t0, args.tend, args.dt, args.comp, pool)
print >> sys.stderr, '{0} samples processed from directory "{1}"'.format(nsamples, args.cc)

## ... and save to output file
np.savetxt(args.outfile, simmat, delimiter='\t')

########################################################################################################################
