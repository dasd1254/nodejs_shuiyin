const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs');
// 【关键新增 1】引入 Node.js 的子进程模块，用于执行外部命令
const { execFile } = require('child_process');

const app = express();
// 端口保持 3001 不变
const PORT = 3001;

app.use(cors());

// 配置静态资源访问
app.use('/result', express.static(path.join(__dirname, 'processed')));

// 确保必要目录存在
const uploadDir = path.join(__dirname, 'uploads');
const processedDir = path.join(__dirname, 'processed');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir, { recursive: true });
if (!fs.existsSync(processedDir)) fs.mkdirSync(processedDir, { recursive: true });

// 配置 Multer 存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => cb(null, uploadDir),
  filename: (req, file, cb) => {
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage: storage });

// ============================
// 核心接口：调用 Python 处理
// ============================
app.post('/remove-watermark', upload.single('file'), (req, res) => {
  console.log("收到上传请求...");
  
  if (!req.file) {
    return res.status(400).json({ code: 400, msg: '没有上传文件' });
  }

  // 1. 准备路径
  const inputPath = req.file.path; // 上传的原图绝对路径
  const outputFilename = `processed_${req.file.filename}`;
  const outputPath = path.join(processedDir, outputFilename); // 准备输出的绝对路径
  const pythonScriptPath = path.join(__dirname, 'process.py'); // Python 脚本路径

  console.log(`准备调用 Python 处理: ${req.file.filename}`);

  // 2. 【核心修改】执行 Python 脚本
  // 相当于在命令行输入: python3 /app/process.py "/app/uploads/xxx.jpg" "/app/processed/yyyy.jpg"
  execFile('python3', [pythonScriptPath, inputPath, outputPath], (error, stdout, stderr) => {
    
    // 清理上传的原图（可选，节省空间）
    // fs.unlinkSync(inputPath);

    if (error) {
      console.error(`Python 执行出错: ${error.message}`);
      console.error(`Python 标准错误输出: ${stderr}`);
      return res.status(500).json({ 
        code: 500, 
        msg: '图像处理服务内部错误',
        detail: stderr || error.message
      });
    }

    // 检查脚本的标准输出
    if (stdout.trim() === 'SUCCESS') {
      console.log("Python 处理成功，准备返回结果");
      const downloadUrl = `/result/${outputFilename}`;
      res.json({
        code: 200,
        msg: '处理成功',
        data: {
          url: downloadUrl
        }
      });
    } else {
       // 脚本虽然执行了，但没有打印 SUCCESS
       console.error(`Python 未知结果: ${stdout}`);
       res.status(500).json({ code: 500, msg: '处理失败，未知响应' });
    }
  });
});

app.listen(PORT, () => {
  console.log(`Node.js 后端运行在端口: ${PORT}`);
});