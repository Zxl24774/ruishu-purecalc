# ruishu-purecalc

`ruishu-purecalc` 是一个面向授权 Ruishu/Rivers Security 目标的 Codex skill 仓库。它的目标不是提供一套可直接套用到所有站点的固定破解器，而是把瑞数纯算工作拆成可验证的阶段：同会话采集 412 挑战、解码 `cd`、复原关键身份值、构建站点 profile、生成 Cookie T、验证入口页 200，并在入口页通过后再处理 Ajax suffix。

> 仅用于你有权限测试、集成或维护的系统。

## 适用场景

- 首次入口请求返回 `412`，页面中包含 `$_ts.cd`、`$_ts.nsd`，响应里有 `xxxS` cookie。
- 需要脱离浏览器生成 Cookie T，并让入口页第二跳返回 200。
- Cookie T 已能解密，但入口页第二跳返回短 400，需要定位 `basearr`/TLV/profile 差异。
- 入口页已经 200，但业务 API 返回 400，需要分析 URL suffix/signature。
- 同一份采集器在不同机器上表现不一致，需要区分固定 profile、fresh session 和机器敏感参数。

如果目标没有返回 412，也没有 `$_ts.cd`/`$_ts.nsd`，不要强行套用瑞数流程。先检查是否是缓存信任 cookie、重定向、路径不对，或根本不是瑞数防护。

## 核心原则

把稳定算法和站点差异分离：

- 稳定层：PRNG、key 提取结构、Huffman、AES-CBC、CRC32、自定义 Base64、Cookie T 包装流程。
- 站点 profile：TLV 字段顺序与长度、`type3` 环境字段、`type2` cp1 映射、`type10` 分支、`type6`、`type7`、codeUid JS 选择、Ajax suffix 布局。
- Fresh session：`cd`、`nsd`、`S`、`T`、45 个 keys、`JSESSIONID`、`r2t`、当前时间、`nd`、suffix 值。
- 机器敏感项：User-Agent、platform、viewport、language、timezone、系统时间、代理、TLS 行为。

不要通过变量名 hook 瑞数 VM。`nsd` 会影响变量名，可靠锚点应来自常量、AST 结构、字节长度、TLV 形状和多组通过样本。

## 推荐工作流

1. 采集入口页 412 挑战，保存同一个 `requests.Session` 中的 `cd`、`nsd`、JS URL、`S` cookie、响应头和 HTML。
2. 解码 `cd`，提取 45 个 keys，并验证关键长度：`len(keys) == 45`、`len(keys[2]) == 48`、`len(keys[16]) == 16`、`len(keys[17]) == 16`。
3. 根据 `nsd` 和 JS 结构复原 `functionsNameSort`、`mainFunctionIdx`、`codeUid` 等外层身份值。
4. 解码浏览器通过的 Cookie T，把 `basearr` 按 `type,length,payload` 解析成 TLV。
5. 用站点 profile 生成 Python `basearr`，与浏览器样本逐字段比较。
6. 先做 hybrid check：浏览器/sdenv 的 `basearr` + 纯 Python 加密。如果不能让入口页第二跳 200，先修加密或 key 提取。
7. 用 fresh 412 bundle 生成 Cookie T，设置同会话的 `S+T` cookie，请求入口页并要求返回 200。
8. 至少 3 组 fresh session 通过入口页 200 后，再处理业务 API。
9. 若入口页 200 但 API 400，再分析 Ajax suffix。不要复用 curl 中复制来的 suffix。

详细阶段表见 `references/workflow.md`。

## 目录结构

```text
.
├── SKILL.md
├── README.md
├── references/
│   ├── workflow.md
│   ├── constants.md
│   ├── basearr-profile.md
│   ├── ajax-suffix.md
│   ├── failure-matrix.md
│   └── portability.md
├── scripts/
│   ├── compare_basearr.py
│   └── profile_lint.py
├── templates/
│   └── site_profile.json
└── evals/
    └── evals.json
```

## 参考文档

