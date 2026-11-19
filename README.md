# 斗图 API + Neon GIF 一体化 Docker 部署

把原 PHP 斗图源码与 [Neon GIF Generator](https://github.com/v200dd/DoutuAPI-Neon-GIF-Generator) 合并为一个 Compose 项目。
保留原 `keyword / wxid / start` 接口、27 个本地模板和授权后台；返回列表额外加入一个本机生成的霓虹 GIF。

## 架构与入口

一个 Nginx 网关对外暴露端口，PHP Apache 与 Python FastAPI 只在容器内部通信。

| 地址 | 用途 |
| --- | --- |
| `/`、`/index.php` | 斗图入口；无 wxid 时显示提示页及 Neon 编辑器链接 |
| `/?keyword=你好&wxid=已授权ID&start=0` | `items: [{url: ...}], code, msg` 格式，27 张 PNG + 1 个 GIF |
| `/admin.php` | 登录并管理授权 ID |
| `/neon/` | Neon 可视化 GIF 编辑器 |
| `/generate?text=你好&color=neon&theme=dark&wrap=true` | 直接生成 GIF |
| `/docs` | GIF 参数文档 |
| `/healthz` | GIF 服务健康检查 |

`start != 0` 仍返回 `code: 201` 和空列表；未授权 wxid 仍返回 JSON `code: 403`。
无关键词时返回 `code: 200` 和空列表，不再跳到外部斗图网站。

## 新服务器部署

要求 Docker Engine 与 Docker Compose v2。仓库目录不要放入已有网站的公开根目录。

```bash
git clone -b integrate-doutu-docker https://github.com/v200dd/DoutuAPI-Neon-GIF-Generator.git doutu
cd doutu
cp .env.example .env
chmod 600 .env
# 编辑 .env：必须设置 ADMIN_PASSWORD，并修改 DOUTU_PUBLIC_URL 为实际域名。
docker compose up -d --build --wait
docker compose ps
docker compose logs --tail=100
```

如果合并了 PR，可以改为克隆 `main`。原项目使用同一个端口时，先停止旧容器，再启动本项目；不要删除旧服务的数据。

浏览器访问 `http://服务器IP:8000/neon/`；后台是 `http://服务器IP:8000/admin.php`。
机器人继续调用原 `/?keyword=...&wxid=...` 地址，无须改成 GIF 接口。

### 配置

| 变量 | 说明 |
| --- | --- |
| `ADMIN_PASSWORD` | 必填；后台密码，也是管理 API 的密钥；没有默认密码 |
| `DOUTU_PUBLIC_URL` | 返回图片 URL 的真实外部地址，如你的 HTTPS 域名；不要填容器内部地址 |
| `DOUTU_PORT` | 对外端口，默认 8000 |
| `DOUTU_BIND_IP` | 默认 0.0.0.0；在同机 HTTPS 反代后面部署可改为 127.0.0.1 |
| `DOUTU_THIRD_PARTY_TOKEN` | 可选；空值完全关闭第三方斗图请求 |
| `DOUTU_THIRD_PARTY_TEXT_PARAM` | 第三方文字参数名，暂按 `text` 组装；启用前按供应商文档确认 |

`.env`、原后台密码、第三方 token、原授权名单均不会随源码提交。
必须使用 HTTPS 保护后台与管理 API；反向代理整站即可，Nginx 已解决 `/static/` 命名冲突。

### 导入原授权名单（仅在自己的服务器上操作）

新部署默认名单为空。可在后台逐个添加，或将旧 `users.json` 导入持久卷：

```bash
# 把旧 users.json 放在当前目录外，以下路径替换成它的实际位置。
docker compose exec -T doutu sh -c 'cat > /var/lib/doutu/users.json && chown www-data:www-data /var/lib/doutu/users.json && chmod 600 /var/lib/doutu/users.json' < /实际私有目录/users.json
```

导入时避免同时修改后台名单，确认原文件是 JSON 字符串数组。数据保存在命名卷 `doutu-data`，普通重建不会丢失。
**不要执行 `docker compose down -v`，这会删除授权数据。**

### 管理 API

保留 `action=api_add` 和 `action=api_delete`；推荐 POST 搭配 `X-API-Key` 请求头。
旧版 URL `key` 参数仍兼容，但可能进入代理日志，不建议继续使用。

```bash
# 在本机从 .env 取出配置，不要把真实密码写入共享脚本。
set -a; . ./.env; set +a
curl -X POST -H "X-API-Key: $ADMIN_PASSWORD" -d 'wxid=待授权ID' \
  'http://127.0.0.1:8000/admin.php?action=api_add'
```

wxid 是兼容旧机器人协议的名单标识，不是强认证凭证；直接模板和 GIF URL 保持公开，不能视为完整的付费访问控制。

## 升级、备份与回退部署

```bash
# 升级前导出授权名单到私有路径，并记录当前提交。
umask 077
git rev-parse HEAD
docker compose exec -T doutu cat /var/lib/doutu/users.json > users.backup.json
git pull --ff-only
docker compose up -d --build --wait
```

备份文件含用户标识，应移出仓库；`*.json` 备份不可提交。部署回退时 checkout 已记录的提交再重建，保留同一个数据卷。
此仓库的原始 Neon 服务结构已移入 `neon/`，不要再用旧的根目录 `python main.py` 启动命令。

## 测试与限制

```bash
python -m pip install -r neon/requirements.txt pytest httpx
pytest -q tests/test_neon.py
# 启动 Compose 后，仅在测试环境运行；会添加和删除测试授权用户。
ADMIN_PASSWORD="$ADMIN_PASSWORD" python tests/smoke.py http://127.0.0.1:8000
```

GitHub Actions 会运行上述单元测试、完整 Docker 构建、27 张 PNG 与 GIF 的真实 HTTP 检查、授权增删、CSRF 校验、静态资源路由和重启后数据持久性测试。
GIF 最多 120 字、60 帧，宽度 120–1600，帧延迟 20–2000ms；另设像素预算及两任务并发上限。
修复原 `frame_count=1` 滚动除零错误，GIF 渲染不再阻塞异步健康检查。
公网网关对 GIF 按源 IP 限速；多人共用同一个上游反代时，可根据部署环境调整限速策略。

## 原字体与轻量仓库版

原字体体积较大，上传网络多次超时，因此仓库不包含上传附件中的 `static/*.ttf`、`static/*.TTF`、`static/*.otf`。
Docker 镜像使用 Neon 仓库中已有的 `neon/fonts/jiying.ttf` 作为中文备用字体；所有模板仍可生成，但字体外观可能与旧版不同。
本次交付的完整代码 ZIP 仍含原字体：将其中 `static/` 的字体文件复制到克隆目录，然后重建即可恢复每个模板原有字体。
模板始终优先使用原字体；没有原字体才启用备用，不需要修改接口或模板配置。

## 版权

Neon 代码的 MIT 声明保留于 `neon/LICENSE`。
上传的 PHP、背景图和字体保留原始权利，没有自动改成 MIT；用于再分发或商业服务前需确认对应素材与字体授权。
