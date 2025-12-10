import cv2
import numpy as np
import sys
import os
import logging

# 禁止 PaddleOCR 打印繁杂的日志
os.environ['FLAGS_allocator_strategy'] = 'auto_growth'
logging.getLogger("ppocr").setLevel(logging.ERROR)

from paddleocr import PaddleOCR

def remove_watermark_auto(input_path, output_path):
    # 1. 初始化 OCR 模型 (第一次运行会自动下载模型，约 15MB)
    # use_angle_cls=True: 支持识别旋转的文字
    # lang='ch': 支持中英文
 # 初始化 OCR 模型
ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    # 2. 读取图片
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Could not read image", file=sys.stderr)
        sys.exit(1)

    # 3. AI 识别：获取所有文字的坐标
    # result 结构: [[[坐标点], (文字, 置信度)], ...]
    result = ocr.ocr(input_path, cls=True)

    # 如果没识别到文字，直接保存原图
    if result is None or len(result) == 0 or result[0] is None:
        cv2.imwrite(output_path, img)
        print("SUCCESS")
        return

    # 4. 创建掩膜 (Mask)
    # mask 是一个纯黑图片，我们在上面把文字区域涂白
    mask = np.zeros(img.shape[:2], np.uint8)
    
    # 遍历识别到的每一段文字
    for line in result[0]:
        points = line[0] # 获取文字框的四个角坐标
        
        # 将坐标转换为整数格式
        points = np.array(points).astype(np.int32)
        
        # 【关键优化】稍微扩大一点识别区域 (膨胀)，保证把文字边缘也覆盖住
        # 这样去除得更干净
        # 计算矩形包围框
        x, y, w, h = cv2.boundingRect(points)
        
        # 在 mask 上画出白色实心矩形 (扩大 5 像素)
        pad = 5 
        cv2.rectangle(mask, (max(0, x-pad), max(0, y-pad)), (min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)), 255, -1)

    # 5. 执行修复 (Inpainting)
    # 使用 Telea 算法，根据 mask 修复原图
    # radius=5: 修复半径，根据水印大小调整
    result_img = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

    # 6. 保存图片
    cv2.imwrite(output_path, result_img)
    print("SUCCESS")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        remove_watermark_auto(input_file, output_file)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)