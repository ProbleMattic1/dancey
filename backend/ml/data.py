import json, numpy as np, torch, random
from pathlib import Path
from .labels import rasterize_segments

class SequenceDataset(torch.utils.data.Dataset):
    def __init__(self, index_file, window=96, hop=48, aug=True):
        self.index = [json.loads(l) for l in Path(index_file).read_text().splitlines()]
        self.window, self.hop, self.aug = window, hop, aug

    def __len__(self): return len(self.index)

    def __getitem__(self, i):
        meta = self.index[i]
        feats = np.load(meta['features_npz'])['Fz'].astype(np.float32)
        labels = json.loads(Path(meta['labels_json']).read_text())
        T, F = feats.shape; fps = meta['fps']
        y, b = rasterize_segments(T, fps, labels['segments'], meta['move_to_idx'], meta['other_idx'])
        center = self.window//2 if T<=self.window else random.randint(self.window//2, T-self.window//2)
        a = max(0, center - self.window//2); z = min(T, a + self.window); a = z - self.window
        X = feats[a:z]; Y = y[a:z]; B = b[a:z]
        return torch.from_numpy(X), torch.from_numpy(Y), torch.from_numpy(B)
