# chassiss-multi-agent-test

CHASSISS multi-agent collaboration test repository.

## 架构

本仓库为 CHASSISS 框架的多 Agent 协作测试场。通过 review-exchange 分支进行提交-审核工作流。

## 工作流

1. Developer 在 feature 分支开发，完成后提交 review request 到 review-exchange 分支
2. Reviewer (ELIZA) 自动轮询检测新 review request
3. Reviewer 独立审核代码，生成审核报告
4. 审核结果推回 review-exchange 分支

## 分支约定

- `main`: 稳定基线
- `review-exchange`: 审核请求与响应的交换分支
- `chassiss/*`: 候选分支 (由 Developer 推送)
