# 安装指南

## 系统要求

- Python 3.8+
- FFmpeg
- 4GB+ RAM

## 安装步骤

### 1. 克隆或下载项目

```bash
git clone <repository-url>
cd auto-ass-gen
```

### 2. 安装Python依赖

推荐使用虚拟环境：

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3. 安装FFmpeg

#### Windows

1. 从 [FFmpeg官网](https://ffmpeg.org/download.html) 下载
2. 解压到任意目录（如 `C:\ffmpeg`）
3. 将 `C:\ffmpeg\bin` 添加到系统PATH环境变量

验证安装：
```bash
ffmpeg -version
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg

# Arch Linux
sudo pacman -S ffmpeg
```

#### macOS

```bash
brew install ffmpeg
```

## 依赖说明

### 核心依赖

- **torch** (>=1.12.0): PyTorch深度学习框架
- **torchaudio** (>=0.12.0): 音频处理库
- **onnxruntime** (>=1.16.1): ONNX模型运行时（推荐，速度更快）
- **silero-vad** (>=5.0.0): Silero语音活动检测
- **pyyaml** (>=6.0): YAML配置文件支持

### 可选依赖

如果你想使用GPU加速（可选）：

```bash
# CUDA 11.8
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118

# CUDA 12.1
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 验证安装

运行测试脚本：

```bash
python test_modules.py
```

应该看到类似输出：

```
测试结果汇总
============================================================
导入测试        : ✓ 通过
时间转换        : ✓ 通过
配置加载        : ✓ 通过
FFmpeg          : ✓ 通过
ASS写入         : ✓ 通过
VAD处理         : ✓ 通过

总计: 6/6 项测试通过
```

## 常见安装问题

### Q: pip install 失败

**A**: 尝试使用镜像源：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: torch安装很慢

**A**: 使用清华镜像或直接下载wheel文件：

```bash
# 使用清华镜像
pip install torch torchaudio -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### Q: silero-vad安装失败

**A**: 从GitHub直接安装：

```bash
pip install git+https://github.com/snakers4/silero-vad.git
```

### Q: AttributeError: module 'torchaudio' has no attribute 'list_audio_backends'

**A**: 这是torchaudio版本兼容性问题。本项目已经内置了兼容的音频读取函数，无需额外配置。如果仍有问题，请确保安装了最新版本：

```bash
pip install --upgrade torch torchaudio
```

### Q: ImportError: TorchCodec is required for load_with_torchcodec

**A**: 这是新版本torchaudio (2.x+) 的依赖问题。解决方法：

```bash
# 安装soundfile
pip install soundfile

# 如果还有问题，强制重装
pip install soundfile --force-reinstall
```

本项目使用 soundfile 直接读取音频文件，完全绕过 torchaudio 的后端问题。

**验证soundfile安装：**
```bash
python -c "import soundfile; print(soundfile.__version__)"
```

如果显示版本号，说明安装成功。

### Q: onnxruntime安装失败

**A**: 如果ONNX安装有问题，可以暂时不安装，程序会使用PyTorch JIT模型：

```bash
# 编辑 requirements.txt，注释掉 onnxruntime 那行
# 然后重新安装
pip install -r requirements.txt
```

然后在配置文件中设置 `use_onnx: false`。

## 更新依赖

如果需要更新到最新版本：

```bash
pip install --upgrade -r requirements.txt
```

## 卸载

```bash
# 停用虚拟环境
deactivate

# 删除虚拟环境目录
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

## 下一步

安装完成后，请查看 [README.md](README.md) 和 [USAGE.md](USAGE.md) 了解使用方法。

