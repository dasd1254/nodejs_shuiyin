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
    # 1. 初始化 OCR 模型
    # ⚠️ 注意：这行代码前面必须有空格！属于函数内部
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")

    # 2. 读取图片
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Could not read image", file=sys.stderr)
        sys.exit(1)

    # 3. AI 识别
    result = ocr.ocr(input_path, cls=True)

    if result is None or len(result) == 0 or result[0] is None:
        cv2.imwrite(output_path, img)
        print("SUCCESS")
        return

    # 4. 创建掩膜
    mask = np.zeros(img.shape[:2], np.uint8)
    
    for line in result[0]:
        points = line[0]
        points = np.array(points).astype(np.int32)
        x, y, w, h = cv2.boundingRect(points)
        
        pad = 5 
        cv2.rectangle(mask, (max(0, x-pad), max(0, y-pad)), (min(img.shape[1], x+w+pad), min(img.shape[0], y+h+pad)), 255, -1)

    # 5. 执行修复
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