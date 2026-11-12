# Diagnostic: dump full ONNX graph structure + all initializer stats.
# Usage: python _diag_onnx2.py [model.onnx]
import sys
import numpy as np
import onnx

path = sys.argv[1] if len(sys.argv) > 1 else r"openWakeWord\output\aili_xiya_v0.1\aili_xiya_v0.1.onnx"
m = onnx.load(path)
print(f"ir_version={m.ir_version} opset={[ (o.domain, o.version) for o in m.opset_import ]}")
g = m.graph

print("\n=== GRAPH INPUTS ===")
for i in g.input:
    print(" ", i.name, [d.dim_value or d.dim_param for d in i.type.tensor_type.shape.dim])
print("=== GRAPH OUTPUTS ===")
for o in g.output:
    print(" ", o.name, [d.dim_value or d.dim_param for d in o.type.tensor_type.shape.dim])

print("\n=== NODES (topological order) ===")
for idx, n in enumerate(g.node):
    attrs = {}
    for a in n.attribute:
        if a.type == onnx.AttributeProto.INT:
            attrs[a.name] = a.i
        elif a.type == onnx.AttributeProto.FLOAT:
            attrs[a.name] = a.f
        elif a.type == onnx.AttributeProto.INTS:
            attrs[a.name] = list(a.ints)
        else:
            attrs[a.name] = str(a)
    print(f"[{idx}] {n.op_type} in={list(n.input)} out={list(n.output)} attr={attrs}")

print("\n=== INITIALIZERS ===")
for init in g.initializer:
    arr = onnx.numpy_helper.to_array(init)
    print(f"  {init.name}: shape={arr.shape} dtype={arr.dtype} "
          f"min={arr.min():.6f} max={arr.max():.6f} mean={arr.mean():.6f} std={arr.std():.6f} L2={np.sqrt((arr**2).sum()):.6f}")

# constants (Constant nodes) are not initializers; list them too
print("\n=== CONSTANT NODE VALUES ===")
for idx, n in enumerate(g.node):
    if n.op_type == "Constant":
        for a in n.attribute:
            if a.name == "value":
                arr = onnx.numpy_helper.to_array(a.t)
                print(f"  node[{idx}] const: shape={arr.shape} dtype={arr.dtype} "
                      f"min={arr.min():.6f} max={arr.max():.6f} mean={arr.mean():.6f}")
