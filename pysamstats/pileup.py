# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division
import functools


import pysamstats.opt as opt
import pysamstats.util as util
import pysamstats.config as config


_doc_params = """
    Parameters
    ----------
    type : string
        Statistics type. One of "coverage", "coverage_strand", "coverage_ext",
        "coverage_ext_strand", "variation", "variation_strand", "tlen", "tlen_strand", "mapq",
        "mapq_strand", "baseq", "baseq_strand", "baseq_ext", "baseq_ext_strand", "coverage_gc".
    alignmentfile : pysam.AlignmentFile or string
        SAM or BAM file or file path.
    fafile : pysam.FastaFile or string
        FASTA file or file path, only required for some statistics types.
    chrom : string
        Chromosome/contig.
    start : int
        Start position.
    end : int
        End position.
    one_based : bool
        Coordinate system, False if zero-based (default), True if one-based.
    truncate : bool
        If True, truncate output to selected region.
    pad : bool
        If True, emit records for every position, even if no reads are aligned.
    max_depth : int
        Maximum depth to allow in pileup column.
    window_size : int
        Window size to use for percent GC calculation (only applies to coverage_gc).
    window_offset : int
        Distance from window start to record position (only applies to coverage_gc)."""


# noinspection PyShadowingBuiltins
def stat_pileup(type,
                alignmentfile,
                fafile=None,
                chrom=None,
                start=None,
                end=None,
                one_based=False,
                truncate=False,
                pad=False,
                max_depth=8000,
                window_size=300,
                window_offset=None):
    """Generate statistics per genome position, based on read pileups.
    {params}

    Returns
    -------
    recs : iterator
        An iterator yielding dict objects, where each dict holds data for a single genome position.

    """

    try:
        if type == 'coverage_gc':
            # special case needed to handle window parameters
            rec, rec_pad = opt.frecs_coverage_gc(window_size=window_size,
                                                 window_offset=window_offset)
        else:
            rec, rec_pad = frecs_pileup[type]
    except KeyError:
        raise ValueError('unsupported statistics type: %r' % type)

    return opt.iter_pileup(rec, rec_pad, alignmentfile=alignmentfile, fafile=fafile, chrom=chrom,
                           start=start, end=end, one_based=one_based, truncate=truncate, pad=pad,
                           max_depth=max_depth)


stat_pileup.__doc__ = stat_pileup.__doc__.format(params=_doc_params)


# noinspection PyShadowingBuiltins
def load_pileup(type,
                alignmentfile,
                fafile=None,
                chrom=None,
                start=None,
                end=None,
                one_based=False,
                truncate=False,
                pad=False,
                max_depth=8000,
                window_size=300,
                window_offset=None,
                dtype=None,
                fields=None):
    """Load statistics per genome position, based on read pileups.
    {params}
    dtype : dtype
        Override default dtype.
    fields : string or list of strings
        Select a subset of fields to load.

    Returns
    -------
    ra : numpy structured array
        A structured array.

    """

    stat = functools.partial(stat_pileup, type)
    try:
        default_dtype = getattr(config, 'dtype_' + type)
    except AttributeError:
        raise ValueError('unsupported statistics type: %r' % type)

    return util.load_stats(stat, user_dtype=dtype, default_dtype=default_dtype,
                           user_fields=fields, alignmentfile=alignmentfile, fafile=fafile,
                           chrom=chrom, start=start, end=end, one_based=one_based,
                           truncate=truncate, pad=pad, max_depth=max_depth, window_size=window_size,
                           window_offset=window_offset)


load_pileup.__doc__ = load_pileup.__doc__.format(params=_doc_params)


frecs_pileup = {
    'coverage': (opt.rec_coverage, opt.rec_coverage_pad),
    'coverage_strand': (opt.rec_coverage_strand, opt.rec_coverage_strand_pad),
    'coverage_ext': (opt.rec_coverage_ext, opt.rec_coverage_ext_pad),
    'coverage_ext_strand': (opt.rec_coverage_ext_strand, opt.rec_coverage_ext_strand_pad),
    'variation': (opt.rec_variation, opt.rec_variation_pad),
    'variation_strand': (opt.rec_variation_strand, opt.rec_variation_strand_pad),
    'tlen': (opt.rec_tlen, opt.rec_tlen_pad),
    'tlen_strand': (opt.rec_tlen_strand, opt.rec_tlen_strand_pad),
    'mapq': (opt.rec_mapq, opt.rec_mapq_pad),
    'mapq_strand': (opt.rec_mapq_strand, opt.rec_mapq_strand_pad),
    'baseq': (opt.rec_baseq, opt.rec_baseq_pad),
    'baseq_strand': (opt.rec_baseq_strand, opt.rec_baseq_strand_pad),
    'baseq_ext': (opt.rec_baseq_ext, opt.rec_baseq_ext_pad),
    'baseq_ext_strand': (opt.rec_baseq_ext_strand, opt.rec_baseq_ext_strand_pad),
}


# backwards compatibility
#########################


_stat_doc_lines = stat_pileup.__doc__.split('\n')
_load_doc_lines = load_pileup.__doc__.split('\n')
# strip "type" parameter
_stat_doc = '\n'.join(_stat_doc_lines[:4] + _stat_doc_lines[8:])
_load_doc = '\n'.join(_load_doc_lines[:4] + _stat_doc_lines[8:])


def _specialize(type):
    stat = functools.partial(stat_pileup, type)
    stat.__doc__ = _stat_doc
    stat.__name__ = 'stat_' + type
    load = functools.partial(load_pileup, type)
    load.__doc__ = _load_doc
    load.__name__ = 'load_' + type
    return stat, load


# named functions
stat_coverage, load_coverage = _specialize('coverage')
stat_coverage_strand, load_coverage_strand = _specialize('coverage_strand')
stat_coverage_ext, load_coverage_ext = _specialize('coverage_ext')
stat_coverage_ext_strand, load_coverage_ext_strand = _specialize('coverage_ext_strand')
stat_variation, load_variation = _specialize('variation')
stat_variation_strand, load_variation_strand = _specialize('variation_strand')
stat_tlen, load_tlen = _specialize('tlen')
stat_tlen_strand, load_tlen_strand = _specialize('tlen_strand')
stat_mapq, load_mapq = _specialize('mapq')
stat_mapq_strand, load_mapq_strand = _specialize('mapq_strand')
stat_baseq, load_baseq = _specialize('baseq')
stat_baseq_strand, load_baseq_strand = _specialize('baseq_strand')
stat_baseq_ext, load_baseq_ext = _specialize('baseq_ext')
stat_baseq_ext_strand, load_baseq_ext_strand = _specialize('baseq_ext_strand')
stat_coverage_gc, load_coverage_gc = _specialize('coverage_gc')
