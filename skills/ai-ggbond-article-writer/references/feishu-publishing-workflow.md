# 飞书知识库发布工作流

## 概述

文章写完后，可通过 `lark-cli` 将内容发布到飞书知识库。适用于需要在飞书团队内分享长文、调研报告、方法论等场景。

## 前置条件

- lark-cli 已安装并配置（路径：`/opt/homebrew/Cellar/node/25.8.2/lib/node_modules/@larksuite/cli/bin/lark-cli`）
- 飞书账号已授权
- 知识库 space_id 已知

## 完整工作流

### 步骤 1：查看知识库结构

```bash
LARK=/opt/homebrew/Cellar/node/25.8.2/lib/node_modules/@larksuite/cli/bin/lark-cli

# 列出所有知识库
$LARK wiki spaces list

# 列出知识库根节点
$LARK wiki nodes list --params '{"space_id":"<SPACE_ID>"}'

# 列出某节点的子节点
$LARK wiki nodes list --params '{"space_id":"<SPACE_ID>","parent_node_token":"<NODE_TOKEN>"}'
```

### 步骤 2：创建文档节点

```bash
# 创建主文档
$LARK wiki +node-create --space-id <SPACE_ID> --title "文档标题" --obj-type docx

# 创建子文档（挂在主文档下）
$LARK wiki +node-create --space-id <SPACE_ID> --parent-node-token <PARENT_NODE> --title "子文档标题" --obj-type docx
```

返回结果中的 `obj_token` 是文档 ID，用于后续写入内容。

### 步骤 3：写入内容

```bash
# 从文件写入（推荐）
$LARK docs +update --doc <OBJ_TOKEN> --mode overwrite --markdown @/path/to/file.md

# 直接写入
$LARK docs +update --doc <OBJ_TOKEN> --mode overwrite --markdown "# 标题\n\n内容..."
```

**注意**：
- `--mode overwrite` 会覆盖全部内容
- `--mode append` 追加到末尾
- lark-cli 对 `@file` 路径有限制，建议先 `cp` 到用户主目录再引用

### 步骤 4：验证

```bash
# 获取文档内容
$LARK docs fetch --doc <OBJ_TOKEN>
```

## 文档结构设计建议

对于多章节的长文或系列报告，建议采用「主文档 + 子文档」结构：

```
主文档（目录/概览）
├── 子文档 1：第一部分
├── 子文档 2：第二部分
└── 子文档 3：第三部分
```

主文档放总览和导航，子文档放详细内容。这样读者可以按需跳转，也方便后续更新单个章节。

## 已知坑点

1. **lark-cli 不在 PATH 中**：需用绝对路径 `/opt/homebrew/Cellar/node/25.8.2/lib/node_modules/@larksuite/cli/bin/lark-cli`
2. **文件路径问题**：`@file` 语法有时不识别绝对路径，建议先 `cp` 到 `~/` 再引用
3. **v1 API 废弃警告**：`docs +update` 使用 v1 API 会显示 deprecation warning，功能仍可用
4. **nodes list 参数格式**：用 `--params '{"key":"value"}'` JSON 格式，不用 `--space-id` 等独立 flag
5. **子节点查询**：需要指定 `parent_node_token`，否则只返回根节点
