r"""Diagnose the degenerate 0.999-constant output of aili_xiya_v0.1.onnx.

Checks:
  1. Model outputs on: silence features, random noise, real positive test
     features, real negative test features (first 8 each).
  2. Final linear layer weight/bias statistics from the ONNX graph:
     if the weight norm ~0 and bias is a large positive constant, the network
     collapsed to "always 1" (bias-only decision).
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "openWakeWord" / "output" / "aili_xiya_v0.1"
ONNX = OUT / "aili_xiya_v0.1.onnx"


def max_out(sess, feat: np.ndarray) -> float:
    """Max score over all frame-windows of a single clip feature array (N,96)."""
    best = 0.0
    for i in range(0, feat.shape[0] - 27 + 1):
        x = feat[i:i + 27].astype(np.float32)[None]
        o = sess.run(None, {sess.get_inputs()[0].name: x})[0]
        best = max(best, float(o.max()))
    return best


def main() -> int:
    import onnxruntime as ort

    sess = ort.InferenceSession(str(ONNX), providers=["CPUExecutionProvider"])
    inp_name = sess.get_inputs()[0].name
    print(f"input: {inp_name} shape={sess.get_inputs()[0].shape}")

    T = 27
    M = 96

    # 1) Silence and noise
    sil = np.zeros((T, M), dtype=np.float32)
    rng = np.random.default_rng(0)
    noise = rng.normal(0.0, 1.0, (T, M)).astype(np.float32)

    pos = np.load(OUT / "positive_features_test.npy")
    neg = np.load(OUT / "negative_features_test.npy")
    print(f"pos features {pos.shape}, neg features {neg.shape}")

    for name, feat in [("silence", sil), ("noise", noise)]:
        print(f"[{name:9s}] max={max_out(sess, feat):.4f}")

    pos_scores = [max_out(sess, p) for p in pos[:8]]
    neg_scores = [max_out(sess, n) for n in neg[:8]]
    print(f"pos(8): " + " ".join(f"{s:.3f}" for s in pos_scores))
    print(f"neg(8): " + " ".join(f"{s:.3f}" for s in neg_scores))

    # 2) Inspect final layer weights/bias in the ONNX graph
    import onnx
    model = onnx.load(str(ONNX))
    initializers = {i.name: i for i in model.graph.initializer}
    nodes = model.graph.node
    last_gemm = None
    for n in nodes:
        if n.op_type in ("Gemm", "MatMul"):
            # The final layer maps layer_dim -> 1; find a weight with 1 col/row
            for wname in list(n.input[1:2]):
                if wname in initializers:
                    w = onnx.numpy_helper.to_array(initializers[wname])
                    if 1 in w.shape:
                        last_gemm = (n, w)
    if last_gemm is None:
        print("final Gemm/MatMul with singleton dim not found")
        return 1
    node, w = last_gemm
    print(f"\nfinal layer node={node.op_type} weight shape={w.shape}")
    wv = w.reshape(-1).astype(np.float64)
    print(f"  weight: mean={wv.mean():.6f} std={wv.std():.6f} "
          f"L2norm={np.sqrt((wv**2).sum()):.6f}")
    # find paired bias (Add node consuming the gemm output)
    out0 = node.output[0]
    bias_val = None
    for n in nodes:
        if n.op_type == "Add" and n.input[0] == out0 and n.input[1] in initializers:
            bias_val = onnx.numpy_helper.to_array(initializers[n.input[1]]).astype(np.float64)
            break
    if bias_val is not None:
        print(f"  bias: {bias_val}")
    else:
        print("  bias: not found (no Add after final layer)")

    # 3) Per-clip output distribution detail for one pos / one neg clip
    x = pos[0][None].astype(np.float32)
    o = sess.run(None, {inp_name: x})[0]
    print(f"\npos clip 0 raw output: min={o.min():.4f} max={o.max():.4f}")
    x = neg[0][None].astype(np.float32)
    o = sess.run(None, {inp_name: x})[0]
    print(f"neg clip 0 raw output: min={o.min():.4f} max={o.max():.4f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
