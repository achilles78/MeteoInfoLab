# coding=utf-8
#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2017-3-9
# Purpose: MeteoInfoLab stats module
# Note: Jython
#-----------------------------------------------------

from org.meteoinfo.math.stats import StatsUtil
from org.meteoinfo.data import ArrayMath, ArrayUtil
from ucar.ma2 import Array

from mipylib.numeric.miarray import MIArray

__all__ = [
    'cov','pearsonr','spearmanr','kendalltau'
    ]

def cov(m, y=None, rowvar=True, bias=False):
    '''
    Estimate a covariance matrix.
    
    :param m: (*array_like*) A 1-D or 2-D array containing multiple variables and observations.
    :param y: (*array_like*) Optional. An additional set of variables and observations. y has the same form as 
        that of m.
    :param rowvar: (*boolean*) If ``rowvar`` is True (default), then each row represents a variable, with 
        observations in the columns. Otherwise, the relationship is transposed: each column represents a 
        variable, while the rows contain observations.
    :param bias: (*boolean*) Default normalization (False) is by (N - 1), where N is the number of observations 
        given (unbiased estimate). If bias is True, then normalization is by N.
    
    :returns: Covariance.
    '''
    if isinstance(m, list):
        m = MIArray(ArrayUtil.array(m))
    if rowvar == True and m.ndim == 2:
        m = m.T
    if y is None:        
        r = StatsUtil.cov(m.asarray(), not bias)
        if isinstance(r, Array):
            return MIArray(r)
        else:
            return r
    else:
        if isinstance(y, list):
            y = MIArray(ArrayUtil.array(y))
        if rowvar == True and y.ndim == 2:
            y = y.T
        r = StatsUtil.cov(m.asarray(), y.asarray(), not bias)
        return MIArray(r)
        
def pearsonr(x, y):
    '''
    Calculates a Pearson correlation coefficient and the p-value for testing non-correlation.

    The Pearson correlation coefficient measures the linear relationship between two datasets. 
    Strictly speaking, Pearson’s correlation requires that each dataset be normally distributed, 
    and not necessarily zero-mean. Like other correlation coefficients, this one varies between 
    -1 and +1 with 0 implying no correlation. Correlations of -1 or +1 imply an exact linear 
    relationship. Positive correlations imply that as x increases, so does y. Negative 
    correlations imply that as x increases, y decreases.

    The p-value roughly indicates the probability of an uncorrelated system producing datasets 
    that have a Pearson correlation at least as extreme as the one computed from these datasets. 
    The p-values are not entirely reliable but are probably reasonable for datasets larger than 
    500 or so.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    
    :returns: Pearson’s correlation coefficient and 2-tailed p-value.
    '''
    if isinstance(x, list):
        x = MIArray(ArrayUtil.array(x))
    if isinstance(y, list):
        y = MIArray(ArrayUtil.array(y))
    r = StatsUtil.pearsonr(x.asarray(), y.asarray())
    return r[0], r[1]
    
def kendalltau(x, y):
    '''
    Calculates Kendall's tau, a correlation measure for ordinal data.
    
    Kendall's tau is a measure of the correspondence between two rankings.
    Values close to 1 indicate strong agreement, values close to -1 indicate
    strong disagreement.  This is the 1945 "tau-b" version of Kendall's
    tau [2]_, which can account for ties and which reduces to the 1938 "tau-a"
    version [1]_ in absence of ties.
    
    :param x: (*array_like*) x data array.
    :param y: (*array_like*) y data array.
    
    :returns: Correlation.
    
    Notes
    -----
    The definition of Kendall's tau that is used is [2]_::
      tau = (P - Q) / sqrt((P + Q + T) * (P + Q + U))
    where P is the number of concordant pairs, Q the number of discordant
    pairs, T the number of ties only in `x`, and U the number of ties only in
    `y`.  If a tie occurs for the same pair in both `x` and `y`, it is not
    added to either T or U.
    References
    ----------
    .. [1] Maurice G. Kendall, "A New Measure of Rank Correlation", Biometrika
           Vol. 30, No. 1/2, pp. 81-93, 1938.
    .. [2] Maurice G. Kendall, "The treatment of ties in ranking problems",
           Biometrika Vol. 33, No. 3, pp. 239-251. 1945.
    .. [3] Gottfried E. Noether, "Elements of Nonparametric Statistics", John
           Wiley & Sons, 1967.
    .. [4] Peter M. Fenwick, "A new data structure for cumulative frequency
           tables", Software: Practice and Experience, Vol. 24, No. 3,
           pp. 327-336, 1994.
    '''
    if isinstance(x, list):
        x = MIArray(ArrayUtil.array(x))
    if isinstance(y, list):
        y = MIArray(ArrayUtil.array(y))
    r = StatsUtil.kendalltau(x.asarray(), y.asarray())
    return r

def spearmanr(m, y=None, axis=0):
    '''
    Calculates a Spearman rank-order correlation coefficient.
    
    The Spearman correlation is a nonparametric measure of the monotonicity of the relationship 
    between two datasets. Unlike the Pearson correlation, the Spearman correlation does not 
    assume that both datasets are normally distributed. Like other correlation coefficients, 
    this one varies between -1 and +1 with 0 implying no correlation. Correlations of -1 or +1 
    imply an exact monotonic relationship. Positive correlations imply that as x increases, so 
    does y. Negative correlations imply that as x increases, y decreases.
    
    :param m: (*array_like*) A 1-D or 2-D array containing multiple variables and observations.
    :param y: (*array_like*) Optional. An additional set of variables and observations. y has the same form as 
        that of m.
    :param axis: (*int*) If axis=0 (default), then each column represents a variable, with 
        observations in the rows. If axis=1, the relationship is transposed: each row represents 
        a variable, while the columns contain observations..
    
    :returns: Spearman correlation matrix.
    '''
    if isinstance(m, list):
        m = MIArray(ArrayUtil.array(m))
    if axis == 1 and m.ndim == 2:
        m = m.T
    if y is None:        
        r = StatsUtil.spearmanr(m.asarray())
        if isinstance(r, Array):
            return MIArray(r)
        else:
            return r
    else:
        if isinstance(y, list):
            y = MIArray(ArrayUtil.array(y))
        if axis == 1 and y.ndim == 2:
            y = y.T
        r = StatsUtil.spearmanr(m.asarray(), y.asarray())
        return MIArray(r)