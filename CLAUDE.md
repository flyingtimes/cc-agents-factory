# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在此代码仓库中工作时提供指导。

## 仓库概述

这是 **cc-agents-factory**，一个专为 Claude Code 设计的专业工具包，具有自定义 MCP (Model Context Protocol) 集成。项目专注于音频提取功能，拥有完整的开发基础设施和多平台支持。

## 技术栈

- **主要语言**: Python 3.8+
- **MCP 框架**: Model Context Protocol 服务器实现
- **音频处理**: FFmpeg 用于音频提取
- **平台**: Windows (支持批处理脚本)
- **依赖项**: MCP 包、pydantic、aiofiles

## 项目结构

```
cc-agents-factory/
├── .claude/
│   ├── agents/
│   │   ├── git.md (中文 git 自动化代理)
│   │   └── video-to-text-converter.md (视频处理代理)
│   └── settings.local.json (MCP 服务器配置)
├── tools/
│   ├── extract-audio-nodejs/ (Node.js 音频提取 MCP 服务器)
│   ├── transcript/ (Python 音频转录 MCP 服务器)
├── assets/
│   └── 1.mp4 (示例视频文件)
├── models/ (统一模型存储目录)
├── outputs/ (统一输出目录)
└── .gitignore (全面的忽略文件)
```

## 目录结构标准化

**重要**: 项目中的所有工具和代理必须遵循以下目录约定：

### 模型存储
- **位置**: 所有模型必须存储在项目根目录的 `models/` 中
- **目的**: 工具使用的所有 AI/ML 模型的集中存储
- **管理**: 工具应根据需要自动创建子目录

### 输出文件
- **位置**: 所有输出文件必须保存到项目根目录的 `outputs/` 中
- **目的**: 所有生成文件（音频、文本、转录等）的集中位置
- **命名**: 使用基于 UUID 的命名确保唯一性：`{name}_{uuid}.extension`

### 工具特定目录
- **工具目录**: 每个工具在 `tools/` 下有自己的子目录
- **本地存储**: 工具可以维护本地的 `models/` 和 `outputs/` 目录用于临时文件
- **最终输出**: 所有最终输出必须移动到项目根目录

## 主要功能

### Audio Extraction MCP Server
- **工具名称**: `extract_audio`
- **位置**: `tools/extract-audio-nodejs/server.js`
- **主要技术**: Node.js + FFmpeg + fluent-ffmpeg
- **实现框架**: 
  - 运行环境：Node.js
  - 音频处理：FFmpeg (通过fluent-ffmpeg包)
  - 服务器：Model Context Protocol (MCP) SDK
  - 文件处理：Node.js fs/promises
  - UUID生成：uuid包
- **输入支持**: 本地视频文件和URL
- **输出格式**: MP3文件，使用UUID命名
- **输出目录**: `outputs/` (项目根目录)
- **质量选项**: 
  - Low: 128kbps @ 44.1kHz
  - Medium: 192kbps @ 44.1kHz (默认)
  - High: 320kbps @ 48kHz
- **核心功能**: 自动输出目录创建、FFmpeg可用性检查、错误处理、进度显示

### Audio Transcription MCP Server
- **工具名称**: `transcribe_audio`
- **位置**: `tools/transcript/server.py`
- **主要技术**: Python + OpenAI Whisper + PyTorch
- **实现框架**: 
  - 运行环境：Python 3.8+
  - 语音识别：OpenAI Whisper (openai-whisper包)
  - 深度学习：PyTorch (GPU/CPU支持)
  - 音频处理：librosa (音频文件加载和预处理)
  - 服务器：Model Context Protocol (MCP) SDK
  - 异步处理：Python asyncio
  - 数据验证：Pydantic
  - 文件操作：aiofiles (异步文件操作)
- **输入支持**: 音频文件 (MP3, WAV, M4A, etc.)
- **输出格式**: 文本文件，使用UUID命名
- **输出目录**: `outputs/` (项目根目录)
- **模型存储**: `models/` (项目根目录)
- **模型选项**: tiny, base, small, medium, large (Whisper模型系列)
- **语言支持**: 自动检测和手动指定
- **核心功能**: 进度跟踪、语言检测、模型缓存、错误处理、异步处理

### Video-to-Text Converter Agent
- **代理名称**: `video-to-text-converter`
- **位置**: `.claude/agents/video-to-text-converter.md`
- **主要技术**: Claude Code Agent Framework + MCP集成
- **实现框架**: 
  - 运行环境：Claude Code Agent Framework
  - 工具集成：MCP工具调用 (extract_audio + transcribe_audio)
  - 任务管理：TodoWrite工具进行任务跟踪
  - 文件操作：Read, Write, Bash等工具
  - 网络处理：WebFetch, WebSearch工具
- **功能**: 完整的视频到文本转录工作流
- **处理流程**: 音频提取 → 语音转录 → 文本输出
- **输出目录**: `outputs/` (项目根目录)
- **集成方式**: 使用extract_audio和transcribe_audio工具的组合
- **核心功能**: 工作流编排、错误处理、进度反馈、文件管理

### 开发基础设施
- **自动化设置**: `setup_claude_integration.py` 用于 MCP 集成
- **测试框架**: `test_server.py` 用于服务器功能验证
- **多平台支持**: 基于 Python 的服务器，支持 Windows 批处理替代方案
- **专业文档**: 全面的 README 文件和使用指南

