import cv2
import numpy as np
import sys
import os
import logging

# ==========================================
# 【自检代码】打印当前 Numpy 版本
# ==========================================
print(f"当前 Numpy 版本: {np.__version__}", flush=True)
if np.__version__.startswith("2"):
    print("❌ 警告：检测到 Numpy 2.0，这将导致 PaddleOCR 崩溃！请检查依赖安装。", flush=True)

# 禁用日志
os.environ['FLAGS_allocator_strategy'] = 'auto_growth'
logging.getLogger("ppocr").setLevel(logging.ERROR)

from paddleocr import PaddleOCR

def remove_watermark_auto(input_path, output_path):
    print("正在初始化 OCR 模型...", flush=True)
    
    try:
        # 只保留核心参数，使用轻量级模型
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
        result = ocr.ocr(input_path)
    except Exception as e:
        print(f"Error running OCR: {e}", file=sys.stderr)
        # 这里如果报错，通常就是 Numpy 版本不对
        sys.exit(1)

    # 没识别到水印，返回原图
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
        
        pad = 5 
        cv2.rectangle(mask, (max(0, x-pad), max(0, y-pad)), (min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)), 255, -1)

    print("正在去水印...", flush=True)
    result_img = cv2.inpaint(img, mask, 5, cv2.INPAINT_TELEA)

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
        print(f"Critical Python Error: {e}", file=sys.stderr)
        sys.exit(1)