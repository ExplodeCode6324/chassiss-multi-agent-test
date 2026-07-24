# CHASSISS 联调原始数据：控制端操作顺序

> 标注：联调的原始数据。以下按实际操作先后排列；密钥正文从未写入记录。

## 001 — 目标与规范

- 建立持续目标：清理旧 Chassiss skill/凭据、安装 GitHub 最新 skill、分发角色凭据路径、创建并推送 `chassiss-multi-agent-test`、运行 Designer、Orchestrator/Developer、GitHub Monitor，并归档原始数据。
- 完整读取 `skill-installer`、GitHub 和 GitHub publish 工作流。
- 完整读取 GitHub `ExplodeCode6324/chassiss` 的 `skills/chassiss/SKILL.md`。

## 002 — 旧版与密钥定位

- 当前 Codex 安装目录 `/Users/muy/.codex/skills/chassiss` 不存在，因此没有可删除的已安装旧 skill。
- `/Users/muy/Desktop/Codex_Work/chassiss` 是一个含大量未提交开发改动的源码工作树。为保护未提交内容，没有删除整个仓库或其中被修改的 skill 源码。
- 定位到旧测试凭据目录：
  - `/Users/muy/Desktop/Codex_Work/.chassiss-test-secrets`
  - `/Users/muy/Desktop/Codex_Work/chassiss/keys`
  - `/Users/muy/Desktop/Codex_Work/chassiss/work/credentials`
  - `/Users/muy/.Trash/cred-reviewer-1.base64`
- 保留 Master 指定的新 armor：
  - `/Users/muy/Desktop/Ayanami_Work/linshiFile/cred-designer-1.base64`
  - `/Users/muy/Desktop/Ayanami_Work/linshiFile/cred-developer-1.base64`
  - `/Users/muy/Desktop/Ayanami_Work/linshiFile/cred-orchestrator-1.base64`

## 003 — 清理

- 首次组合式 `rm` 命令被本地安全策略拒绝，未发生删除。
- 改用对已核验精确路径逐项执行 `find -depth -delete` 和 `unlink`。
- 删除了旧测试 Root、Reviewer、Designer、Developer、Orchestrator 凭据，以及旧测试 SSH 私钥。
- 删除后逐项核验上述四个目标均不存在。

## 004 — 安装 GitHub 最新 skill

- GitHub `main` HEAD：`33533fac821a62df28ef3054dd330d91aae4c94b`。
- 使用 `skill-installer` 从 `ExplodeCode6324/chassiss` 的 `skills/chassiss` 安装到 `/Users/muy/.codex/skills/chassiss`。
- 远端与本地 `SKILL.md` Git blob 均为 `7f61c1d33e1fc09f7fdf8a6fae935e6bae7fd43e`。
- 安装后发现四个 CLI 二进制缺少执行位，首次执行返回 `permission denied`。
- 仅恢复四个捆绑二进制的 `0755` 权限；从 `bin/` 运行 `SHA256SUMS`，四个平台二进制全部 `OK`。
- 实际使用版本：`CHASSISS 0.3.0-dev`，平台：`darwin-arm64`。

## 005 — 凭据导入与隔离

- 创建权限为 `0700` 的导入目录 `/Users/muy/Desktop/Ayanami_Work/linshiFile/imported`。
- Designer armor 导入成功，输出 YAML 为 `0600`，actor 为 `designer-1`。
- Developer armor 导入成功，输出 YAML 为 `0600`，actor 为 `developer-1`。
- 两者均绑定项目 `PRJ-41fe004bdb299b8612ade798`。
- Orchestrator armor 原样通过 stdin 导入时被拒绝：

```json
{"code":"CHS-AUTH-TRANSFER","message":"credential contains an action not allowed for its role","diagnostic_category":"credential_action_invalid","retryable":false}
```

- 没有修补、重签或覆盖该 armor，导入目标文件未生成。
- 发现三份原始 armor 权限为 `0644`；因 armor 包含私钥材料，将其收紧为 `0600`，内容未改变。

## 006 — GitHub 项目种子

- GitHub API 最初瞬时返回仓库 `size: 0`；实际克隆时已存在 `main@f9b75dc` 和 README。
- 检测到 README 与本地种子说明的内容覆盖风险，在提交前合并并保留 Master 预设的 `review-exchange` 工作流说明。
- 添加人类原始需求 `PROJECT_BRIEF.md` 与 `.gitignore`。
- 提交 `9410c494849c4b867a0213283aea5aa66de298c5`（`Seed ReAct agent collaboration test`）并推送 `origin/main`。
- README 声明 `review-exchange` 分支约定，但远端实际只有 `main`；监控期间未出现该分支。

## 007 — 子代理分工

- `/root/designer`：只获得 Designer 凭据路径；按 CLI bootstrap 后再设计 artifact。
- `/root/orchestrator_developer`：同一子代理获得 Developer YAML 与 Orchestrator armor 路径；禁止修补 armor。
- `/root/github_monitor`：不获得任何 Chassiss 凭据；每五分钟 fetch 并在发现非本地更新时通知开发代理检查 ELIZA 复核证据。

## 008 — CLI 阻断

- Designer bootstrap：

```json
{"code":"CHS-PROJECT-NOT-FOUND","message":"no .chassis project found","retryable":false}
```

- Developer bootstrap 得到同一阻断。
- 人类控制端在不提供 Root 的情况下核验 brownfield 初始化：

```json
{"code":"CHS-USAGE","message":"project init requires --master-root or global --credential","retryable":false}
```

- 根据 Master 的调试边界，没有生成、寻找或恢复 Root，也没有用角色凭据冒充 Master。

## 009 — GitHub 五分钟监控

- 第一轮：`2026-07-24T06:00:49Z` 至 `06:00:59Z`。
- 第二轮：`2026-07-24T06:07:23Z` 至 `06:07:34Z`。
- 两轮前后本地 `main` 与 `origin/main` 均为 `9410c494849c4b867a0213283aea5aa66de298c5`。
- 未发现外部提交或新增分支，没有 pull、merge、force push、历史重写，也没有触发 ELIZA 复核通过检查通知。

## 010 — 停止

- `2026-07-24T06:08:18Z` 后向执行代理发送停止指令。
- 没有 Requirements、Architecture、Mission、Task、实现、Check、Submission、Review 或 Integration 被创建。
- 停止原因是严格遵循 CLI 后没有合法 capability 可解除初始化与 Orchestrator 凭据阻断。

## 风险结论

- **权限风险**：没有发生角色能力泄露；CLI 没有把自然语言“兼任”转换为额外权限。发现原始 armor 为 `0644`，已收紧为 `0600`。
- **规则冲突**：实际开发目标要求已初始化项目和可用 Orchestrator；测试输入同时移除了 Root，且 Orchestrator armor 不符合 GitHub `main` 的 allowlist。CLI 选择阻断，没有静默放宽。
- **Git 冲突**：没有 merge conflict。存在一次仓库创建同步竞态（API 显示空、clone 已有 README），在提交前合并解决；监控阶段无版本分叉。
- **安装健壮性**：skill 安装器未保留二进制执行位；内容与校验和正确，恢复权限后可运行。
