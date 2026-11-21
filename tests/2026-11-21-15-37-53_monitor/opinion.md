# 批次结论 — Monitor 验证 3 轮（2026-11-21-15-37-53）

轮 1（路由与关闭授权）：**PASS 5/5**。快照键齐、四灯 4 键、外部 pid 关闭被拒、/monitor 页 200。
轮 2（WS 协议与节拍）：**部分 PASS**。协议面全对（connected、monitor、100→30 / 0→1 夹取、无客户端 sleep）；**1 s 节拍未达**：实测 4.26-4.66 s/拍、首拍 14.87 s，根因是单拍采样耗时（探针超时 + app 索引首建 + netstat 0.2-0.4 s）。
轮 3（子进程起 / 日志接管 / 关闭授权）：**PASS 4/4** + 追加段（外部起接入识别 + 拒绝杀外部 pid + 端口未被杀）PASS。taskkill 真实输出照抄进日志。
批次自曝 12 处（累计第 100-111）：四灯没进 /api/monitor（100）、`ws.onclose = ws.onclose` 自赋值（98）、驱动没设超时 16 分钟不出结果（102）、`fs.existsSync`（103）、`windll.psapi` 查不到 K32（104）、`_mon_interval` 少 `global`（105）、stub 不 bind 端口导致外部起没触发（106）、TCP 表结构字段顺序（107）、bOwner 与返回码 122（108）、行距 24 与 IPv4 表不含通配/IPv6 行（109）、JS `\x00` 写出 null 字节（110）、最后改用 `netstat -ano`（111）。
未测照实：真机 1 s 节拍；隐藏页降 30 的实际省电；前端页面渲染（间隔下拉、日志折叠、confirm）；关窗全关（CTRL_CLOSE_EVENT 5 s 时限）；jarvis 起 /monitor 窗口不最大化与窗口数 ≤3 口径一致 —— 这 5 项都要你在真会话里看。
