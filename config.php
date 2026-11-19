<?php
// Configuration and private data never live in the public source tree.
$host = rtrim(getenv('DOUTU_PUBLIC_URL') ?: 'http://127.0.0.1:8000', '/');
$usersFile = getenv('DOUTU_USERS_FILE') ?: '/var/lib/doutu/users.json';

function doutu_read_users(): array {
    global $usersFile;
    if (!is_file($usersFile)) return [];
    $users = json_decode(file_get_contents($usersFile), true);
    return is_array($users) ? array_values(array_filter($users, 'is_string')) : [];
}

// Lock the entire read/modify/write transaction, not just the final write.
function doutu_change_user(string $wxid, bool $add): void {
    global $usersFile;
    $fp = fopen($usersFile, 'c+');
    if (!$fp || !flock($fp, LOCK_EX)) throw new RuntimeException('Cannot lock users file');
    try {
        $users = json_decode(stream_get_contents($fp), true) ?: [];
        $users = array_values(array_filter($users, 'is_string'));
        if ($add && !in_array($wxid, $users, true)) $users[] = $wxid;
        if (!$add) $users = array_values(array_filter($users, fn($u) => $u !== $wxid));
        $json = json_encode($users, JSON_UNESCAPED_UNICODE | JSON_THROW_ON_ERROR);
        rewind($fp);
        if (fwrite($fp, $json) !== strlen($json) || !ftruncate($fp, strlen($json))) {
            throw new RuntimeException('Cannot write users file');
        }
        fflush($fp);
    } finally {
        flock($fp, LOCK_UN);
        fclose($fp);
    }
}
