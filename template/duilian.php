<?php
require "./common.php";

// 对联模版

// 要显示的文字
$text = $_GET["text"];
// 拆分文本为多行
$lines = explode("\n", mb_wordwrap($text, 6, "\n"));

// 创建默认画布
$width = 640;
$height = 452;

// 设置字体大小
$fontSize = 47;

// 设置文本位置
$x = 67;
$y = 82;


// 默认背景图片
$backgroundImagePath = '../static/duilian1.png';
// 提供的字体文件路径
$font = doutu_font('../static/AaJiuZhongXiao-2.ttf');
// 根据文字行数切换背景图片
if (count($lines) == 1) {
    $backgroundImagePath = '../static/duilian1.png';
    $height = 113;
}elseif (count($lines) == 2) {
    $backgroundImagePath = '../static/duilian2.png';
    $height = 226;
}elseif (count($lines) == 3) {
    $backgroundImagePath = '../static/duilian3.png';
    $height = 339;
}elseif (count($lines) == 4) {
    $backgroundImagePath = '../static/duilian4.png';
    $height = 452;
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
$textColor = imagecolorallocate($image, 0, 0, 0);


// 逐行绘制文字
foreach ($lines as $line) {
    imagettftext($image, $fontSize, 0, $x, $y, $textColor, $font, $line);
    
    $y += $fontSize + 59; // 垂直间距
    
}





// 发送头部信息，告诉浏览器这是一个图片
header('Content-Type: image/png');

// 输出图片
imagepng($image);

// 释放内存
imagedestroy($image);
imagedestroy($backgroundImage);

?>