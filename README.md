# 霓虹 GIF 生成器 (Neon GIF Generator)

这是一个基于 Python FastAPI 的 GIF 生成工具，专注于生成酷炫的赛博朋克风格文字 GIF。

它不仅支持基础的文字滚动，还支持多种动态特效，如彩虹流动、波浪、弹跳和霓虹脉冲。项目内置了现代化的 Web 界面，方便用户直接在浏览器中创作。

## ✨ 主要功能

*   **Web 可视化界面**：所见即所得，实时预览 GIF 效果。
*   **酷炫特效**：
    *   🌈 **彩虹流动 (Rainbow Flow)**：动态流动的彩虹渐变。
    *   🌊 **波浪 (Wave)**：文字像波浪一样上下起伏。
    *   🏀 **弹跳 (Bounce)**：文字整体有节奏地跳动。
    *   💡 **霓虹脉冲 (Neon Pulse)**：模拟霓虹灯的闪烁和发光效果。
    *   🌬️ **呼吸灯 (Breathing)**：双色渐变呼吸效果。
*   **高度可定制**：支持自定义文字颜色（Hex/名称）、背景主题（透明/深色/浅色）、宽度、帧数和延迟。
*   **自动换行**：支持长文本自动换行居中显示。
*   **多种字体**：自动从 `fonts` 目录随机加载字体，支持中文字体。

## 🚀 快速开始

### 1. 环境要求

*   Python 3.8+
*   依赖库：`fastapi`, `uvicorn`, `pillow`

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 启动服务

```bash
python main.py
```

或者使用 uvicorn:

```bash
uvicorn main:app --reload
```

### 4. 使用 Web 界面

服务启动后，打开浏览器访问：

**http://127.0.0.1:8000/**

即可看到图形化操作界面。

### 5. Docker 部署 (推荐)

本项目支持 Docker 一键部署，无需手动配置 Python 环境。

**步骤：**

1.  确保已安装 Docker 和 Docker Compose。
2.  在项目根目录下运行：

```bash
docker-compose up -d --build
```

3.  等待构建完成后，访问 **http://服务器IP:8000** 即可使用。

*注意：Docker 部署会自动安装中文字体支持。*

## 📖 API 使用文档

如果你想通过 API 直接生成 GIF，可以访问 `/generate` 接口。

**示例 URL:**

```
http://127.0.0.1:8000/generate?text=Hello&color=neon&theme=dark
```

**参数说明:**

| 参数 | 类型 | 默认值 | 说明 |
| :--- | :--- | :--- | :--- |
| `text` | string | (必填) | 要生成的文字内容 |
| `color` | string | None | 颜色名称、Hex 代码或特效名 (`rainbow_flow`, `wave`, `bounce`, `neon`) |
| `width_pixels` | int | 500 | GIF 图片宽度 |
| `frame_count` | int | 20 | 动画帧数 (特效模式下建议 >= 20) |
| `delay` | int | 100 | 每帧延迟 (毫秒) |
| `theme` | string | transparent | 背景主题: `transparent`, `dark`, `light` |
| `wrap` | bool | False | 是否自动换行 (开启后禁用滚动) |

## 📂 项目结构

```
.
├── main.py              # FastAPI 主程序 & 路由
├── gif_generator.py     # 核心 GIF 生成逻辑
├── static/              # Web 界面静态资源
│   ├── index.html       # 主页
│   ├── style.css        # 样式表
│   └── script.js        # 前端逻辑
├── fonts/               # 字体文件目录
└── requirements.txt     # 项目依赖
```

## 📝 许可证

MIT License
