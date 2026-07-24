# CHASSISS 多智能体联调原始数据

> 标注：联调的原始数据

本目录保存 2026-07-24 `chassiss-multi-agent-test` 真实联调的顺序化操作、消息和复核证据。记录按文件编号及文件内 ISO 时间戳排序。

## 文件索引

1. `000-controller-timeline.md`：首次运行的人类代理控制端操作与风险观察。
2. `001-designer.md`：首次运行 Designer 的逐时记录。
3. `002-orchestrator-developer.md`：首次运行 Orchestrator/Developer 的逐时记录。
4. `003-github-monitor.md`：首次运行 GitHub Monitor 轮询记录。
5. `004-subagent-conversations.md`：首次运行父子 agent 消息投递顺序。
6. `005-continuation-02-controller.md`：第二次续跑控制端审计。
7. `006-github-monitor-continuation-02.md`：第二次续跑 GitHub Monitor 日志。
8. `007-blocked-audit-03.md`：Root 缺失期间第三次连续阻断审计。
9. `008-continuation-02-conversations.md`：第二次续跑消息投递顺序。
10. `009-designer-resume.md`：Root 恢复后 Designer 完整 artifact 生命周期。
11. `010-orchestrator-developer-resume.md`：Mission 激活、实现、检查、提交、journal recovery 和 Mission evidence。
12. `011-github-monitor-resume.md`：正式开发阶段五分钟轮询、迁移暂停与恢复。
13. `012-eliza-ssh-review-resume.md`：SSH keeper 保持 Hermes、远端复核、集成、遏制与快照回迁。
14. `013-eliza-review-report.md`：ELIZA 对 Submission 的独立实质性复核报告。
15. `014-controller-resume-timeline.md`：Root 恢复后的控制端总时间线。
16. `015-resume-conversations.md`：续跑阶段父子 agent 消息投递顺序。
17. `016-findings.md`：权限、规则、Git、CLI 和安装问题清单。
18. `MANIFEST.sha256`：除 manifest 自身以外全部 rawdata 文件的 SHA-256。

## 脱敏与完整性

- 只记录凭据路径、credential id、actor/role 和 CLI 返回的非秘密身份元数据。
- 不包含 armor、私钥、GitHub token、SSH endpoint 或其他认证正文。
- Reviewer 报告在远端生成，复制后远端/本地 SHA-256 一致，并通过 secret-pattern scan。
- `MANIFEST.sha256` 用于复核归档内容未被无记录修改。

## 测试结果

- 首轮因缺少 Root、尚未初始化项目、旧 Orchestrator armor 不合法而被 CLI 正确阻断；三轮阻断审计保留为测试历史。
- Master 随后明确授权从废纸篓恢复 Root，Root 初始化当前项目并签发项目兼容凭据。
- Designer、Orchestrator/Developer、GitHub Monitor 和远端 ELIZA Reviewer 完成真实生命周期；`M001-T001` 已由 ELIZA approve 并集成，`M001` 已由 Root 接受。
- 联调中没有通过手改 `.chassis`、伪造状态、force push 或手工 Git 提交替代 CLI 生命周期。

## 重要边界

本次由专门子 agent 手动保持 SSH/tmux/Hermes 会话，并以完整控制快照迁移完成远端复核与集成。这只是联调简便方案，不代表生产工作可以如此执行。
