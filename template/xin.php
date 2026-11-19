<?php
require "./common.php";

// 写信模版

// 要显示的文字
$text = $_GET["text"];
// 拆分文本为多行
$lines = explode("\n", mb_wordwrap($text, 7, "\n"));

// 创建默认画布
$width = 590;
$height = 390;

// 设置字体大小
$fontSize = 50;

// 设置文本位置
$x = 25;
$y = 87;


// 默认背景图片
$backgroundImagePath = '../static/line05.png';
// 提供的字体文件路径
$font = doutu_font('../static/yingbi.ttf');
// 根据文字行数切换背景图片
if (count($lines) == 1) {
    $backgroundImagePath = '../static/line01.png';
    $height = 120;
}elseif (count($lines) == 2) {
    $backgroundImagePath = '../static/line02.png';
    $height = 180;
}elseif (count($lines) == 3) {
    $backgroundImagePath = '../static/line03.png';
    $height = 250;
}elseif (count($lines) == 4) {
    $backgroundImagePath = '../static/line04.png';
    $height = 310;
}elseif (count($lines) == 5) {
    $backgroundImagePath = '../static/line05.png';
    $height = 390;
}

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

// 将背景图复制到画布上
imagecopyresampled($image, $backgroundImage, 0, 0, 0, 0, $width, $height, imagesx($backgroundImage), imagesy($backgroundImage));

// 设置文本颜色
$textColor = imagecolorallocate($image, 60, 60, 50);


// 逐行绘制文字
foreach ($lines as $line) {
    imagettftext($image, $fontSize, 0, $x, $y, $textColor, $font, $line);
    $y += $fontSize + 20; // 垂直间距
}

// 发送头部信息，告诉浏览器这是一个图片
header('Content-Type: image/png');

// 输出图片
imagepng($image);

// 释放内存
imagedestroy($image);
imagedestroy($backgroundImage);

?>