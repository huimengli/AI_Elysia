import importlib.util

spec = importlib.util.spec_from_file_location("t2cn", "_t2_train_cn.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

out = m.cn_generate_adversarial_texts("爱莉希雅", 30, include_partial_phrase=1.0, include_input_words=0.2)
print("N =", len(out))
for s in out[:30]:
    print(s)
assert "爱莉希雅" not in out
print("CN_ADV_OK")
