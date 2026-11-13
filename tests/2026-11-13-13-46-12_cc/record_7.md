# 轮 7（附加）— 拼音索引的英文缺口（HB-041，修后 PASS）
- **时间**：2026-11-13 14:30 发现 / 14:28 修后复测
- **场景**：查 `apps` 表 `py` 列填充状态，再直调 `open_app('chrome')`（零截图）
- **期望**：拼音索引对**全部 227 条**有效，不只中文名
- **实际**：
  ```
  修前：py 为空 158 条（Google Chrome / OneDrive / aida64 / launcher …）
        `dnSpy.exe - 快捷方式` 被索引成 kuaijiefangshi，与 HaoZip - 快捷方式 撞车
  修后：py 为空 0 条；Google Chrome -> googlechrome，OneDrive -> onedrive，aida64 -> aida
        dnSpy -> dnspyexe，HaoZip -> haozip（先剥「- 快捷方式」尾巴）
  复测：已打开：Google Chrome（从应用列表匹配，复读确认进程 chrome）
  ```
- **结果**：**修后 PASS**
- **备注**：根因是 `pypinyin` 的 `errors="ignore"` **丢掉非中文字符**。**副作用披露**：这轮真打开了 Chrome（我没有关掉它，`next`/Chrome 窗口留在你屏幕上）。`aida64 -> aida` 是字母截断（数字被丢），子串层仍可命中，如实记录这个精度损失。
