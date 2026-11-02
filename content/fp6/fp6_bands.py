# Copyright (C) 2026 Harald Pretl and co-authors (harald.pretl@jku.at)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Frequency bands of the Fairphone (Gen. 6), shared by the figures of the
appendix in content/fp6/.

Band edges in MHz from 3GPP TS 36.101 (LTE) and TS 38.101-1 (NR FR1); NR
bands n1 ... n71 reuse the edges of the LTE band with the same number.
"""

# LTE FDD bands: (UL low, UL high, DL low, DL high)
FDD = {
    1:  (1920, 1980, 2110, 2170),
    2:  (1850, 1910, 1930, 1990),
    3:  (1710, 1785, 1805, 1880),
    4:  (1710, 1755, 2110, 2155),
    5:  (824, 849, 869, 894),
    7:  (2500, 2570, 2620, 2690),
    8:  (880, 915, 925, 960),
    12: (699, 716, 729, 746),
    17: (704, 716, 734, 746),
    20: (832, 862, 791, 821),
    25: (1850, 1915, 1930, 1995),
    26: (814, 849, 859, 894),
    28: (703, 748, 758, 803),
    66: (1710, 1780, 2110, 2200),
    71: (663, 698, 617, 652),
}

# supplemental downlink (DL only)
SDL = {32: (1452, 1496)}

# TDD bands (LTE and NR): (low, high)
TDD = {
    'B38': (2570, 2620),
    'B40': (2300, 2400),
    'B41': (2496, 2690),
    'B42': (3400, 3600),
    'n77': (3300, 4200),
    'n78': (3300, 3800),
}

# band groups as used in the analysis of the RF front-end
GROUPS = {
    'LB':  (617, 960),
    'MB':  (1452, 2200),
    'HB':  (2300, 2690),
    'UHB': (3300, 5000),
}

# other receivers: GNSS center frequencies, the GNSS bands occupied by GPS,
# Galileo, BeiDou and GLONASS (L5: 1176.45 MHz +/- 10.23 MHz; L1: from BeiDou
# B1I at 1561.098 MHz - 2.046 MHz to GLONASS L1 at 1605.9 MHz), and Wi-Fi bands
GNSS = {'L5': 1176.45, 'L1': 1575.42}
GNSS_BANDS = {'L5': (1166.22, 1186.68), 'L1': (1559.05, 1605.89)}
WIFI = {'2.4 GHz': (2400, 2483.5), '5 GHz': (5150, 5895), '6 GHz': (5925, 7125)}


def duplex_gap(band):
    """Gap between UL and DL of an FDD band in MHz (positive)."""
    ul_lo, ul_hi, dl_lo, dl_hi = FDD[band]
    return dl_lo - ul_hi if dl_lo > ul_hi else ul_lo - dl_hi


def center(band):
    """Center frequency of the complete FDD band (UL and DL) in MHz."""
    ul_lo, ul_hi, dl_lo, dl_hi = FDD[band]
    return (min(ul_lo, dl_lo) + max(ul_hi, dl_hi)) / 2


def rx_bands():
    """All receive bands of the phone as a list of (name, low, high) in MHz."""
    rx = [(f'B{b} DL', v[2], v[3]) for b, v in FDD.items()]
    rx += [(f'B{b} DL', lo, hi) for b, (lo, hi) in SDL.items()]
    rx += [(name, lo, hi) for name, (lo, hi) in TDD.items()]
    rx += [(f'GNSS {name}', lo, hi) for name, (lo, hi) in GNSS_BANDS.items()]
    rx += [(f'Wi-Fi {name}', lo, hi) for name, (lo, hi) in WIFI.items()]
    return rx


def mix(m, band_a, n, band_b):
    """Frequency range of |m f_a + n f_b| for f_a, f_b in the given ranges."""
    corners = [abs(m * fa + n * fb_) for fa in band_a for fb_ in band_b]
    lo, hi = min(corners), max(corners)
    # a difference product passes through zero if the ranges overlap
    if m * n < 0 and (m * band_a[0] + n * band_b[1]) * (m * band_a[1] + n * band_b[0]) < 0:
        lo = 0
    return lo, hi


def group(f):
    """Band group of a frequency in MHz, or None."""
    for name, (lo, hi) in GROUPS.items():
        if lo <= f <= hi:
            return name
    return None
