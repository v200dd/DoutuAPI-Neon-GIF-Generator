document.addEventListener('DOMContentLoaded', () => {
    const elements = {
        text: document.getElementById('text-input'),
        effect: document.getElementById('effect-select'),
        theme: document.getElementById('theme-select'),
        color: document.getElementById('color-input'),
        width: document.getElementById('width-input'),
        frames: document.getElementById('frames-input'),
        delay: document.getElementById('delay-input'),
        wrap: document.getElementById('wrap-input'),

        widthVal: document.getElementById('width-val'),
        framesVal: document.getElementById('frames-val'),
        delayVal: document.getElementById('delay-val'),

        preview: document.getElementById('gif-preview'),
        loading: document.getElementById('loading'),
        urlInput: document.getElementById('url-input'),
        downloadBtn: document.getElementById('download-btn'),
        copyBtn: document.getElementById('copy-btn')
    };

    let debounceTimer;

    // 更新滑块数值显示
    elements.width.addEventListener('input', (e) => elements.widthVal.textContent = e.target.value);
    elements.frames.addEventListener('input', (e) => elements.framesVal.textContent = e.target.value);
    elements.delay.addEventListener('input', (e) => elements.delayVal.textContent = e.target.value);

    // 主更新函数
    function updatePreview() {
        elements.loading.classList.add('active');

        const params = new URLSearchParams();
        params.append('text', elements.text.value || 'Hello');
        params.append('width_pixels', elements.width.value);
        params.append('frame_count', elements.frames.value);
        params.append('delay', elements.delay.value);
        params.append('theme', elements.theme.value);

        if (elements.wrap.checked) {
            params.append('wrap', 'true');
        }

        // 处理颜色/特效逻辑
        let colorParam = elements.color.value.trim();
        const effect = elements.effect.value;

        if (effect) {
            if (effect === 'breathing' && colorParam.includes(':')) {
                // 用户手动输入了呼吸灯参数，直接使用或添加前缀
                if (!colorParam.startsWith('breathing:')) {
                    colorParam = `breathing:${colorParam}`;
                }
                params.append('color', colorParam);
            } else if (effect === 'breathing') {
                // 如果未指定颜色，使用默认呼吸灯效果
                params.append('color', 'breathing:#ff0000:#0000ff');
            } else {
                // 其他特效如 wave, bounce, neon, rainbow_flow
                params.append('color', effect);
            }
        } else if (colorParam) {
            params.append('color', colorParam);
        }

        const url = `/generate?${params.toString()}`;
        elements.urlInput.value = window.location.origin + url;

        // 加载图片
        const img = new Image();
        img.onload = () => {
            elements.preview.src = url;
            elements.loading.classList.remove('active');
        };
        img.onerror = () => {
            elements.loading.classList.remove('active');
            // 可以显示错误占位符
        };
        img.src = url;
    }

    // 防抖更新
    function triggerUpdate() {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(updatePreview, 800); // 800ms 防抖
    }

    // 绑定事件监听器
    const inputs = [
        elements.text, elements.effect, elements.theme,
        elements.color, elements.width, elements.frames,
        elements.delay, elements.wrap
    ];

    inputs.forEach(input => {
        input.addEventListener('input', triggerUpdate);
        input.addEventListener('change', triggerUpdate); // 针对 select/checkbox
    });

    // 下载按钮
    elements.downloadBtn.addEventListener('click', () => {
        const link = document.createElement('a');
        link.href = elements.preview.src;
        link.download = 'neon_text.gif';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });

    // 复制 URL 按钮
    elements.copyBtn.addEventListener('click', () => {
        elements.urlInput.select();
        document.execCommand('copy');
        const originalText = elements.copyBtn.textContent;
        elements.copyBtn.textContent = '已复制!';
        setTimeout(() => elements.copyBtn.textContent = originalText, 2000);
    });

    // 初始加载
    updatePreview();
});
