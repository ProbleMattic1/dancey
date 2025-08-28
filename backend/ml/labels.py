import numpy as np
def rasterize_segments(T, fps, segs, move_to_idx, other_idx):
    y = np.full((T,), other_idx, dtype=np.int64)
    b = np.zeros((T,2), dtype=np.float32)
    for s in segs:
        a=int(round((s['start_ms']/1000.0)*fps)); z=int(round((s['end_ms']/1000.0)*fps))
        y[a:z]=move_to_idx[s['move_id']]; b[a,0]=1.0; b[z-1,1]=1.0
    return y,b