- `SKILL.md`：skill 入口说明、决策树、阶段门禁和常见错误。
- `references/workflow.md`：从 412 采集到业务 API 验证的完整阶段。
- `references/constants.md`：常见稳定常量、key 含义和 Cookie T 加密流水线。
- `references/basearr-profile.md`：TLV profile、分支识别、字段来源分类、`type=2` 映射策略。
- `references/ajax-suffix.md`：入口页 200 后的 API 400/suffix 分析流程。
- `references/failure-matrix.md`：第二跳 412、短 400、API 400、跨机器失败等诊断顺序。
- `references/portability.md`：固定值、fresh 值和机器敏感值的迁移检查。

## 脚本用法

### 比较两组 basearr

`scripts/compare_basearr.py` 接收两个 JSON 文件。文件可以是整数数组，也可以是包含 `basearr`、`browser_basearr` 或 `python_basearr` 字段的对象。

```powershell
python scripts/compare_basearr.py browser_basearr.json python_basearr.json
```

输出会显示整体长度、TLV 解析结束位置、每个字段的 type/length/position，以及前 40 个差异字节。

### 校验站点 profile

先复制模板：

```powershell
Copy-Item templates/site_profile.json profiles/my-target.json
```

然后填写目标、入口路径、headers、cookie、basearr 分支和验证命令，再运行：

```powershell
python scripts/profile_lint.py profiles/my-target.json
```

当前 lint 只做轻量结构校验，确保必需顶层字段存在，并检查 `basearr.branches` 的基本字段。

## Site Profile 模板

`templates/site_profile.json` 用来记录站点差异，主要字段包括：

- `target`、`entry_path`、`api_paths`：目标和接口路径。
- `headers`：请求头和 `type3` 中必须保持一致的 UA/language 等。
- `challenge`：`cd`、`nsd`、`S` cookie 和主 JS 的来源。
- `cookie`：Cookie T 名称表达式和 enable cookie。
- `code_uid`：`keys[33]`、`keys[34]` 以及不同分支的 JS index。
- `suffix`：Ajax suffix 参数名、是否需要、path/body/time/random 等来源。
- `basearr`：TLV 字段顺序和分支条件。
- `type3`、`type2`：环境字段和 cp1 映射。
- `verification`：入口页 200、API JSON 和 fresh session 验证命令。

站点差异应该进入 profile，不要硬编码到通用加密逻辑里。

## 故障定位速查

| 现象 | 优先检查 |
| --- | --- |
| 首次请求不是 412 | 路径、cookies、缓存信任、重定向、是否非瑞数路径 |
| 第二跳仍是 412 | Cookie 名称、同会话 `S+T`、T 格式、key 提取、挑战 freshness |
| 第二跳短 400 | `basearr` TLV、分支长度、`type10`、`type2`、`codeUid`、`type3` |
| 入口页 200 但 API 400 | Ajax suffix/signature、`nd`、路径/请求体序列化、当前 session keys |
| 入口页 200 但 API 返回 HTML | Referer、XHR headers、Content-Type、session cookie、路由 |
| 换机器失败 | UA/type3 一致性、系统时间、代理、TLS、headers |

调试顺序应从可解密结果开始：先解密自己生成的 Cookie T，确认 `basearr` 是预期内容；再解码浏览器通过样本；然后逐 TLV 字段比较。不要在入口页第二跳未 200 前修改 Ajax suffix。

## 验证标准

一个目标只有满足以下条件，才算完成纯算接入：

- fresh session 下不用浏览器生成 Cookie T。
- 入口页第二跳返回 200，且至少 3 组 fresh 412 bundle 通过。
- 若包含业务 API，必须在 fresh session 中拿到预期 JSON，而不是只复用抓包 curl。
- 站点 profile 记录了固定值、fresh 值、分支规则和验证命令。
- 400/412 失败时有清晰的定位路径。

## Eval 样例

`evals/evals.json` 记录了该 skill 应覆盖的典型问题，包括：

- 412 Cookie T 纯 Python 计划。
- 第二跳短 400 的 TLV/profile 诊断。
- Cookie T 长度分支策略。
- 跨机器迁移参数分类。
- 入口页 200 后 API 400 的 Ajax suffix 分析。
- 非瑞数目标的排除判断。

这些 eval 可以作为后续修改 `SKILL.md` 或 references 时的回归检查清单。
