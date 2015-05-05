#-----------------------------------------------------
# Author: Yaqiang Wang
# Date: 2014-12-26
# Purpose: MeteoInfo plot module
# Note: Jython
#-----------------------------------------------------

def linspace(start, stop, num=50, endpoint=True, retstep=False, dtype=None):
    """
    Return evenly spaced numbers over a specified interval.

    Returns `num` evenly spaced samples, calculated over the
    interval [`start`, `stop` ].

    The endpoint of the interval can optionally be excluded.

    Parameters
    ----------
    start : scalar
        The starting value of the sequence.
    stop : scalar
        The end value of the sequence, unless `endpoint` is set to False.
        In that case, the sequence consists of all but the last of ``num + 1``
        evenly spaced samples, so that `stop` is excluded.  Note that the step
        size changes when `endpoint` is False.
    num : int, optional
        Number of samples to generate. Default is 50.
    endpoint : bool, optional
        If True, `stop` is the last sample. Otherwise, it is not included.
        Default is True.
    retstep : bool, optional
        If True, return (`samples`, `step`), where `step` is the spacing
        between samples.
    dtype : dtype, optional
        The type of the output array.  If `dtype` is not given, infer the data
        type from the other input arguments.

        .. versionadded:: 1.9.0

    Returns
    -------
    samples : ndarray
        There are `num` equally spaced samples in the closed interval
        ``[start, stop]`` or the half-open interval ``[start, stop)``
        (depending on whether `endpoint` is True or False).
    step : float
        Only returned if `retstep` is True

        Size of spacing between samples.
    """
    
    num = int(num)

    # Convert float/complex array scalars to float, gh-3504 
    start = start * 1.
    stop = stop * 1.

    if dtype is None:
        dtype = result_type(start, stop, float(num))

    if num <= 0:
        return array([], dtype)
    if endpoint:
        if num == 1:
            return array([start], dtype=dtype)
        step = (stop-start)/float((num-1))
        y = _nx.arange(0, num, dtype=dtype) * step + start
        y[-1] = stop
    else:
        step = (stop-start)/float(num)
        y = _nx.arange(0, num, dtype=dtype) * step + start
    if retstep:
        return y.astype(dtype), step
    else:
        return y.astype(dtype)