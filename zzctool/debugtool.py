import time

_t0_cached = {}
_t1_cached = {}
_t1_cached_last = {}


def ts_count_start(name):
    _t0_cached[name] = time.time()


def ts_count_end(name):
    if name in _t1_cached:
        _t1_cached_last[name] = _t1_cached[name]
        _t1_cached[name] = time.time()
        ts_d = _t1_cached[name] - _t0_cached[name]
        ts_total = _t1_cached[name] - _t1_cached_last[name]
        print(f'[{name}] {ts_d:.6f}, {ts_total:.6f} -> {ts_d / ts_total:.4f}')
    else:
        _t1_cached[name] = time.time()
