# 第 1 轮：`/favicon.ico` 返回 200 且字节一致（2026-11-13 00:00）

- 时间：2026-11-12 23:59-00:00
- 场景：`.tmp/gen_favicon.py` 用主题色（粉 `#F8A9C4` + 丁香 `#C9B7E0` + 金 `#F2C9A8` + 玫瑰 `#7E3F66`）画 64×64 圆盘 + 四角星，存成 16/32/48/64 四档 ICO（788 字节）到 `jarvis/static/favicon.ico`；`jarvis/web.py` 新增 `@app.get("/favicon.ico")` 用 `FileResponse`（缺文件时返回 204，不抛 500）；`jarvis/static/index.html` 加 `<link rel="icon" href="/favicon.ico" type="image/x-icon">`；重启 `:7860`
- 期望：`curl.exe --ssl-no-revoke` 取 `/favicon.ico` = **200**、字节数与磁盘文件一致
- 实际：`code=200 bytes=788`；磁盘 788 字节；`Get-FileHash` 下载件与磁盘件 **一致 True**
- 结果：**通过**（404 根因消除）
- 备注：零截图；ICO 是二进制小文件（788 B），随代码一起 commit，不含敏感信息。
