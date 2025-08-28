import numpy as np

def resample_timewise(seq: np.ndarray, new_len: int) -> np.ndarray:
    T,F = seq.shape
    if T == new_len: return seq
    xs = np.linspace(0, 1, T, dtype=np.float32)
    xi = np.linspace(0, 1, new_len, dtype=np.float32)
    out = np.empty((new_len, F), dtype=seq.dtype)
    for f in range(F):
        out[:,f] = np.interp(xi, xs, seq[:,f])
    return out

def dtw_cost(A: np.ndarray, B: np.ndarray, w: np.ndarray | None = None, band: float = 0.1):
    Ta,F = A.shape; Tb,_ = B.shape
    if w is None: w = np.ones(F, dtype=A.dtype)
    W = w[None,:]
    bandw = int(max(Ta, Tb) * band)
    INF = 1e9
    D = np.full((Ta+1, Tb+1), INF, dtype=A.dtype)
    D[0,0] = 0.0
    for i in range(1, Ta+1):
        jmin = max(1, i - bandw); jmax = min(Tb, i + bandw)
        ai = A[i-1:i]
        for j in range(jmin, jmax+1):
            bj = B[j-1:j]
            d = np.sqrt(np.sum(W * (ai - bj) ** 2))
            D[i,j] = d + min(D[i-1,j-1], D[i-1,j], D[i,j-1])
    return float(D[Ta,Tb]/(Ta+Tb))

def score_segment_against_templates(seg_feats, templates, weights, warp_pct=0.20, band=0.1, alpha=5.0):
    candidates=[]
    for t in templates:
        for scale in [1.0, 1.0-warp_pct, 1.0+warp_pct]:
            Tt = int(round(t['feats'].shape[0]*scale))
            B = resample_timewise(t['feats'], Tt)
            cost = dtw_cost(seg_feats, B, w=weights, band=band)
            candidates.append((t['id'], cost))
    import numpy as np
    costs = np.array([c for _,c in candidates])
    probs = np.exp(-alpha*(costs - costs.min()))
    probs = probs / probs.sum()
    agg = {}
    for (mid,c),p in zip(candidates, probs):
        agg.setdefault(mid, []).append((c,p))
    out=[]
    for mid, lst in agg.items():
        mc = float(np.mean([c for c,_ in lst])); mp = float(np.sum([p for _,p in lst]))
        out.append({'move_id': mid, 'cost': mc, 'prob': mp})
    return sorted(out, key=lambda x: (x['cost'], -x['prob']))[:5]
