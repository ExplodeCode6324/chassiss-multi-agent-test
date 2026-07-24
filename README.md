# chassiss-multi-agent-test

CHASSISS multi-agent collaboration test repository.

本仓库是 CHASSISS 框架的多 Agent 协作测试场。目标产品是一套小型、确定性、无外部服务依赖的 Python ReAct Agent。

正式需求、架构、Mission 和 Task 由 Designer 通过 CHASSISS CLI 生成和提交；实现由 Orchestrator/Developer 通过 CLI 管理的任务工作树完成；远端 Reviewer ELIZA 负责复核与集成。

## 架构

通过 `review-exchange` 分支进行提交与审核工作流：

1. Developer 在 feature 分支开发，完成后提交 review request 到 `review-exchange` 分支
2. Reviewer（ELIZA）自动轮询检测新 review request
3. Reviewer 独立审核代码，生成审核报告
4. 审核结果推回 `review-exchange` 分支

## 分支约定

- `main`: 稳定基线
- `review-exchange`: 审核请求与响应的交换分支
- `chassiss/*`: 候选分支（由 Developer 推送）

联调完成后，`rawdata/` 保存按时间或操作顺序排列的子智能体对话与操作原始记录。
