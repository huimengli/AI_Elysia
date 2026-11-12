# Instrumented mini-training: replicate __main__ data setup exactly, train a few
# thousand steps with constant lr, and log per-step diagnostics to catch when
# and how the network collapses to constant-1 output.
import os
import sys

import numpy as np
import torch

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _t2_train_cn import Model  # noqa: E402
from openwakeword.data import mmap_batch_generator  # noqa: E402

FEAT_DIR = r"openWakeWord\output\aili_xiya_v0.1"
N_STEPS = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
LR = float(sys.argv[2]) if len(sys.argv) > 2 else 1e-4
MODE = sys.argv[3] if len(sys.argv) > 3 else "triple"  # triple (32p+64n, current yaml) | balanced (32p+32n)

pos_train = os.path.join(FEAT_DIR, "positive_features_train.npy")
neg_train = os.path.join(FEAT_DIR, "negative_features_train.npy")
pos_test = np.load(os.path.join(FEAT_DIR, "positive_features_test.npy"))
neg_test = np.load(os.path.join(FEAT_DIR, "negative_features_test.npy"))

# feature statistics
posf = np.load(pos_train)
negf = np.load(neg_train)
print(f"pos train: {posf.shape} mean={posf.mean():.4f} std={posf.std():.4f}")
print(f"neg train: {negf.shape} mean={negf.mean():.4f} std={negf.std():.4f}")

# correlation of class means (are the two classes separable at all?)
diff = posf.reshape(posf.shape[0], -1).mean(0) - negf.reshape(negf.shape[0], -1).mean(0)
print(f"feature-mean |diff| L2={np.abs(diff).sum():.4f}  max|diff|={np.abs(diff).max():.4f}")

# same transform as __main__ (n = 27 frames)
def f(x, n=27):
    if n > x.shape[1] or n < x.shape[1]:
        x = np.vstack(x)
        new_batch = np.array([x[i:i+n, :] for i in range(0, x.shape[0]-n, n)])
    else:
        return x
    return new_batch

if MODE == "balanced":
    files = {"positive": pos_train, "adversarial_negative": neg_train}
else:  # triple: current yaml layout (negative + adversarial both -> same file)
    files = {"negative": neg_train, "positive": pos_train, "adversarial_negative": neg_train}
gen = mmap_batch_generator(
    files,
    n_per_class={k: 32 for k in files},
    data_transform_funcs={k: f for k in files},
    label_transform_funcs={
        "positive": lambda x: [1 for i in x],
        "negative": lambda x: [0 for i in x],
        "adversarial_negative": lambda x: [0 for i in x],
    },
)

# inspect first batch
xb, yb = gen.__next__()
print(f"batch: x={xb.shape} y sum={yb.sum()} of {len(yb)} (pos={int(yb.sum())})")

model = Model(n_classes=1, input_shape=(27, 96), model_type="dnn", layer_dim=128,
              seconds_per_example=1280*27/16000)
opt = torch.optim.Adam(model.model.parameters(), lr=LR)
lossf = torch.nn.functional.binary_cross_entropy

val_pos = torch.from_numpy(pos_test[:8].astype(np.float32))
val_neg = torch.from_numpy(neg_test[:8].astype(np.float32))


def stats(tag, step):
    with torch.no_grad():
        pp = model.model(val_pos).numpy()
        nn_ = model.model(val_neg).numpy()
        h = None
        x = torch.from_numpy(pos_test[0:1].astype(np.float32))
        h = model.model.flatten(x)
        h = model.model.relu1(model.model.layernorm1(model.model.layer1(h)))
        h = model.model.blocks[0](h)
    print(f"{tag:6} step={step:5d} loss_last={last_loss:8.4f} | "
          f"pos pred mean={pp.mean():.4f} neg pred mean={nn_.mean():.4f} | "
          f"lastbias={model.model.last_layer.bias.item():+.4f} | "
          f"relu1 sum={h.sum().item():7.3f} max={h.max().item():6.3f} nonzero={(h>0).sum().item()}/128")


last_loss = float("nan")
print(f"\n{'':6} step=    0 (init)")
stats("init", 0)

it = iter(gen)
for step in range(N_STEPS):
    xb, yb = next(it)
    x = torch.from_numpy(xb).to(torch.float32)
    y = torch.from_numpy(yb).to(torch.long)
    yf = y[..., None].to(torch.float32)
    opt.zero_grad()
    pred = model.model(x)
    loss = lossf(pred, yf)
    last_loss = loss.item()
    loss.backward()
    opt.step()
    if step % 100 == 0 or step == N_STEPS - 1:
        stats(f"loss={loss.item():.3f}"[:6], step)
