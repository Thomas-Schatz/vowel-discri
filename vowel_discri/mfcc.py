# -*- coding: utf-8 -*-
"""
Created on Mon June 10 10:14:04 2019

@author: Thomas Schatz
Adapted from https://github.com/librosa

Compute MFCC coefficients.

Steps:
    Waveform -> pre-emphasis -> STFT with Hanning window 25ms + 10ms -> 128 channels mel power-spectrogram
    using area-normalized triangular filters over 0-8000Hz -> to DB (log-compression) -> type II DCT (PCA)
    -> 13 coefficients -> replace 0-th order coefficient with log-energy or drop it (optional)
    -> perform cepstral mean normalization (optional)

Something we did not implement for now: use energy to replace first MFCC coefficient.

Main differences with librosa default are:
    - no padding of time-series to get first frame centered on t=0
    - signal is pre-emphasized
    - defaults: n_MFCC=13, sr=16000, n_fft=400, hop_length=160
    - works from time-series only
    - allows optional dropping or replacement with log-energy of zeroth-order MFCC coefficient
    - allows optional cepstral mean normalization


Requirements: librosa, numpy, scipy

Usage:
    import soundfile
    y, fs = soundfile.read(filename)
    assert fs == 16000
    coefs = mfcc(y)
    # coefs is a 13 by nb_frames numpy array of MFCCs
"""

import numpy as np
import scipy.fftpack
import scipy.signal as sig
from librosa.core.spectrum import power_to_db, stft
from librosa import filters


def pre_emphasize(y):
    b = [1, -.97]
    a = 1
    zi = sig.lfilter_zi(b, a)
    return sig.lfilter(b, a, y, zi=zi)[0]


def log_energy(y, n_fft=400, hop_length=160):
    power_spectrum = np.abs(stft(y, n_fft=n_fft, hop_length=hop_length, center=False))**2
    log_E = 10*np.log10(sum(power_spectrum))  # in dB
    return log_E


def melspectrogram(y=None, sr=16000, n_fft=400, hop_length=160,
                   power=2.0, **kwargs):
    """Compute a mel-scaled spectrogram.

    If a spectrogram input `S` is provided, then it is mapped directly onto
    the mel basis `mel_f` by `mel_f.dot(S)`.

    If a time-series input `y, sr` is provided, then its magnitude spectrogram
    `S` is first computed, and then mapped onto the mel scale by
    `mel_f.dot(S**power)`.  By default, `power=2` operates on a power spectrum.

    Parameters
    ----------
    y : np.ndarray [shape=(n,)] or None
        audio time-series

    sr : number > 0 [scalar]
        sampling rate of `y`

    n_fft : int > 0 [scalar]
        length of the FFT window

    hop_length : int > 0 [scalar]
        number of samples between successive frames.
        See `librosa.core.stft`

    power : float > 0 [scalar]
        Exponent for the magnitude melspectrogram.
        e.g., 1 for energy, 2 for power, etc.

    kwargs : additional keyword arguments
      Mel filter bank parameters.
      See `librosa.filters.mel` for details.

    Returns
    -------
    S : np.ndarray [shape=(n_mels, t)]
        Mel spectrogram
    """
    # Compute a magnitude spectrogram from input
    S = np.abs(stft(y, n_fft=n_fft, hop_length=hop_length, center=False))**power

    # Build a Mel filter
    mel_basis = filters.mel(sr, n_fft, **kwargs)

    return np.dot(mel_basis, S)


def mfcc(y=None, sr=16000, n_mfcc=13, dct_type=2, norm='ortho', 
         zeroth_coef=None, cep_mean_norm=False, **kwargs):
    """Mel-frequency cepstral coefficients (MFCCs)

    Parameters
    ----------
    y     : np.ndarray [shape=(n,)] or None
        audio time series

    sr    : number > 0 [scalar]
        sampling rate of `y`

    n_mfcc: int > 0 [scalar]
        number of MFCCs to return

    dct_type : None, or {1, 2, 3}
        Discrete cosine transform (DCT) type.
        By default, DCT type-2 is used.

    norm : None or 'ortho'
        If `dct_type` is `2 or 3`, setting `norm='ortho'` uses an ortho-normal
        DCT basis.

        Normalization is not supported for `dct_type=1`.

    kwargs : additional keyword arguments
        Arguments to `melspectrogram`, if operating
        on time series input

    Returns
    -------
    M     : np.ndarray [shape=(n_mfcc, t)]
        MFCC sequence
    """

    # pre-emphasize signal
    y = pre_emphasize(y)

    # compute mel-spectrogram
    S = power_to_db(melspectrogram(y=y, sr=sr, **kwargs))

    # compute MFCCs
    coefs = scipy.fftpack.dct(S, axis=0, type=dct_type, norm=norm)[:n_mfcc]

    if zeroth_coef == 'energy':
        # replace 0th order MFCC coef with log energy
        coefs[0, :] = log_energy(y)
    elif zeroth_coef == 'remove':
        coefs = coefs[1:, :]

    if cep_mean_norm:
        # do cepstral mean normalization
        coefs = coefs - np.mean(coefs, axis=0)

    return coefs
