<?php
require_once __DIR__ . '/config.php';
session_set_cookie_params([
    'httponly' => true, 'samesite' => 'Strict',
    'secure' => parse_url($host, PHP_URL_SCHEME) === 'https'
]);
session_start();
$password = getenv('ADMIN_PASSWORD') ?: '';
function admin_json(array $data, int $status = 200): never {
    http_response_code($status);
    header('Content-Type: application/json; charset=utf-8');
    echo json_encode($data, JSON_UNESCAPED_UNICODE);
    exit;
}
if ($password === '') admin_json(['status' => 'error', 'msg' => 'ADMIN_PASSWORD 未配置'], 503);
$_SESSION['csrf'] ??= bin2hex(random_bytes(24));
$action = is_string($_GET['action'] ?? null) ? $_GET['action'] : '';
try {
    if (in_array($action, ['api_add', 'api_delete'], true)) {
        $apiKey = $_SERVER['HTTP_X_API_KEY'] ?? $_POST['key'] ?? $_GET['key'] ?? '';
        if (!is_string($apiKey) || !hash_equals($password, $apiKey)) {
            admin_json(['status' => 'error', 'msg' => '认证失败，密钥错误'], 403);
        }
        $wxid = $_POST['wxid'] ?? $_GET['wxid'] ?? '';
        if (!is_string($wxid) || trim($wxid) === '' || strlen($wxid) > 128) {
            admin_json(['status' => 'error', 'msg' => 'wxid 不能为空且最多 128 字节'], 400);
        }
        doutu_change_user(trim($wxid), $action === 'api_add');
        admin_json(['status' => 'success', 'msg' => $action === 'api_add' ? '添加成功' : '删除成功']);
    }
    if ($action === 'login') {
        $pwd = $_POST['pwd'] ?? '';
        if (is_string($pwd) && hash_equals($password, $pwd)) {
            session_regenerate_id(true);
            $_SESSION['admin'] = true;
            admin_json(['status' => 'success']);
        }
        admin_json(['status' => 'fail'], 403);
    }
    if ($action === 'logout') {
        session_destroy();
        header('Location: /admin.php');
        exit;
    }
    if (in_array($action, ['add', 'delete'], true)) {
        if (empty($_SESSION['admin'])) admin_json(['status' => 'error', 'msg' => '请先登录'], 403);
        $csrf = $_POST['csrf'] ?? '';
        if (!is_string($csrf) || !hash_equals($_SESSION['csrf'], $csrf)) {
            admin_json(['status' => 'error', 'msg' => 'CSRF 校验失败'], 403);
        }
        $wxid = $_POST[$action === 'add' ? 'new_id' : 'id'] ?? '';
        if (!is_string($wxid) || trim($wxid) === '' || strlen($wxid) > 128) {
            admin_json(['status' => 'error', 'msg' => 'wxid 无效'], 400);
        }
        doutu_change_user(trim($wxid), $action === 'add');
        admin_json(['status' => 'success']);
    }
    $currentUsers = doutu_read_users();
} catch (Throwable $error) {
    error_log('Doutu user storage failure: ' . get_class($error));
    admin_json(['status' => 'error', 'msg' => '授权名单读写失败'], 500);
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Wxid 授权中心</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        body { font-family: 'Inter', sans-serif; background-color: #f8fafc; }
        .glass-card { background: rgba(255, 255, 255, 0.9); backdrop-filter: blur(10px); }
    </style>
</head>
<body class="min-h-screen flex items-center justify-center p-4">

    <div class="w-full max-w-md">
        <?php if (!isset($_SESSION['admin'])): ?>
        <div class="glass-card shadow-2xl rounded-2xl p-8 border border-gray-100">
            <div class="text-center mb-8">
                <div class="bg-blue-600 w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg shadow-blue-200">
                    <i class="fas fa-shield-halved text-white text-2xl"></i>
                </div>
                <h2 class="text-2xl font-bold text-gray-800">后台管理</h2>
                <p class="text-gray-500 text-sm">请输入管理密码以继续</p>
            </div>
            
            <div class="space-y-4">
                <div class="relative">
                    <i class="fas fa-lock absolute left-3 top-3.5 text-gray-400"></i>
                    <input type="password" id="loginPwd" 
                           class="w-full pl-10 pr-4 py-3 bg-gray-50 border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all" 
                           placeholder="输入管理密码">
                </div>
                <button onclick="login()" 
                        class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 rounded-xl transition-all shadow-md active:scale-[0.98]">
                    立即登录
                </button>
            </div>
        </div>

        <?php else: ?>
        <div class="glass-card shadow-2xl rounded-2xl overflow-hidden border border-gray-100">
            <div class="bg-white px-6 py-4 border-b border-gray-100 flex justify-between items-center">
                <h2 class="text-lg font-bold text-gray-800 flex items-center">
                    <i class="fas fa-users-gear mr-2 text-blue-600"></i> 授权管理
                </h2>
                <a href="?action=logout" class="text-gray-400 hover:text-red-500 transition-colors text-sm font-medium">
                    <i class="fas fa-right-from-bracket mr-1"></i> 退出
                </a>
            </div>

            <div class="p-6">
                <div class="flex gap-2 mb-6">
                    <div class="relative flex-1">
                        <i class="fas fa-user-plus absolute left-3 top-3 text-gray-400"></i>
                        <input type="text" id="newWxid" 
                               class="w-full pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none transition-all" 
                               placeholder="输入 wxid">
                    </div>
                    <button onclick="addUser()" 
                            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium shadow-sm transition-all active:scale-95">
                        添加
                    </button>
                </div>

                <div id="userList" class="space-y-2 max-h-[400px] overflow-y-auto pr-1">
                    <?php if (empty($currentUsers)): ?>
                        <div class="text-center py-10 text-gray-400">
                            <i class="fas fa-inbox text-4xl mb-3 opacity-20"></i>
                            <p>暂无授权用户</p>
                        </div>
                    <?php else: ?>
                        <?php foreach ($currentUsers as $u): ?>
                        <div class="group flex justify-between items-center p-3 bg-gray-50 hover:bg-white hover:shadow-md rounded-xl border border-transparent hover:border-blue-100 transition-all">
                            <span class="text-gray-700 font-mono text-sm"><?php echo htmlspecialchars($u, ENT_QUOTES, 'UTF-8'); ?></span>
                            <button onclick="delUser(<?php echo htmlspecialchars(json_encode($u), ENT_QUOTES, 'UTF-8'); ?>)" 
                                    class="opacity-0 group-hover:opacity-100 text-red-400 hover:text-red-600 p-2 transition-all"
                                    title="删除">
                                <i class="fas fa-trash-can"></i>
                            </button>
                        </div>
                        <?php endforeach; ?>
                    <?php endif; ?>
                </div>
                
                <div class="mt-4 pt-4 border-t border-gray-50 text-center">
                    <p class="text-xs text-gray-400">当前共有 <?php echo count($currentUsers); ?> 个授权 ID</p>
                </div>
            </div>
        </div>
        <?php endif; ?>
    </div>

    <script>
        // 回车键支持
        document.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                if (document.getElementById('loginPwd')) login();
                else if (document.getElementById('newWxid')) addUser();
            }
        });

        async function login() {
            const pwd = document.getElementById('loginPwd').value;
            if(!pwd) return;
            const fd = new FormData(); fd.append('csrf', <?php echo json_encode($_SESSION['csrf']); ?>); fd.append('pwd', pwd);
            const res = await fetch('?action=login', {method: 'POST', body: fd});
            const data = await res.json();
            if(data.status === 'success') location.reload(); else alert('❌ 密码错误');
        }

        async function addUser() {
            const id = document.getElementById('newWxid').value;
            if(!id) return;
            const fd = new FormData(); fd.append('csrf', <?php echo json_encode($_SESSION['csrf']); ?>); fd.append('new_id', id);
            await fetch('?action=add', {method: 'POST', body: fd});
            location.reload();
        }

        async function delUser(id) {
            if(!confirm('确定要移除该授权吗？')) return;
            const fd = new FormData(); fd.append('csrf', <?php echo json_encode($_SESSION['csrf']); ?>); fd.append('id', id);
            await fetch('?action=delete', {method: 'POST', body: fd});
            location.reload();
        }
    </script>
</body>
</html>