# WMS Evidence Album — CC-04 FR
# Functional Record

## 1. 功能交付

CC-04 已交付登录 Portal 客户访问自己有效证据 Album 的完整基础查看器：

- 已发布且未过期 Album 的客户隔离列表；
- Page 展示和切换；
- 全部、图片、视频筛选；
- 图片缩略图、灯箱和全屏；
- 视频内联播放；
- 单文件下载；
- GET/HEAD 媒体访问和单 Range 响应；
- 未授权资源统一 404；
- Item ID 作为媒体资源边界；
- 授权完成后才读取附件。

## 2. 范围确认

CC-04 不包含 ZIP、多选下载、匿名 Token、客户编辑/上传、评论、点赞、视频转码或 CC-05 功能。

## 3. 决策登记

- **TDD-Q-003**：本版本不展示来源信息，返回数据不含部分来源字段；后续可在独立变更中增加稳定的可选结构。
- **TDD-Q-007**：图片缩略图使用 Pillow 临时生成；不保存缩略图附件、不改变原文件；视频不转码。

## 4. 验收依据

- 实施历史见 [CC-04 IHR](./wd_evidence_album_CC-04_IHR_v1.0.0.md)。
- 自动化证据见 [CC-04 ATR](./wd_evidence_album_CC-04_ATR_v1.0.0.md)。
- 用户确认见 [CC-04 HVR](./wd_evidence_album_CC-04_HVR_v1.0.0.md)。
