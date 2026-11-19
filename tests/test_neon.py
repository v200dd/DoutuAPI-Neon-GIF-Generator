import io
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'neon'))
from main import app, render_slots

client = TestClient(app)


@pytest.mark.parametrize('color', [None, 'rainbow', 'rainbow_flow', 'wave', 'bounce', 'neon', 'breathing:#ff0000:#0000ff'])
def test_effects(color):
    params = {'text': '斗图测试', 'width_pixels': 320, 'frame_count': 20, 'theme': 'dark', 'wrap': True}
    if color:
        params['color'] = color
    r = client.get('/generate', params=params)
    assert r.status_code == 200, r.text
    assert r.headers['content-type'] == 'image/gif'
    image = Image.open(io.BytesIO(r.content))
    assert image.width == 320
    if color in ['neon', 'rainbow_flow', 'wave', 'bounce'] or (color and color.startswith('breathing:')):
        assert image.n_frames > 1


def test_one_frame_scroll_regression():
    r = client.get('/generate', params={'text': 'Hi', 'frame_count': 1, 'theme': 'dark'})
    assert r.status_code == 200
    assert Image.open(io.BytesIO(r.content)).n_frames == 1


@pytest.mark.parametrize('params', [
    {'text': ''}, {'text': '   '}, {'text': 'x' * 121},
    {'text': 'Hi', 'frame_count': 61}, {'text': 'Hi', 'width_pixels': 119},
    {'text': 'Hi', 'theme': 'invalid'}, {'text': 'Hi', 'delay': 2001},
])
def test_bounds(params):
    assert client.get('/generate', params=params).status_code == 422


def test_pixel_budget():
    r = client.get('/generate', params={'text': '测试' * 60, 'width_pixels': 120, 'frame_count': 60, 'wrap': True})
    assert r.status_code == 400


def test_busy_and_health():
    render_slots.acquire()
    render_slots.acquire()
    try:
        assert client.get('/generate', params={'text': 'Hi'}).status_code == 503
        assert client.get('/healthz').status_code == 200
    finally:
        render_slots.release()
        render_slots.release()


def test_ui_assets():
    assert '/neon/static/script.js' in client.get('/').text
    assert client.get('/neon/static/script.js').status_code == 200
    assert client.get('/neon/static/style.css').status_code == 200
