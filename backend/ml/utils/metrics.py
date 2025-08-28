def iou_1d(a,b):
    s=max(a[0],b[0]); e=min(a[1],b[1])
    inter=max(0,e-s); union=(a[1]-a[0])+(b[1]-b[0])-inter
    return inter/union if union>0 else 0.0
