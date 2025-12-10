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
    
    try:
        # ==========================================================
        # 【最终修正】只保留最核心的参数，删掉 use_gpu
        # use_angle_cls=False : 关闭方向检测 (提速)
        # lang="ch" : 中文模式
        # ocr_version='PP-OCRv4' : 强制使用轻量级模型 (解决内存溢出)
        # ==========================================================
        ocr = PaddleOCR(
            use_angle_cls=False, 
            lang="ch", 
            ocr_version='PP-OCRv4'
        )
    except Exception as e:
        print(f"Error initializing PaddleOCR: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"开始读取图片: {input_path}", flush=True)
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Could not read image", file=sys.stderr)
        sys.exit(1)

    print("开始识别文字...", flush=True)
    try:
        # 识别 (不传任何额外参数)
        result = ocr.ocr(input_path)
    except Exception as e:
        print(f"Error running OCR: {e}", file=sys.stderr)
        sys.exit(1)

    # 没识别到水印，直接返回原图
    if result is None or len(result) == 0 or result[0] is None:
        print("未检测到水印文字", flush=True)
        cv2.imwrite(output_path, img)
        print("SUCCESS")
        return

    # 创建掩膜
    mask = np.zeros(img.shape[:2], np.uint8)
    
    for line in result[0]:
        points = line[0]
        points = np.array(points).astype(np.int32)
        x, y, w, h = cv2.boundingRect(points)
        
        # 扩大消除范围
        pad = 5 
        cv2.rectangle(mask, (max(0, x-pad), max(0, y-pad)), (min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)), 255, -1)

    print("正在去水印...", flush=True)
    # 修复
    result_img = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

    # 保存
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
        print(f"Critical Python Error: {e}", file=sys.stderr)
        sys.exit(1)