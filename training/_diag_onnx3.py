# Diagnostic: rebuild the torch Net from the ONNX initializers (same weights)
# and compare torch vs ORT outputs on identical feature inputs.
import os
import sys

import numpy as np
import onnx
import torch
from onnxruntime import InferenceSession


class FCNBlock(torch.nn.Module):
    def __init__(self, d):
        super().__init__()
        self.fcn_layer = torch.nn.Linear(d, d)
        self.relu = torch.nn.ReLU()
        self.layer_norm = torch.nn.LayerNorm(d)

    def forward(self, x):
        return self.relu(self.layer_norm(self.fcn_layer(x)))


class Net(torch.nn.Module):
    def __init__(self, T, D, L=128):
        super().__init__()
        self.flatten = torch.nn.Flatten()
        self.layer1 = torch.nn.Linear(T * D, L)
        self.relu1 = torch.nn.ReLU()
        self.layernorm1 = torch.nn.LayerNorm(L)
        self.blocks = torch.nn.ModuleList([FCNBlock(L) for _ in range(1)])
        self.last_layer = torch.nn.Linear(L, 1)
        self.last_act = torch.nn.Sigmoid()

    def forward(self, x):
        x = self.relu1(self.layernorm1(self.layer1(self.flatten(x))))
        for b in self.blocks:
            x = b(x)
        return self.last_act(self.last_layer(x))


model_path = sys.argv[1] if len(sys.argv) > 1 else r"openWakeWord\output\aili_xiya_v0.1\aili_xiya_v0.1.onnx"
feat_dir = os.path.join(os.path.dirname(model_path))
pos_npy = os.path.join(feat_dir, "positive_features_test.npy")
neg_npy = os.path.join(feat_dir, "negative_features_test.npy")

# 1) pull weights out of ONNX
m = onnx.load(model_path)
inits = {i.name: onnx.numpy_helper.to_array(i) for i in m.graph.initializer}
print("initializers:", {k: v.shape for k, v in inits.items()})

net = Net(27, 96)
state = {
    "layer1.weight": torch.from_numpy(inits["layer1.weight"]),
    "layer1.bias": torch.from_numpy(inits["layer1.bias"]),
    "layernorm1.weight": torch.from_numpy(inits["layernorm1.weight"]),
    "layernorm1.bias": torch.from_numpy(inits["layernorm1.bias"]),
    "blocks.0.fcn_layer.weight": torch.from_numpy(inits["blocks.0.fcn_layer.weight"]),
    "blocks.0.fcn_layer.bias": torch.from_numpy(inits["blocks.0.fcn_layer.bias"]),
    "blocks.0.layer_norm.weight": torch.from_numpy(inits["blocks.0.layer_norm.weight"]),
    "blocks.0.layer_norm.bias": torch.from_numpy(inits["blocks.0.layer_norm.bias"]),
    "last_layer.weight": torch.from_numpy(inits["last_layer.weight"]),
    "last_layer.bias": torch.from_numpy(inits["last_layer.bias"]),
}
net.load_state_dict(state)
net.eval()

# 2) load features
pos = np.load(pos_npy)   # (400, 27, 96)
neg = np.load(neg_npy)
print("pos shape", pos.shape, "neg shape", neg.shape)

sess = InferenceSession(model_path, providers=["CPUExecutionProvider"])

samples = [
    ("zeros", np.zeros((1, 27, 96), dtype=np.float32)),
    ("random", np.random.RandomState(0).randn(1, 27, 96).astype(np.float32)),
    ("pos[0]", pos[0:1].astype(np.float32)),
    ("neg[0]", neg[0:1].astype(np.float32)),
    ("neg[3]", neg[3:4].astype(np.float32)),
]

print(f"\n{'sample':<8} | {'torch out':>10} | {'ORT out':>10} | torch logit | ORT logit")
for name, x in samples:
    with torch.no_grad():
        t_out = net(torch.from_numpy(x)).numpy()[0, 0]
    o_out = sess.run(["sigmoid"], {"x": x})[0][0, 0]

    def logit(p):
        p = min(max(p, 1e-9), 1 - 1e-9)
        return float(np.log(p / (1 - p)))

    print(f"{name:<8} | {t_out:10.6f} | {o_out:10.6f} | {logit(t_out):+11.4f} | {logit(o_out):+11.4f}")

# 3) intermediate relu_1 comparison via ORT
print("\n=== ORT intermediates (relu_1) ===")
for name, x in samples[:4]:
    r1 = sess.run(["relu_1"], {"x": x})[0][0]
    print(f"{name:<8} relu_1: mean={r1.mean():.6f} std={r1.std():.6f} max={r1.max():.6f} nonzero={(r1>0).sum()}/128")

# 4) torch intermediate
print("\n=== torch intermediates (relu_1) ===")
with torch.no_grad():
    for name, x in samples[:4]:
        h = net.flatten(torch.from_numpy(x))
        h = net.relu1(net.layernorm1(net.layer1(h)))
        h = net.blocks[0](h)  # full block incl. relu -> this is relu_1
        r1 = h.numpy()[0]
        print(f"{name:<8} relu_1: mean={r1.mean():.6f} std={r1.std():.6f} max={r1.max():.6f} nonzero={(r1>0).sum()}/128")
