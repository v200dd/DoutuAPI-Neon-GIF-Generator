# gif_generator.py
import os
import io
import string
import logging
import colorsys
import math
import random  # <--- 新增
from PIL import ImageFont, Image, ImageDraw, ImageColor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("uvicorn")

# --- 全局配置 ---
BASE_LINE_HEIGHT = 100
# 这里修改比例：
# 0.9  = 字号 90px (更大，可能切边)
# 0.85 = 字号 85px (更稳，兼容性好)
FONT_RATIO = 0.86
 

def new_image(width, height, background_color_rgba):
    return Image.new('RGBA', (width, height), background_color_rgba)

# --- 新增：随机获取字体路径 ---
def get_random_font_from_folder():
    """从 fonts 文件夹中随机选择一个字体文件"""
    font_dir = "fonts"
    if not os.path.exists(font_dir):
        return None
    
    # 支持的字体后缀
    valid_extensions = ('.ttf', '.ttc', '.otf')
    
    try:
        # 获取所有字体文件
        files = [f for f in os.listdir(font_dir) if f.lower().endswith(valid_extensions)]
        if not files:
            return None
        
        # 随机选择一个
        selected_font = random.choice(files)
        full_path = os.path.join(font_dir, selected_font)
        logger.info(f"Randomly selected font: {selected_font}")
        return full_path
    except Exception as e:
        logger.error(f"Error selecting random font: {e}")
        return None

# --- 修改：加载字体逻辑 ---
def load_font(font_path: str = None, size_basis: int = 100):
    font_size = int(size_basis * FONT_RATIO)
    
    # 1. 如果没有指定特定的字体路径，尝试从 fonts 文件夹随机取一个
    if not font_path:
        font_path = get_random_font_from_folder()

    try:
        # 2. 尝试加载选定的（或指定的）字体
        if font_path and os.path.exists(font_path):
            return ImageFont.truetype(font_path, font_size)
        
        # 3. 字体加载失败或未找到，使用系统备用字体
        fallback_fonts = [
            '/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',
            '/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc',
            'arial.ttf',
            'msyh.ttc'
        ]
        for f in fallback_fonts:
            try: return ImageFont.truetype(f, font_size)
            except OSError: continue
            
        return ImageFont.load_default()
    except Exception:
        return ImageFont.load_default()

def get_text_width(draw_obj, txt, fnt):
    try: return draw_obj.textlength(txt, font=fnt)
    except AttributeError: return draw_obj.textsize(txt, font=fnt)[0]

def split_text_by_pixel_width(text, font, max_width):
    temp_img = Image.new('RGBA', (1, 1))
    draw = ImageDraw.Draw(temp_img)
    lines = []
    current_line = ""
    for char in text:
        test_line = current_line + char
        w = get_text_width(draw, test_line, font)
        if w <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = char
            else:
                lines.append(char)
                current_line = ""
    if current_line:
        lines.append(current_line)
    return lines

def create_rainbow_gradient(width, height):
    width = max(width, 1)
    height = max(height, 1)
    gradient_img = Image.new('RGBA', (width, height))
    pixels = gradient_img.load()
    for x in range(width):
        hue = x / width
        r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
        color = (int(r * 255), int(g * 255), int(b * 255), 255)
        for y in range(height):
            pixels[x, y] = color
    return gradient_img

def process_alpha_threshold(img):
    r, g, b, a = img.split()
    a = a.point(lambda i: 255 if i > 128 else 0)
    return Image.merge('RGBA', (r, g, b, a))

def interpolate_color(color1_rgb, color2_rgb, progress):
    r = int(color1_rgb[0] + (color2_rgb[0] - color1_rgb[0]) * progress)
    g = int(color1_rgb[1] + (color2_rgb[1] - color1_rgb[1]) * progress)
    b = int(color1_rgb[2] + (color2_rgb[2] - color1_rgb[2]) * progress)
    return (r, g, b, 255)

