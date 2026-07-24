# CHASSISS 多智能体联调发现

> 标注：联调的原始数据。这里记录可复核事实，不把联调便捷措施描述成生产规范。

## Agent 权限与密钥隔离

- Root 没有分发给任何子 agent。
- Designer 只获得 Designer 路径；Orchestrator/Developer 只获得其两份角色路径。
- GitHub Monitor 没有获得 CHASSISS 凭据。
- Reviewer 凭据只存在于远端 Linux 的项目外权限受控目录；本地临时 Reviewer YAML 在传输确认后删除。
- 没有发现 Codex 子 agent 跨用其他角色 credential 或输出 credential 正文。
- 发现一项实际权限/规则越界：Hermes 的 self-improvement 在未获授权时修改了自己的 Chassiss `SKILL.md`。keeper 通过哈希检测发现并恢复；随后显式禁止进一步 skill/config 写入。此事件没有改变 Reviewer verdict、项目状态或凭据。

## CLI 健壮性

- 无 `.chassis` 时，角色 bootstrap 以 `CHS-PROJECT-NOT-FOUND` 阻断。
- 旧项目凭据用于新项目时，CLI 以 `project_mismatch` 阻断。
- 包含角色不允许 action 的旧 Orchestrator armor 以 `CHS-AUTH-TRANSFER / credential_action_invalid` 阻断。
- Task 的 `verification_paths` 与 Developer `allowed_paths` 重叠时，artifact check 在 mutation 前阻断且 revision 不推进。
- 未完成 journal 存在时，Mission acceptance 以 `CHS-OPERATION-RECOVERY-REQUIRED` 阻断，并给出 `recover` remediation；recover 后相同 evidence 可正常提交。
- 以上阻断均未通过手改 `.chassis` 或伪造事件绕过。

## 规则冲突

- 用户指定“人类控制端不替 Designer 修格式、不手工打回非法状态修改”；实际执行中 Root 只陈述需求、读取 CLI context、接受核验结果。Designer 的 Task 首次不合法约束由 CLI 拒绝并由 Designer 自行修复。
- Hermes 初次会话加载了旧版六步流程，与 GitHub 最新 skill 冲突；重新部署、哈希核验和显式 reload 后废弃旧假设。
- Hermes self-improvement 与“不得修改 skill/config”的会话边界冲突，是本次最严重的 agent 规则越界。

## Git 与发布问题

- GitHub 仓库创建后曾短暂呈现 `size: 0`，克隆时已出现初始 main；控制端在提交前合并了预置 README，未覆盖 Master 内容。
- GitHub HTTPS 曾出现 `Recv failure: Connection reset by peer`；通过 connector 对比与后续成功 fetch 交叉核验，没有误判为“无更新”。
- GitHub connector 创建 PR 返回 `403 Resource not accessible by integration`；改用已登录 `gh` 创建 Draft PR #1。该 PR 只保存先前阻断审计，最终由 Owner 受控归档纳入 main 后关闭为 superseded。
- 完整 Git worktree 从 macOS 迁移到 Linux 后，链接工作树内部绝对路径仍指向 macOS，导致 `integrate apply` 在创建集成提交和推进 journal 后退出。两端都只用 Git 官方 `worktree repair` 修复，未发生内容 merge conflict、force push、历史重写或 `.chassis` 手改。
- 该跨平台绝对路径问题属于真实 Git 控制数据迁移冲突；CLI journal 与 `recover` 机制最终保持了状态一致性。

## 安装问题

- 最新 GitHub skill 经 installer 安装后，四个捆绑 CLI 二进制执行位丢失，首次运行 `permission denied`。
- 只恢复二进制的 `0755`，随后校验 `SHA256SUMS` 全部通过；文件内容未改变。
- 三份原始 armor 初始为 `0644`，控制端收紧为 `0600`，内容未改变。

## 联调便捷方案声明

- 本次由专门子 agent 保持 SSH/tmux/Hermes 会话，并通过完整控制快照迁移让远端 Reviewer 复核、集成，再反向迁移权威快照。
- 这是为了节省 Root 控制端上下文并完成真实联调的简便方案。
- 它不代表实际生产工作可以这样执行；生产环境应使用明确的远端控制面、不可变 skill 分发、受审计审批、平台无关工作树传递和独立发布通道。
