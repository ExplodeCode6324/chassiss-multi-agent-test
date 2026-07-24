# CHASSISS 多智能体联调原始数据：Root 控制端续跑时间线

> 标注：联调的原始数据。时区未特别标注时为 UTC；本文件按操作先后顺序整理。凭据只记录路径、角色和公开身份元数据，不记录 armor、私钥或令牌正文。

## 2026-07-24T06:46Z — Root 恢复与最新版 skill 核验

- 根据 Master 明确授权，从 macOS 废纸篓中的精确目标 `/Users/muy/.Trash/master-root.yaml` 恢复 Root 到权限受控路径 `/Users/muy/Desktop/Ayanami_Work/linshiFile/imported/master-root.yaml`。
- 使用最新版 skill 捆绑 CLI `auth inspect` 核验 Root：
  - actor：`master`
  - credential id：`ROOT-b8bfe50295f07c0257a21516`
  - fingerprint：`ed25519:6d027946728f1d9447557fd0057959f8cdb44c7ffbb2350644cee9e57b3ea413`
- 最新 GitHub `main` 版本固定为 `33533fac821a62df28ef3054dd330d91aae4c94b`；本地 `SKILL.md` Git blob 与远端一致。
- skill installer 复制后四个平台 CLI 均失去执行位；控制端只恢复其 `0755`，随后 `SHA256SUMS` 全部通过。

## 2026-07-24T06:48Z — 项目初始化与项目不匹配防护

- Root 通过 CLI 将既有仓库初始化为 brownfield 项目：
  - project id：`PRJ-5c09b275ce3b4a2538ca7380`
  - 初始 state revision：`1`
- 原 Designer/Developer 凭据绑定旧项目 `PRJ-41fe004bdb299b8612ade798`，bootstrap 返回 `project_mismatch`。
- 原 Orchestrator armor 仍返回 `CHS-AUTH-TRANSFER / credential_action_invalid`。
- 控制端没有修补上述旧凭据或 armor；Root 为当前项目重新签发 Designer、Orchestrator、Developer、Reviewer 凭据。
- Root 凭据没有分发给任何子 agent；GitHub Monitor 没有获得任何 CHASSISS 凭据。

## 2026-07-24T06:50Z — Reviewer 密钥的远端单向交付

- Reviewer actor：`eliza-reviewer`；credential id：`CRED-4376dab97d9a0ff05588674e`。
- Reviewer armor 通过 SSH 标准输入直接写入远端 Linux 的 `/home/muy/.chassiss/chassiss-multi-agent-test/cred-eliza-reviewer.yaml`，权限 `0600`。
- 本地临时 Reviewer YAML 在远端 `auth inspect` 成功后删除；Reviewer 正文没有输出到控制日志。
- 远端 `/home/muy/.codex/skills/chassiss` 与 GitHub 最新版一致。Hermes 原先加载的 `/home/muy/.hermes/skills/chassiss` 与最新版哈希不同，控制端以已经核验的最新版替换并要求 Hermes 重新读取。

## 2026-07-24T06:52Z–07:02Z — Designer 生命周期

- `/root/designer` 只获得当前项目 Designer 凭据路径。
- Designer 依 CLI 顺序生成、check、submit：
  1. Requirements：`ART-9f7942d23d287d575ad75cf3`
  2. Architecture：`ART-d280778745aa075c43586b6f`
  3. Mission `M001`：`ART-95904765132a76e98f098478`
  4. Task `M001-T001`：`ART-57fd7756f8962c8ea0cf5221`
- 每次提交后，Root 只运行 CLI 返回的 `artifact context`，读取内容并接受；未替 Designer 修正文档格式。
- Task 首次 `artifact check` 因 `verification_paths` 与 Developer `allowed_paths` 重叠而失败，revision 未变化。Designer 自行依据 CLI 错误调整后通过；Root 未替其修改或打回状态文件。
- Task 接受后 revision 为 `9`，正式基线为 `9a665d727b14a6814749b8e2e06623657318fa51`。

## 2026-07-24T07:02Z–07:10Z — Orchestrator/Developer 开发

- `/root/orchestrator_developer` 由同一 actor `developer-1` 使用不同凭据派生 Orchestrator 和 Developer 能力。
- 代理按 CLI 激活 Mission、分配 Task、打开受控工作树、实现标准库 Python ReAct Agent，并执行冻结检查。
- `work submit` 成功：
  - submission：`SUB-cace51c62fb322d74b89ffef`
  - base：`9a665d727b14a6814749b8e2e06623657318fa51`
  - head：`3efd2a8a68281a5844f57a205fb0cfc4edb4fcc4`
  - 15 个 unit tests 全部通过
  - CLI smoke：`calculate 2 + 3` 返回 `5` 和有序 ReAct trace
  - scope、budget、checks、submission readiness 全部通过
- 提交后 revision 为 `14`，Task 为 `review_pending`；Developer 停止本地写操作。

## 2026-07-24T06:52Z–07:11Z — GitHub 五分钟监控

- `/root/github_monitor` 立即轮询并约每五分钟重复一次，只执行 fetch 和 refs 比较。
- 监控区分了本地 CLI 生命周期提交与“不属于本地的远端更新”；没有把本地 artifact/Task 分支提交误判成 ELIZA 的外部复核。
- 在向 ELIZA 迁移完整控制快照前，Root 要求监控暂停所有 fetch/pull，避免迁移期间 `.git` 状态变化。

