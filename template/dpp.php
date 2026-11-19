<?php
require "./common.php";

// 获取输入的文字
$text = $_GET["text"];
// 拆分文本为多行
$lines = explode("\n", mb_wordwrap($text, 5, "\n"));

// 创建默认画布
$width = 350;
$height = 350;

// 设置字体大小
$fontSize = 26;

// 设置文本位置
$x = 72;
$y = 160;

// 指定背景图路径（PNG 格式）
$backgroundImagePath = "../static/dpp.png";
// 提供的字体文件路径
$font = doutu_font('../static/langman.ttf');

// 创建图片
$image = imagecreatetruecolor($width, $height);

// 为图片分配一个 Alpha 通道
$transparent = imagecolorallocatealpha($image, 0, 0, 0, 127);
imagefill($image, 0, 0, $transparent);

// 启用 Alpha 混合
imagesavealpha($image, true);
imagealphablending($image, true);

// 载入背景图
$backgroundImage = imagecreatefrompng($backgroundImagePath);
imagecopyresampled($image, $backgroundImage, 0, 0, 0, 0, $width, $height, imagesx($backgroundImage), imagesy($backgroundImage));

// 设置文本颜色
$textColor = imagecolorallocate($image, 0, 0, 0);

// 逐行绘制文字
foreach ($lines as $line) {
    imagettftext($image, $fontSize, 0, $x, $y, $textColor, $font, $line);
    $y += $fontSize + 15; // 垂直间距
}

// 发送头部信息，告诉浏览器这是一个图片
header('Content-Type: image/png');

// 输出图片
imagepng($image);

// 释放内存
imagedestroy($image);
imagedestroy($backgroundImage);

?>