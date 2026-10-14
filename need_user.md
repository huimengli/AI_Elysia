# Need User（需用户确认的问题）

<!-- 已归档于 ai_buckup/need_user.md_2026-10-13-21-12-19.md（Q2/Q3 历史条目 + Q4 llama 重启请求，全部 status: done） -->

## Q5 2026-10-13-22-30 GitHub 仓库私有化 / 描述改"自用"（status: wait）

**问题**: 用户要求把 `github.com/huimengli/JarvisAi` 改为私有仓库，若不可行则把仓库描述改为"自用"。AGENTS.md 禁止 Agent 执行 `git push` 或任何远程写入（含 GitHub API/网页操作），此操作只能由用户在 GitHub 端手动完成。

**给用户的步骤**:
1. 打开 https://github.com/huimengli/JarvisAi → 右上角 **Settings**。
2. 左侧 **General**：
   - "Change repository visibility" → **Make private**（需要账号有私有仓库权限；免费版账号有数量限制，超限则只能改描述）。
   - "Description" 输入 `自用`。
3. 保存（Save）。
4. 注意：本 Agent 从未执行过 push，本地提交不会自动同步到 GitHub；若仓库此前是公开空仓库/已有公开内容，改私有后历史内容仍保留在仓库中。

**A**: （待用户回复）
