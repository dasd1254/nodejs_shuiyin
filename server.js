const express = require('express');
const multer = require('multer');
const cors = require('cors');
const sharp = require('sharp');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3001;

// 1. 允许跨域
app.use(cors());

// 2. 配置静态资源目录，让前端能通过 URL 访问到处理后的图片
// 访问 localhost:3000/result/xxx.png
app.use('/result', express.static(path.join(__dirname, 'processed')));

// 确保文件夹存在
const uploadDir = path.join(__dirname, 'uploads');
const processedDir = path.join(__dirname, 'processed');
if (!fs.existsSync(uploadDir)) fs.mkdirSync(uploadDir);
if (!fs.existsSync(processedDir)) fs.mkdirSync(processedDir);

// 3. 配置上传存储
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, 'uploads/');
  },
  filename: (req, file, cb) => {
    // 保持原有扩展名
    const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
    cb(null, uniqueSuffix + path.extname(file.originalname));
  }
});
const upload = multer({ storage: storage });

// 4. 核心接口：上传并处理
app.post('/remove-watermark', upload.single('file'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).send('没有上传文件');
    }

    const inputPath = req.file.path;
    const outputFilename = `processed_${req.file.filename}`;
    const outputPath = path.join(processedDir, outputFilename);

    // --- 这里是核心处理逻辑 ---
    // 真实场景：这里会调用 AI 模型或者 Python 脚本
    // 演示场景：我们用 Sharp 给图片加个高斯模糊，假装处理了一下，或者仅仅是转换格式
    await sharp(inputPath)
      // .blur(5) // 这里演示处理效果，你可以注释掉
      .toFile(outputPath);

    // 5. 返回图片的访问地址
    // 注意：部署到服务器时，这里要换成服务器 IP
    // 为了灵活性，我们返回相对路径，前端自己拼域名，或者由后端动态获取
    const downloadUrl = `/result/${outputFilename}`;

    res.json({
      code: 200,
      msg: '处理成功',
      data: {
        url: downloadUrl // 前端拿到这个 url 拼上 http://111.231.120.121:3000 即可
      }
    });

  } catch (error) {
    console.error(error);
    res.status(500).send('处理失败');
  }
});

app.listen(PORT, () => {
  console.log(`服务器运行在: http://localhost:${PORT}`);
});