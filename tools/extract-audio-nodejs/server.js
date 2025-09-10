#!/usr/bin/env node

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import ffmpeg from "fluent-ffmpeg";
import { promises as fs } from "fs";
import path from "path";
import { v4 as uuidv4 } from "uuid";

const server = new Server(
  {
    name: "extract-audio-server",
    version: "1.0.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// 音频质量配置
const AUDIO_QUALITY = {
  low: { bitrate: "128k", sampleRate: 44100 },
  medium: { bitrate: "192k", sampleRate: 44100 },
  high: { bitrate: "320k", sampleRate: 48000 },
};

// 工具列表
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: "extract_audio",
        description: "Extract audio from video files or URLs using FFmpeg",
        inputSchema: {
          type: "object",
          properties: {
            input_path: {
              type: "string",
              description: "Path to video file or URL",
            },
            output_name: {
              type: "string",
              description: "Custom output filename (without extension)",
            },
            output_dir: {
              type: "string",
              description: "Output directory (default: ../../outputs)",
            },
            audio_quality: {
              type: "string",
              enum: ["low", "medium", "high"],
              description: "Audio quality (default: medium)",
            },
          },
          required: ["input_path"],
        },
      },
    ],
  };
});

// 清理文件名，移除无效字符
function sanitizeFilename(filename) {
  return filename
    .replace(/[\/\\:*?"<>|]/g, "_")
    .replace(/\s+/g, "_");
}

// 检查FFmpeg是否可用
function checkFFmpeg() {
  return new Promise((resolve, reject) => {
    ffmpeg.getAvailableFormats((err) => {
      if (err) {
        reject(new Error("FFmpeg is not installed or not in PATH"));
      } else {
        resolve(true);
      }
    });
  });
}

// 提取音频函数
async function extractAudio(inputPath, outputName, outputDir, audioQuality) {
  try {
    // 检查FFmpeg
    await checkFFmpeg();

    // 设置默认值
    const quality = AUDIO_QUALITY[audioQuality || "medium"];
    const finalOutputDir = outputDir || path.join(process.cwd(), "outputs");
    const uuid = uuidv4();
    
    // 生成输出文件名
    let finalOutputName;
    if (outputName) {
      finalOutputName = `${sanitizeFilename(outputName)}_${uuid}`;
    } else {
      // 从输入路径提取文件名
      const inputFilename = path.basename(inputPath, path.extname(inputPath));
      finalOutputName = `${sanitizeFilename(inputFilename)}_${uuid}`;
    }
    
    const outputFile = path.join(finalOutputDir, `${finalOutputName}.mp3`);

    // 创建输出目录
    await fs.mkdir(finalOutputDir, { recursive: true });

    // 执行音频提取
    return new Promise((resolve, reject) => {
      const command = ffmpeg(inputPath)
        .noVideo()
        .audioCodec("libmp3lame")
        .audioBitrate(quality.bitrate)
        .audioFrequency(quality.sampleRate)
        .on("start", (commandLine) => {
          console.log(`FFmpeg command: ${commandLine}`);
        })
        .on("progress", (progress) => {
          console.log(`Processing: ${Math.round(progress.percent || 0)}%`);
        })
        .on("end", () => {
          console.log(`Audio extraction completed: ${outputFile}`);
          resolve({
            success: true,
            output_file: outputFile,
            output_name: finalOutputName,
            quality: audioQuality || "medium",
            file_size: null, // 将在后续获取
          });
        })
        .on("error", (err) => {
          console.error(`FFmpeg error: ${err.message}`);
          reject(new Error(`Audio extraction failed: ${err.message}`));
        });

      command.save(outputFile);
    });

  } catch (error) {
    throw new Error(`Audio extraction failed: ${error.message}`);
  }
}

// 工具调用处理
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name === "extract_audio") {
    const { input_path, output_name, output_dir, audio_quality } = args;

    if (!input_path) {
      throw new Error("input_path is required");
    }

    // 验证音频质量
    if (audio_quality && !["low", "medium", "high"].includes(audio_quality)) {
      throw new Error("audio_quality must be one of: low, medium, high");
    }

    try {
      const result = await extractAudio(
        input_path,
        output_name,
        output_dir,
        audio_quality
      );

      // 获取文件大小
      try {
        const stats = await fs.stat(result.output_file);
        result.file_size = stats.size;
      } catch (error) {
        console.warn(`Could not get file size: ${error.message}`);
      }

      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    } catch (error) {
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify({
              success: false,
              error: error.message,
            }, null, 2),
          },
        ],
        isError: true,
      };
    }
  }

  throw new Error(`Unknown tool: ${name}`);
});

// 启动服务器
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  console.error("Extract Audio MCP server started");
}

main().catch((error) => {
  console.error("Server error:", error);
  process.exit(1);
});