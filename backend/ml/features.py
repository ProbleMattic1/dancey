import numpy as np
from scipy.signal import savgol_filter

KP = dict(nose=0, l_shoulder=11, r_shoulder=12, l_elbow=13, r_elbow=14, l_wrist=15, r_wrist=16, l_hip=23, r_hip=24, l_knee=25, r_knee=26, l_ankle=27, r_ankle=28)

def normalize_coords(xy: np.ndarray, conf: np.ndarray, conf_th=0.2, eps=1e-6):
    T,J,_ = xy.shape
    hip_mid = 0.5*(xy[:,KP['l_hip']] + xy[:,KP['r_hip']])
    sh_mid  = 0.5*(xy[:,KP['l_shoulder']] + xy[:,KP['r_shoulder']])
    torso = np.linalg.norm(sh_mid - hip_mid, axis=1, keepdims=True)
    torso = np.maximum(torso, eps)
    xy0 = xy - hip_mid[:,None,:]
    sh_vec = xy[:,KP['r_shoulder']] - xy[:,KP['l_shoulder']]
    theta = np.arctan2(sh_vec[:,1], sh_vec[:,0])
    c, s = np.cos(-theta), np.sin(-theta)
    R = np.stack([np.stack([c,-s],-1), np.stack([s,c],-1)], -2)
    xy_rot = (R[:,None,:,:] @ xy0[:,:,:,None]).squeeze(-1)
    xy_n = xy_rot / torso[:,None,:]
    mask = (conf >= conf_th).astype(np.float32)
    return xy_n, mask

def sg_smooth(arr, w=11, p=3):
    if arr.shape[0] < w: return arr
    return savgol_filter(arr, window_length=w, polyorder=p, axis=0, mode='interp')

def angle(a,b,c, eps=1e-6):
    u = a - b; v = c - b
    u = u / (np.linalg.norm(u,axis=-1,keepdims=True)+eps)
    v = v / (np.linalg.norm(v,axis=-1,keepdims=True)+eps)
    cross = u[...,0]*v[...,1] - u[...,1]*v[...,0]
    dot   = u[...,0]*v[...,0] + u[...,1]*v[...,1]
    return np.arctan2(cross, dot)

def make_features(xy, conf):
    xy, mask = normalize_coords(xy, conf)
    xy = sg_smooth(xy)
    T,J,_ = xy.shape
    feats = []
    L = KP
    ang_elbow_L = angle(xy[:,L['l_shoulder']], xy[:,L['l_elbow']], xy[:,L['l_wrist']])
    ang_elbow_R = angle(xy[:,L['r_shoulder']], xy[:,L['r_elbow']], xy[:,L['r_wrist']])
    ang_knee_L  = angle(xy[:,L['l_hip']], xy[:,L['l_knee']], xy[:,L['l_ankle']])
    ang_knee_R  = angle(xy[:,L['r_hip']], xy[:,L['r_knee']], xy[:,L['r_ankle']])
    feats.extend([ang_elbow_L, ang_elbow_R, ang_knee_L, ang_knee_R])
    v = np.zeros_like(xy); v[1:] = xy[1:] - xy[:-1]
    speed_hands = np.linalg.norm(v[:,[L['l_wrist'],L['r_wrist']]],axis=-1)
    speed_feet  = np.linalg.norm(v[:,[L['l_ankle'],L['r_ankle']]],axis=-1)
    feats.append(speed_hands); feats.append(speed_feet)
    def dist(i,j): return np.linalg.norm(xy[:,i]-xy[:,j],axis=-1)
    d_wrist_head_L = dist(L['l_wrist'], L['nose']); d_wrist_head_R = dist(L['r_wrist'], L['nose'])
    feats.extend([d_wrist_head_L, d_wrist_head_R])
    feats.append(ang_elbow_L - ang_elbow_R); feats.append(ang_knee_L - ang_knee_R)
    energy = np.sum(np.linalg.norm(v,axis=-1),axis=-1,keepdims=True); feats.append(energy)
    F = np.column_stack([f if f.ndim==1 else f.reshape(f.shape[0], -1) for f in feats])
    mu = F.mean(0, keepdims=True); sd = F.std(0, keepdims=True)+1e-6
    Fz = (F - mu)/sd
    return Fz.astype(np.float32), {'mu': mu.squeeze().tolist(), 'sd': sd.squeeze().tolist()}
