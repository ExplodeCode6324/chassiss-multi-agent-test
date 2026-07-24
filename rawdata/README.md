# CHASSISS 多智能体联调原始数据

> 标注：联调的原始数据

本目录保存 2026-07-24 `chassiss-multi-agent-test` 真实联调的操作记录。记录按文件编号和文件内时间戳排序。

## 文件

1. `000-controller-timeline.md`：人类代理控制端的操作顺序、CLI 结果和风险观察。
2. `001-designer.md`：Designer Agent 的逐时操作原始记录。
3. `002-orchestrator-developer.md`：兼任 Orchestrator/Developer Agent 的逐时操作原始记录。
4. `003-github-monitor.md`：GitHub Monitor Agent 的两轮轮询原始记录。
5. `004-subagent-conversations.md`：父子代理指令和消息的投递顺序记录。

## 脱敏说明

- 只记录凭据路径和 CLI 返回的非秘密身份元数据。
- 不包含 armor、私钥、GitHub token 或其他认证正文。
- CLI 错误若可能带入 armor 文本，只保留错误码、诊断类别和脱敏后的路径。

## 测试边界

测试因缺少 Master Root、项目尚未初始化且 Orchestrator armor 与 GitHub `main` 的角色策略不兼容而被 CLI 阻断。没有通过手工编辑 `.chassis/`、伪造状态、重签凭据或直接 Git 开发绕过阻断。