### 中文语言支持
git 代理 (`.claude/agents/git.md`) 配置为中文响应，为中文开发者提供 git 自动化功能。

## 开发命令

### 安装和设置
```bash
# 安装 Python 依赖项
pip install -r tools/transcript/requirements.txt

# 运行自动化 Claude Code 集成设置
cd tools/transcript
python test_server.py

# 测试 MCP 服务器功能
python -c "import sys; sys.path.append('tools/transcript'); import server"
```

### 测试和验证
```bash
# 运行全面的服务器测试
python tools/transcript/test_server.py

# 测试 MCP 服务器启动
python -c "import sys; sys.path.append('tools/transcript'); import server"

# 验证 FFmpeg 安装
ffmpeg -version

# 检查 MCP 包安装
pip show mcp

# 检查 Whisper 安装
pip show openai-whisper
```

### 开发工作流程
```bash
# 手动启动 MCP 服务器进行测试
python tools/transcript/server.py

# 验证 Claude Code 配置
cat .claude/settings.local.json

# 测试 Node.js 音频提取服务器
node tools/extract-audio-nodejs/server.js
```

### 前置要求
- Python 3.8+
- Node.js 16+
- FFmpeg 已安装并在 PATH 中
- Claude Code 支持 MCP

### 使用方法

#### 音频提取工具
`extract_audio` 工具在 Claude Code 会话中可用：

```json
{
  "name": "extract_audio",
  "arguments": {
    "input_path": "assets/1.mp4",
    "output_name": "my_audio",
    "audio_quality": "high"
  }
}
```

**参数**：
- `input_path` (必需): 视频文件路径或 URL
- `output_name` (可选): 自定义输出文件名
- `output_dir` (可选): 输出目录 (默认: outputs/)
- `audio_quality` (可选): low/medium/high (默认: medium)

#### 音频转录工具
`transcribe_audio` 工具在 Claude Code 会话中可用：

```json
{
  "name": "transcribe_audio",
  "arguments": {
    "input_path": "outputs/my_audio_12345678.mp3",
    "output_name": "my_transcript",
    "model_size": "base",
    "language": "auto"
  }
}
```

**参数**：
- `input_path` (必需): 音频文件路径 (MP3, WAV, M4A, etc.)
- `output_name` (可选): 自定义输出文件名
- `output_dir` (可选): 输出目录 (默认: outputs/)
- `model_size` (可选): tiny/base/small/medium/large (默认: base)
- `language` (可选): 语言代码 (如 'en', 'zh', 'ja', 'auto')

#### 视频转文本转换器代理
使用代理进行完整的视频转文本工作流：

```bash
@agent-video-to-text-converter assets/1.mp4
```

## 配置文件

### Claude Code 设置
- `.claude/settings.local.json`: MCP 服务器配置
- `.mcp.json`: 额外的 MCP 设置
- `.claude/agents/git.md`: 中文 git 自动化代理

### 构建和开发
- **无传统构建过程**: 这是基于 Python 的 MCP 服务器
- **依赖项**: 列在 `tools/transcript/requirements.txt` 中
- **测试**: 使用 `test_server.py` 验证功能（测试 UUID 生成、质量设置、目录创建）
- **集成**: 使用自动化设置（安装 MCP 依赖、测试服务器、检查配置）
- **开发**: 服务器可以手动启动 `python tools/transcript/server.py`

## 重要文件

### MCP 服务器
- `tools/extract-audio-nodejs/server.js`: Node.js 音频提取 MCP 服务器
- `tools/transcript/server.py`: Python 音频转录 MCP 服务器
- `tools/transcript/requirements.txt`: 转录的 Python 依赖项

### 代理
- `.claude/agents/git.md`: 中文 git 自动化代理
- `.claude/agents/video-to-text-converter.md`: 视频转文本转换代理

### 配置
- `.mcp.json`: MCP 服务器配置
- `.claude/settings.local.json`: Claude Code 设置
- `.gitignore`: 所有平台的全面忽略文件

### 目录结构
- `models/`: 统一模型存储目录
- `outputs/`: 统一输出目录
- `assets/`: 示例文件和测试数据

## 输出格式
所有输出文件都使用基于 UUID 的名称保存以确保唯一性：
- **音频文件**: `{name}_{uuid}.mp3` (如 `my_audio_550e8400-e29b-41d4-a716-446655440000.mp3`)
- **转录文件**: `{name}_{uuid}.txt` (如 `my_transcript_550e8400-e29b-41d4-a716-446655440000.txt`)
- **默认位置**: `outputs/` (项目根目录)
- **模型存储**: `models/` (项目根目录)

## 错误处理
服务器包含全面的错误处理：
- FFmpeg 可用性检查
- 输入验证和文件存在性验证
- URL 的网络错误处理
- 权限和路径验证

## 故障排除

如果 MCP 工具没有出现：
1. 重启 Claude Code
2. 检查 FFmpeg 安装：`ffmpeg -version`
3. 验证 MCP 包：`pip show mcp`
4. 检查配置：`.claude/settings.local.json`
5. 检查 Whisper 安装：`pip show openai-whisper`
6. 验证 Node.js 安装：`node --version`

## Claude Code 权限

当前权限允许全面的文件操作、bash 命令和 MCP 服务器集成。项目已完全配置为 Claude Code 开发工作流程。