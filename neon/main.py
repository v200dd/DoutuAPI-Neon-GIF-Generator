# main.py
from pathlib import Path
from threading import BoundedSemaphore
from typing import Literal

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import Response, FileResponse
from fastapi.staticfiles import StaticFiles
from gif_generator import generate_gif_bytes

BASE_DIR = Path(__file__).resolve().parent
render_slots = BoundedSemaphore(2)

app = FastAPI(
    title="Text to GIF API (Word Wrap Edition)",
    version="1.6.0"
)

# 挂载静态文件
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
app.mount("/neon/static", StaticFiles(directory=BASE_DIR / "static"), name="neon-static")

@app.get("/")
async def read_index():
    return FileResponse(BASE_DIR / 'static/index.html')

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

@app.get("/generate")
def get_gif(
    text: str = Query(..., min_length=1, max_length=120),
    frame_count: int = Query(20, ge=1, le=60),
    delay: int = Query(100, ge=20, le=2000),
    color: str = Query(None, description="Color name, hex code, or effect: 'rainbow', 'rainbow_flow', 'wave', 'bounce', 'neon', 'breathing:color1:color2'"),
    width_pixels: int = Query(500, ge=120, le=1600),
    theme: Literal["transparent", "dark", "light"] = Query("transparent"),
    # --- 新增参数 ---
    wrap: bool = Query(False, description="Auto wrap text to new lines if it exceeds width. Disables scrolling.")
):
    if not text.strip():
        raise HTTPException(status_code=422, detail="Text cannot be blank")
    if not render_slots.acquire(blocking=False):
        raise HTTPException(status_code=503, detail="Generator busy; retry later")
    try:
        # 呼吸灯逻辑检查
        if color and color.startswith('breathing:') and frame_count < 20:
             frame_count = 20
        
        # 如果开启换行，强制静态/呼吸（因为多行滚动通常不需要）
        # 但我们保留 frame_count 用于呼吸灯效果
        
        gif_buffer = generate_gif_bytes(
            text=text,
            frame_count=frame_count,
            delay=delay,
            font_path=None,
            text_color_param=color,
            width_pixels=width_pixels,
            theme=theme,
            auto_wrap=wrap # 传入参数
        )

        if not gif_buffer:
            raise HTTPException(status_code=400, detail="Failed.")

        return Response(content=gif_buffer.getvalue(), media_type="image/gif")
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Server Error")
    finally:
        render_slots.release()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
