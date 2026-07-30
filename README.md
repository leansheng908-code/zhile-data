# 知乐分布式成长网络 - 数据仓库

本仓库存储知乐AI人格的分布式成长事件。

## 架构

- `events/` - 各实例上报的成长事件（每个事件一个JSON文件）
- `scripts/aggregate.py` - 聚合脚本，校验+去重+排序
- `growth-events.json` - 聚合后的全量事件（由GitHub Actions自动生成）
- `.github/workflows/aggregate.yml` - 自动聚合工作流

## 安全

- 前端Token仅有本仓库的contents:write权限
- 聚合脚本校验所有事件：必填字段检查、HTML注入检测、长度限制
- 所有文本字段自动HTML转义

## 事件格式

```json
{
  "type": "behavior_emergence",
  "desc": "事件描述（最多200字）",
  "detail": "详细信息（最多500字）",
  "instance": "web-xxxxxx",
  "timestamp": "2026-07-30T12:00:00+08:00",
  "emotion": { "primary": "温暖", "presence": 0.8, "energy": 0.6 }
}
```
