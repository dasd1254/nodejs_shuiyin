import cv2
import numpy as np
import sys
import os
import logging

# 1. 禁用日志
os.environ['FLAGS_allocator_strategy'] = 'auto_growth'
logging.getLogger("ppocr").setLevel(logging.ERROR)

from paddleocr import PaddleOCR

def remove_watermark_auto(input_path, output_path):
    print("正在初始化 OCR 模型...", flush=True)
    
    # ==========================================================
    # 【核心修复】 强制使用 PP-OCRv4 轻量级模型！
    # ocr_version='PP-OCRv4' : 指定使用 v4 版本的轻量模型
    # use_gpu=False : 强制使用 CPU (防报错)
    # enable_mkldnn=False : 关闭加速库以节省内存
    # ==========================================================
    try:
        ocr = PaddleOCR(
            use_angle_cls=False, 
            lang="ch", 
            ocr_version='PP-OCRv4', 
            use_gpu=False,
            enable_mkldnn=False
        )
    except Exception as e:
        print(f"Error initializing PaddleOCR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"开始读取图片: {input_path}", flush=True)
    # 2. 读取图片
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Could not read image", file=sys.stderr)
        sys.exit(1)

    # 3. 识别
    print("开始识别文字...", flush=True)
    try:
        # 此时已经没有 cls 参数了，不会报错
        result = ocr.ocr(input_path)
    except Exception as e:
        print(f"Error running OCR: {e}", file=sys.stderr)
        sys.exit(1)

    # 如果没识别到文字，直接保存原图
    if result is None or len(result) == 0 or result[0] is None:
        print("未检测到水印文字", flush=True)
        cv2.imwrite(output_path, img)
        print("SUCCESS")
        return

    # 4. 创建掩膜
    mask = np.zeros(img.shape[:2], np.uint8)
    
    for line in result[0]:
        points = line[0]
        points = np.array(points).astype(np.int32)
        x, y, w, h = cv2.boundingRect(points)
        
        # 扩大消除范围
        pad = 5 
        cv2.rectangle(mask, (max(0, x-pad), max(0, y-pad)), (min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)), 255, -1)

    # 5. 修复
    print("正在去水印...", flush=True)
    result_img = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

    # 6. 保存
    cv2.imwrite(output_path, result_img)
    print("SUCCESS")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python process.py <input> <output>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        remove_watermark_auto(input_file, output_file)
    except Exception as e:
        # 捕获所有未知错误并打印，防止静默崩溃
        print(f"Critical Python Error: {e}", file=sys.stderr)
        sys.exit(1)