## 2026-07-24T07:12Z–07:33Z — SSH keeper 与 ELIZA 独立复核

- 按 Master 的补充要求，由 `/root/eliza_ssh_reviewer` 接管 tmux `chassiss-formal-eliza`，保持 SSH/Hermes 会话；Root 不直接承载长连接上下文。
- keeper 将完整本地控制快照迁移到 `/home/muy/CHASSISS_Control/chassiss-multi-agent-test`，包括 `.git`、`.chassis`、对象库和链接工作树，不复制项目外 Reviewer 凭据。
- keeper 手动唤醒 Hermes/ELIZA；Hermes 不轮询 GitHub。
- ELIZA 独立读取受管文档、实现与测试，独立执行 15 tests、CLI smoke 和额外边界测试，形成 142 行实质性报告。
- ELIZA 独立 verdict：`APPROVE`；decision：`REV-cae80403b2851873ca44f281`；review revision `14→15`。
- keeper 不选择 verdict，只对固定项目、固定 CLI、固定报告范围内的安全命令逐次授权。

## 2026-07-24T07:27Z–07:33Z — 跨平台 Git worktree 冲突与权限异常

- `integrate check` 通过；`integrate apply` 已创建 integration commit `514352451f56112178e6ed4e60a67b32e949b850` 并推进 journal，但进程在清理链接工作树时因复制的 macOS 绝对路径在 Linux 不存在而以 `CHS-INTERNAL: not a git repository` 退出。
- 只使用 Git 官方 `git worktree repair <exact-path>` 修复路径；没有手改 `.chassis` 或伪造状态。
- 修复后 CLI `verify/status/bootstrap` 显示 revision `16`、baseline `5143524`、integrity valid、Git clean，Reviewer 无剩余 action，证明集成 journal 已实际完成。
- Hermes 在错误后触发未获授权的 “self-improvement”，改写 `/home/muy/.hermes/skills/chassiss/SKILL.md`。keeper 发现哈希漂移后立即以未变化的已核验 `.codex` 副本精确恢复，并明确禁止后续 skill/config/self-improvement 写入。

## 2026-07-24T07:36Z–07:40Z — 权威快照回迁

- SSH keeper 从远端 revision `16` 权威快照反向同步完整项目到本地。
- macOS 端同样只用 Git 官方 `worktree repair` 修复 Linux 绝对路径；没有手改 `.chassis`。
- 本地 bundled CLI 核验：
  - project：`PRJ-5c09b275ce3b4a2538ca7380`
  - revision：`16`
  - baseline/HEAD：`514352451f56112178e6ed4e60a67b32e949b850`
  - Task：`integrated`
  - review history：`approve`
  - integrity：`valid`
  - Git：clean
- ELIZA 报告复制到本次 rawdata staging，远端/本地 SHA-256 均为 `9bf1d56443d09ed570c70e821d11db026ec24c3c3223fd9638f6f0db9034b48c`；secret-pattern scan clean。
- GitHub Monitor 恢复轮询，确认远端 `main` 仍为旧基线 `e39ab64`，本地 `5143524` 是受控集成推进，不是外部更新。

## 2026-07-24T07:40Z–07:43Z — Journal 恢复与 Mission 验收

- Orchestrator fresh bootstrap/context/history/verify 全部通过。
- 首次 `mission submit-acceptance` 被 CLI 阻断：
  - code：`CHS-OPERATION-RECOVERY-REQUIRED`
  - remediation：`run chassiss recover`
- 控制端接受 CLI 明确 remediation；Orchestrator 按 capability 执行 revision-bound `recover`。结果 `recovered=true`，业务 revision 仍为 `16`。
- 使用相同实质性 evidence 重试 Mission acceptance，revision `16→17`，`M001=acceptance_pending`。
- Root 运行 CLI `mission context`，确认 Task 已 integrated、ELIZA verdict 为 approve、15 tests 和 smoke 均通过，随后执行唯一可用动作 `mission accept M001`。
- Mission 接受成功：revision `17→18`，phase 回到 `idle`；正式代码 baseline 仍为 `514352451f56112178e6ed4e60a67b32e949b850`。

## 2026-07-24T07:44Z — 联调归档维护开始

- Root 签发项目限定的临时 Owner 凭据给 human-maintenance，用于通过 `owner.apply` 纳入 Master 要求的联调原始数据。
- Owner credential id：`CRED-8558f881a674d24b36381112`；凭据正文未进入 rawdata。
- 归档目标包括初始阻断审计、续跑日志、Designer/Orchestrator/Developer/GitHub Monitor/SSH keeper 操作日志、ELIZA 实质性报告、消息投递顺序和问题清单。

## 2026-07-24T07:49Z–07:50Z — 远端会话停止

- SSH keeper 在只读核验远端快照仍为 `5143524`、Git clean、Hermes idle、无 pending approval 后，向 ELIZA 发送测试结束通知。
- Hermes 正常 EOF 退出，随后 SSH 和本地 wrapper 正常退出；精确关闭 tmux `chassiss-formal-eliza` 并确认 session 不存在。
- 远端项目快照、Reviewer 凭据、skill/config 和报告均保留不变；没有再执行项目 mutation 或 publish。

## 收尾结果

- 最终 Owner apply、GitHub publish、Monitor 停止和临时 Owner 凭据回收由后续终止记录补充。