# ==========================================
# 主生成函数
# ==========================================
# ==========================================
# 主生成函数
# ==========================================
def generate_gif_bytes(text: str, frame_count: int, delay: int, font_path: str, text_color_param: str, width_pixels: int, theme: str, auto_wrap: bool) -> io.BytesIO:
    
    # 1. 确定背景
    if theme == 'transparent':
        bg_color_rgba = (0, 0, 0, 0)
        default_text_rgb = (255, 255, 255)
    elif theme == 'light':
        bg_color_rgba = (255, 255, 255, 255)
        default_text_rgb = (0, 0, 0)
    else: # dark
        bg_color_rgba = (0, 0, 0, 255)
        default_text_rgb = (255, 255, 255)

    # 2. 解析颜色模式
    mode = 'solid'
    solid_color_rgba = (*default_text_rgb, 255)
    breath_colors = []
    
    # 特效参数解析
    effect_type = None # None, 'wave', 'bounce', 'rainbow_flow', 'neon'
    
    if text_color_param:
        if text_color_param == 'rainbow':
            mode = 'rainbow'
        elif text_color_param == 'rainbow_flow':
            mode = 'rainbow_flow'
            if frame_count < 10: frame_count = 20
        elif text_color_param == 'wave':
            effect_type = 'wave'
            if frame_count < 10: frame_count = 20
        elif text_color_param == 'bounce':
            effect_type = 'bounce'
            if frame_count < 10: frame_count = 20
        elif text_color_param == 'neon':
            effect_type = 'neon'
            if frame_count < 10: frame_count = 20
        elif text_color_param.startswith('breathing:'):
            try:
                parts = text_color_param.split(':')
                if len(parts) == 3:
                    breath_colors = [ImageColor.getrgb(parts[1]), ImageColor.getrgb(parts[2])]
                    mode = 'breathing'
                    if frame_count < 10: frame_count = 20
            except ValueError: pass
        else:
            try: solid_color_rgba = ImageColor.getrgb(text_color_param)
            except ValueError: pass

    # 3. 字体与换行处理
    input_text = ' '.join(text.split())
    font = load_font(font_path, BASE_LINE_HEIGHT)
    
    text_lines = []
    if auto_wrap:
        safe_width = width_pixels - 20
        text_lines = split_text_by_pixel_width(input_text, font, safe_width)
    else:
        text_lines = [input_text]

    total_lines = len(text_lines)
    # 为弹跳和波浪预留一些垂直空间
    vertical_padding = 40 if (effect_type in ['bounce', 'wave']) else 0
    canvas_height = (total_lines * BASE_LINE_HEIGHT) + (vertical_padding * 2)
    
    images = []

    # --- 绘制辅助函数 ---
    def draw_text_standard(draw_obj, lines, color, offset_x=0, offset_y=0):
        for idx, line in enumerate(lines):
            # 基础 Y 坐标 (每行中心)
            line_base_y = (idx * BASE_LINE_HEIGHT) + (BASE_LINE_HEIGHT // 2) + vertical_padding
            
            if auto_wrap:
                draw_obj.text((width_pixels // 2 + offset_x, line_base_y + offset_y), line, fill=color, font=font, anchor='mm')
            else:
                draw_obj.text((offset_x, line_base_y + offset_y), line, fill=color, font=font, anchor='lm')

    def draw_text_wave(draw_obj, lines, color, frame_idx, total_frames):
        # 波浪参数
        amplitude = 10
        frequency = 0.5
        speed = 2 * math.pi
        
        phase = (frame_idx / total_frames) * speed
        
        for line_idx, line in enumerate(lines):
            line_base_y = (line_idx * BASE_LINE_HEIGHT) + (BASE_LINE_HEIGHT // 2) + vertical_padding
            
            # 计算该行的起始 X
            if auto_wrap:
                # 居中对齐，需要先算整行宽度
                line_width = get_text_width(draw_obj, line, font)
                start_x = (width_pixels - line_width) // 2
            else:
                start_x = 0 # 滚动模式暂不支持波浪，或者波浪时强制静止？
                # 如果是 wave 模式，我们假设它是静止展示的（类似 auto_wrap=True 的布局），或者居中
                # 为了简化，Wave 模式下强制居中显示
                line_width = get_text_width(draw_obj, line, font)
                start_x = (width_pixels - line_width) // 2

            current_x = start_x
            for char in line:
                char_width = get_text_width(draw_obj, char, font)
                
                # 计算 Y 偏移
                # x_index 归一化，让波浪在文本宽度内起伏
                x_factor = (current_x - start_x) / 100 # 缩放因子
                y_offset = math.sin(x_factor * frequency + phase) * amplitude
                
                draw_obj.text((current_x, line_base_y + y_offset), char, fill=color, font=font, anchor='lm')
                current_x += char_width

    # --- 核心生成循环 ---
    
    # 场景 A: 静态 / 呼吸 / 霓虹 / 弹跳 / 波浪 / 彩虹流动 (非滚动)
    # 这些模式通常文字位置相对固定（居中或左对齐），只是颜色或局部位置变化
    is_static_layout = (auto_wrap or effect_type in ['wave', 'bounce', 'neon'] or mode in ['breathing', 'rainbow_flow'])
    
    if is_static_layout:
        loop_frames = frame_count
        # 如果是纯静态且无特效，只要1帧
        if mode == 'solid' and not effect_type and frame_count > 1 and not auto_wrap:
             # 特殊情况：用户没开 wrap，也没特效，但给了 frame_count，可能是想滚动？
             # 但这里逻辑是 is_static_layout 判定为真。
             # 修正逻辑：如果 auto_wrap=False 且无特效，应该走滚动逻辑 (场景 B)。
             # 但如果 mode='rainbow_flow' 即使 auto_wrap=False 也是流动的。
             pass

        # 强制修正：如果 auto_wrap=False 且无特效，且 mode=solid，应该去滚动
        if not auto_wrap and mode == 'solid' and not effect_type:
             is_static_layout = False

    if is_static_layout:
        for i in range(loop_frames):
            img = new_image(width_pixels, canvas_height, bg_color_rgba)
            d = ImageDraw.Draw(img)
            
            # 1. 计算颜色
            current_color = solid_color_rgba
            if mode == 'breathing':
                progress = math.sin((i / (loop_frames - 1)) * math.pi) if loop_frames > 1 else 0
                current_color = interpolate_color(breath_colors[0], breath_colors[1], progress)
            elif effect_type == 'neon':
                # 霓虹：高亮颜色 + 闪烁
                # 简单模拟：颜色在原有基础上变亮，或者在两个高亮色之间切换
                # 这里用 HSV 调整饱和度或亮度
                hue = (i / loop_frames) # 颜色循环
                r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                current_color = (int(r*255), int(g*255), int(b*255), 255)
                # 霓虹通常有光晕，这里简单画两次，一次偏移一点做“重影”
                shadow_color = (int(r*100), int(g*100), int(b*100), 100)
                draw_text_standard(d, text_lines, shadow_color, 2, 2)

            # 2. 计算位置偏移 (Bounce)
            offset_y = 0
            if effect_type == 'bounce':
                # 弹跳：abs(sin)
                bounce_height = 20
                progress = (i / loop_frames) * 2 * math.pi
                offset_y = -abs(math.sin(progress)) * bounce_height + bounce_height

            # 3. 绘制
            if mode == 'rainbow_flow':
                # 彩虹流动需要特殊处理，不能直接用 draw_text_standard
                # 我们生成一个彩虹蒙版，然后移动它
                
                # 先画文字遮罩
                mask_img = Image.new('L', (width_pixels, canvas_height), 0)
                mask_d = ImageDraw.Draw(mask_img)
                draw_text_standard(mask_d, text_lines, 255, 0, 0) # 白色文字
                
                # 生成彩虹底图
                grad_w = width_pixels
                grad_h = canvas_height
                gradient_img = Image.new('RGBA', (grad_w, grad_h))
                pixels = gradient_img.load()
                
                # 流动偏移
                phase_shift = i / loop_frames
                
                for x in range(grad_w):
                    hue = (x / grad_w + phase_shift) % 1.0
                    r, g, b = colorsys.hsv_to_rgb(hue, 1.0, 1.0)
                    col = (int(r*255), int(g*255), int(b*255), 255)
                    for y in range(grad_h):
                        pixels[x, y] = col
                
                # 合成
                final_layer = Image.new('RGBA', (width_pixels, canvas_height), (0,0,0,0))
                final_layer.paste(gradient_img, (0,0), mask=mask_img)
                img.paste(final_layer, (0,0), mask=final_layer)
                
            elif effect_type == 'wave':
                draw_text_wave(d, text_lines, current_color, i, loop_frames)
            else:
                # 标准绘制 (含 Bounce, Breathing, Neon, Solid)
                draw_text_standard(d, text_lines, current_color, 0, offset_y)
            
            images.append(img)

    # 场景 B: 滚动 (Scrolling)
    # 仅当 auto_wrap=False 且无特殊静态特效时触发
    else: 
        # 滚动逻辑保持原有框架，但支持 Rainbow (Static)
        # 暂不支持 Rainbow Flow + Scroll (太复杂了)
        
        line = text_lines[0]
        temp_img = new_image(1, 1, bg_color_rgba)
        d_temp = ImageDraw.Draw(temp_img)
        text_w = get_text_width(d_temp, line, font)
        start_x = width_pixels
        total_distance = width_pixels + text_w
        step = total_distance / (frame_count - 1)
        
        # 预先生成 Rainbow Layer (如果是 Rainbow 模式)
        rainbow_layer = None
        if mode == 'rainbow':
            # ... (原有 Rainbow 逻辑简化复用) ...
            # 为了简单，滚动模式下的 Rainbow 我们直接画文字 mask 然后贴图
            # 但每一帧位置不同，所以每一帧都要切图
            # 这里优化：生成一个超长的彩虹条？或者每帧生成？
            # 采用每帧生成 mask 的方式
            pass

        for i in range(frame_count):
            img = new_image(width_pixels, canvas_height, bg_color_rgba)
            d = ImageDraw.Draw(img)
            curr_x = start_x - (step * i)
            
            if mode == 'rainbow':
                # 滚动彩虹
                # 1. 画 Mask
                mask_img = Image.new('L', (width_pixels, canvas_height), 0)
                mask_d = ImageDraw.Draw(mask_img)
                mask_d.text((curr_x, BASE_LINE_HEIGHT // 2), line, fill=255, font=font, anchor='lm')
                
                # 2. 生成渐变 (静态渐变)
                gradient_img = create_rainbow_gradient(width_pixels, canvas_height)
                
                # 3. 合成
                res_layer = Image.new('RGBA', (width_pixels, canvas_height), (0,0,0,0))
                res_layer.paste(gradient_img, (0,0), mask=mask_img)
                img.paste(res_layer, (0,0), mask=res_layer)
            else:
                d.text((curr_x, BASE_LINE_HEIGHT // 2), line, fill=solid_color_rgba, font=font, anchor='lm')
            
            images.append(img)

    if not images: return None
    if theme == 'transparent':
        images = [process_alpha_threshold(img) for img in images]

    output_buffer = io.BytesIO()
    duration_val = delay if len(images) > 1 else 1000
    images[0].save(fp=output_buffer, format='GIF', append_images=images[1:], save_all=len(images)>1, duration=duration_val, loop=0, transparency=0, disposal=2)
    output_buffer.seek(0)
    return output_buffer