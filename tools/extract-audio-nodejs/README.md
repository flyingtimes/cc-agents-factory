# Extract Audio MCP Server (Node.js)

基于Node.js的MCP服务器，用于从视频文件和URL中提取音频。这是原Windows批处理文件的现代化替代方案。

## 功能特性

- **音频提取**: 从本地视频文件和在线URL提取音频
- **质量控制**: 支持低、中、高三种音频质量设置
- **智能命名**: 使用UUID生成唯一文件名
- **错误处理**: 完善的错误处理和状态反馈
- **多平台支持**: 基于Node.js，支持Windows、macOS和Linux

## 音频质量选项

- **低**: 128kbps @ 44.1kHz
- **中**: 192kbps @ 44.1kHz (默认)
- **高**: 320kbps @ 48kHz

## 安装和设置

### 前置要求

- Node.js 18.0+
- FFmpeg (安装并添加到PATH)
- Claude Code with MCP支持

### 快速开始

```bash
# 进入服务器目录
cd tools/extract-audio-nodejs

# 安装依赖
npm install

# 运行测试
npm test

# 设置Claude Code集成
npm run setup
```

### 手动设置

1. **安装依赖**:
   ```bash
   npm install
   ```

2. **测试服务器**:
   ```bash
   npm test
   ```

3. **配置Claude Code**:
   ```bash
   npm run setup
   ```

## 使用方法

在Claude Code中，你可以使用`extract_audio`工具：

```json
{
  "name": "extract_audio",
  "arguments": {
    "input_path": "path/to/video.mp4",
    "output_name": "my_audio",
    "audio_quality": "high"
  }
}
```

### 参数说明

- **input_path** (必需): 视频文件路径或URL
- **output_name** (可选): 自定义输出文件名（不带扩展名）
- **output_dir** (可选): 输出目录（默认: ../outputs）
- **audio_quality** (可选): low/medium/high（默认: medium）

### 使用示例

```bash
# 提取本地文件音频
extract_audio_tool(input_path='C:/path/to/video.mp4')

# 提取在线视频音频
extract_audio_tool(input_path='https://example.com/video.mp4')

# 高质量音频提取
extract_audio_tool(input_path='video.mp4', audio_quality='high')

# 自定义输出名称
extract_audio_tool(input_path='video.mp4', output_name='my_audio')
```

## 输出格式

音频文件使用UUID命名以确保唯一性：
- 格式: `{name}_{uuid}.mp3`
- 默认位置: `outputs/`
- 示例: `my_audio_550e8400-e29b-41d4-a716-446655440000.mp3`

## 开发信息

### 项目结构

```
tools/extract-audio-nodejs/
├── package.json          # 项目配置和依赖
├── server.js             # MCP服务器主文件
├── setup_claude_integration.js  # Claude Code集成脚本
├── test_server.js        # 测试套件
└── README.md            # 说明文档
```

### 技术栈

- **运行时**: Node.js 18.0+
- **MCP框架**: @modelcontextprotocol/sdk
- **音频处理**: fluent-ffmpeg
- **文件系统**: Node.js fs/promises
- **UUID生成**: uuid

### 开发命令

```bash
# 启动服务器
npm start

# 运行测试
npm test

# 设置Claude Code集成
npm run setup

# 安装依赖
npm install
```

## 故障排除

### 常见问题

1. **FFmpeg未找到**:
   ```bash
   # 检查FFmpeg安装
   ffmpeg -version
   ```

2. **Node.js版本过低**:
   ```bash
   # 检查Node.js版本
   node --version
   ```

3. **MCP工具未出现**:
   - 重启Claude Code
   - 检查`.claude/settings.local.json`配置
   - 运行`npm run setup`重新配置

### 测试和验证

```bash
# 运行完整测试套件
npm test

# 手动测试服务器启动
node server.js

# 验证FFmpeg
ffmpeg -version

# 检查MCP SDK安装
npm list @modelcontextprotocol/sdk
```

## 配置文件

### Claude Code配置

服务器会自动更新`.claude/settings.local.json`文件：

```json
{
  "mcpServers": {
    "extract-audio": {
      "command": "node",
      "args": ["tools/extract-audio-nodejs/server.js"],
      "env": {}
    }
  }
}
```

## 与原批处理文件的比较

| 特性 | 批处理文件 | Node.js MCP服务器 |
|------|-----------|------------------|
| 平台支持 | 仅Windows | 跨平台 |
| 错误处理 | 基础 | 完善 |
| 配置选项 | 有限 | 灵活 |
| 集成方式 | 命令行 | MCP协议 |
| 命名生成 | 时间戳 | UUID |
| 输出格式 | 固定 | 可配置 |

## 许可证

MIT License