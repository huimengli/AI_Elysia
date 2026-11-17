

## 批次结论 · HB-040 `_coerce` 架空中文默认值（3 轮，2026-11-17 13:25）

**3/3 PASS。**

- **根因（代码级）**：`router.py::_coerce` 对**每一个 schema 参数**都写值 → 模型**省略**的键被写成 `""`/`0`/`False`
  并**存在于 dict**，函数自己的默认值因此被架空。实测受害者 `set_timer(seconds, message="定时到了！")`
  （`system.py` L248）在模型省略 `message` 时播报**空串**
- **修法**：`if key not in out: continue` —— 模型没传的键**保持缺席**（函数默认值生效）；显式 `null` **仍 coerce 成空串**，
  因为把 `None` 喂进字符串工具就是当年开幻觉通道的那次崩溃（`events.db` 242/245）
- **轮 1** `{'seconds':3600}` → `_coerce` `{'seconds':3600}`（`message` 缺席）→ 「已设置 1小时 0分 后的提醒：**定时到了！**」PASS
- **轮 2** `{'seconds':3600,'message':'该喝水了'}` → 中文值原样保住 PASS
- **轮 3** `{'seconds':3600,'message':None}` → `message=''`，播报空串但**不崩**，PASS（这是模型明说的 null，不是被架空）
- **附加**：`click_at({'x':1,'y':2})` → `_coerce` `{'x':1,'y':2}`，`button` 键缺席 → 函数默认 `left` 生效
- **边界**：不改 schema 文案、不增删工具（工具面 10,633 字符 / 36 工具，token 面 2,806 不变）

