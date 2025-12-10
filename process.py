# process.py
import cv2
import numpy as np
import sys
import os

def remove_watermark(input_path, output_path):
    # 1. 检查文件是否存在
    if not os.path.exists(input_path):
        print(f"Error: Input file not found at {input_path}", file=sys.stderr)
        sys.exit(1)

    # 2. 读取图片
    img = cv2.imread(input_path)
    if img is None:
        print("Error: Could not decode image", file=sys.stderr)
        sys.exit(1)

    height, width = img.shape[:2]

    # ==========================================
    # 核心逻辑：定义需要修复的区域 (Mask)
    # ==========================================
    # 创建一个纯黑色的掩膜图片，大小与原图一致
    mask = np.zeros(img.shape[:2], np.uint8)

    # 【关键演示设定】：假设水印在右下角，宽160，高60的区域
    # 在真实商业项目中，这一步通常由一个 AI 检测模型来自动生成白色区域
    watermark_width = 160
    watermark_height = 60
    
    # 计算右下角的坐标
    start_point = (width - watermark_width, height - watermark_height)
    end_point = (width, height)
    
    # 在 mask 上，把需要去水印的区域画成纯白色 (255)
    # cv2.rectangle(图像, 左上角坐标, 右下角坐标, 颜色(白色), 线宽(-1表示填充))
    cv2.rectangle(mask, start_point, end_point, 255, -1)

    # ==========================================
    # 核心算法：执行修复 (Inpainting)
    # ==========================================
    # 使用 Telea 算法根据 mask 进行修复，半径为 3 像素
    # 这个函数会自动参考白色区域周围的像素，把它填补上
    result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)

    # 4. 保存结果
    cv2.imwrite(output_path, result)
    print("SUCCESS") # 向 Node.js 发送成功信号

if __name__ == "__main__":
    # 接收 Node.js 传来的参数
    # 格式: python3 process.py <输入路径> <输出路径>
    if len(sys.argv) < 3:
        print("Usage: python3 process.py <input_path> <output_path>", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    try:
        remove_watermark(input_file, output_file)
    except Exception as e:
        print(f"Python Error: {str(e)}", file=sys.stderr)
        sys.exit(1)