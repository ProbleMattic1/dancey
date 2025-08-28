import torch, torch.nn as nn

class TCNBlock(nn.Module):
    def __init__(self, c, k=3, d=1, p=0.1):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv1d(c, c, k, padding=d*(k-1)//2, dilation=d),
            nn.GroupNorm(8, c), nn.ReLU(), nn.Dropout(p),
            nn.Conv1d(c, c, k, padding=d*(k-1)//2, dilation=d),
            nn.GroupNorm(8, c)
        )
        self.act = nn.ReLU()
    def forward(self, x): return self.act(self.net(x) + x)

class TCNHead(nn.Module):
    def __init__(self, in_f, hid=256, classes=51, p=0.1):
        super().__init__()
        self.inp = nn.Conv1d(in_f, hid, 1)
        self.blocks = nn.Sequential(*[TCNBlock(hid, d=d) for d in [1,2,4,8,16,32]])
        self.cls = nn.Conv1d(hid, classes, 1)
        self.bnd = nn.Conv1d(hid, 2, 1)
    def forward(self, x):  # x: [B,L,F]
        x = x.transpose(1,2)      # [B,F,L]
        h = self.blocks(self.inp(x))
        return self.cls(h).transpose(1,2), self.bnd(h).transpose(1,2)
