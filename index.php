<?php
/**
 * 表情包模板分发接口 (整合美化版 UI)
 * 管理员信息由部署者配置
 */

// --- 1. 基础配置 ---
require_once __DIR__ . '/config.php';

// --- 2. 获取请求参数 ---
$text  = isset($_GET["keyword"]) && is_string($_GET['keyword']) ? trim($_GET["keyword"]) : '';
$wxid  = isset($_GET['wxid']) && is_string($_GET['wxid']) ? trim($_GET['wxid']) : '';
$start = isset($_GET["start"]) ? (int)$_GET["start"] : 0;

// --- 3. 落地页逻辑：如果没有传 wxid，显示美化提示界面 ---
if (empty($wxid)) {
    ?>
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>授权访问 - 表情包助手</title>
        <style>
            * { box-sizing: border-box; }
            body { 
                margin: 0; padding: 0; 
                display: flex; justify-content: center; align-items: center; 
                min-height: 100vh; 
                background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%); 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            }
            .card { 
                background: rgba(255, 255, 255, 0.9); 
                backdrop-filter: blur(10px);
                padding: 40px 20px; 
                border-radius: 24px; 
                box-shadow: 0 15px 35px rgba(0,0,0,0.1); 
                text-align: center; 
                max-width: 380px; width: 90%;
                border: 1px solid white;
            }
            .icon-box {
                width: 80px; height: 80px;
                background: #fff;
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex; align-items: center; justify-content: center;
                font-size: 40px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
            }
            h2 { color: #2c3e50; margin: 10px 0; font-size: 22px; }
            p { color: #7f8c8d; line-height: 1.6; font-size: 15px; margin: 5px 0; }
            .contact-box { 
                background: #4facfe; 
                color: white;
                padding: 12px 20px; 
                border-radius: 12px; 
                display: inline-block;
                margin-top: 25px;
                text-decoration: none;
                font-weight: bold;
                transition: transform 0.2s;
            }
            .contact-box:hover { transform: scale(1.05); }
            .footer { margin-top: 40px; font-size: 12px; color: #bdc3c7; }
        </style>
    </head>
    <body>
        <div class="card">
            <div class="icon-box">🔐</div>
            <h2>访问受限</h2>
            <p>该接口仅对授权用户开放</p>
            <p>请联系管理员申请授权</p>
            <p><a href="/neon/">✨ 打开霓虹 GIF 编辑器</a></p>
            <div style="margin-top:15px; border-top: 1px solid #eee; padding-top:15px;">
                <p>联系本站管理员：</p>
                <div class="contact-box">管理员</div>
            </div>
            <div class="footer">Doutu API Service v2.0</div>
        </div>
    </body>
    </html>
    <?php
    exit();
}

// --- 4. 接口逻辑：权限校验 ---
$users = doutu_read_users();

if (!in_array($wxid, $users, true)) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        "items" => [["url" => $host . "/static/dog.png"]],
        "code"  => 403,
        "msg"   => "授权失效，请联系本站管理员"
    ], JSON_UNESCAPED_UNICODE);
    exit();
}

// --- 5. 接口逻辑：参数校验 ---
if ($text === '') {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode([
        "items" => [],
        "code"  => 200,
        "msg"   => "关键词不能为空"
    ], JSON_UNESCAPED_UNICODE);
    exit();
}

if ($start != 0) {
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(["items" => [], "code" => 201, "msg" => "没有更多数据啦"], JSON_UNESCAPED_UNICODE);
    exit();
}

if (mb_strlen($text, 'UTF-8') > 120) {
    http_response_code(400);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode(['items' => [], 'code' => 400, 'msg' => '关键词最多 120 字'], JSON_UNESCAPED_UNICODE);
    exit;
}

// --- 6. 接口逻辑：模板分发 ---
$templates = [
    "xin", "duilian", "jianzhi", "xinfeng", "baidu1", "baidu", "FBI", 
    "niebi", "youyunvhai", "wj", "110", "96110", "NOKIA", "toukan", 
    "wanou", "mayun", "qingchun", 
    "luxun1", "opa334", "shengzhi", "heisi1", "dpp", "mm1", 
    "mm2", "mm3", "mm4", "heikuang"
];

$items = [];

// 6.1 加入本地模板
foreach ($templates as $tp) {
    $items[] = ["url" => $host . "/template/" . $tp . ".php?text=" . urlencode($text)];
}


// 6.2 Add the local Neon generator to the existing items/url contract.
$items[] = ['url' => $host . '/generate?' . http_build_query([
    'text' => $text, 'color' => 'neon', 'theme' => 'dark', 'wrap' => 'true'
], '', '&', PHP_QUERY_RFC3986)];

// 6.3 Optional third-party source: disabled until a token is supplied privately.
$thirdPartyToken = getenv('DOUTU_THIRD_PARTY_TOKEN') ?: '';
$textParam = getenv('DOUTU_THIRD_PARTY_TEXT_PARAM') ?: 'text';
$apiUrl = 'https://openapi.52vmy.cn/api/wl/doutu?' . http_build_query([
    'token' => $thirdPartyToken, $textParam => $text
], '', '&', PHP_QUERY_RFC3986);

// 设置一个简单的超时上下文，防止第三方接口卡死导致你的服务器也卡死
$context = stream_context_create([
    'http' => [
        'timeout' => 3 // 超时时间设置为 3 秒
    ]
]);

// 请求第三方接口 (@ 符号用来抑制网络错误产生的警告信息)
$apiResponse = $thirdPartyToken !== '' ? @file_get_contents($apiUrl, false, $context) : false;

if ($apiResponse) {
    $apiData = json_decode($apiResponse, true);
    
    // 校验接口是否返回 200 并且 data 里面有数据
    if (isset($apiData['code']) && $apiData['code'] == 200 && !empty($apiData['data'])) {
        foreach ($apiData['data'] as $imgData) {
            // 提取每张图片的真实 URL 并塞进我们的返回列表里
            if (!empty($imgData['url'])) {
                $items[] = ["url" => $imgData['url']];
            }
        }
    }
}

// --- 7. 输出最终 JSON ---
header('Content-Type: application/json; charset=utf-8');
echo json_encode([
    "items" => $items,
    "code"  => 200,
    "msg"   => "success"
], JSON_UNESCAPED_UNICODE);
exit();
