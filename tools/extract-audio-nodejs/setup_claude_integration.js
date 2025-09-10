#!/usr/bin/env node

import { spawn } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

// 颜色输出
const colors = {
  reset: "\x1b[0m",
  green: "\x1b[32m",
  yellow: "\x1b[33m",
  red: "\x1b[31m",
  blue: "\x1b[34m",
  bold: "\x1b[1m",
};

function log(message, color = "reset") {
  console.log(`${colors[color]}${message}${colors.reset}`);
}

async function checkDependencies() {
  log("Checking dependencies...", "blue");
  
  // 检查Node.js版本
  const nodeVersion = process.version;
  const majorVersion = parseInt(nodeVersion.slice(1).split(".")[0]);
  if (majorVersion < 18) {
    throw new Error(`Node.js version 18 or higher is required. Current: ${nodeVersion}`);
  }
  log(`✓ Node.js ${nodeVersion}`, "green");
  
  // 检查FFmpeg
  await new Promise((resolve, reject) => {
    const ffmpeg = spawn("ffmpeg", ["-version"]);
    ffmpeg.on("close", (code) => {
      if (code === 0) {
        log("✓ FFmpeg is available", "green");
        resolve();
      } else {
        reject(new Error("FFmpeg is not installed or not in PATH"));
      }
    });
  });
  
  // 检查package.json
  const packagePath = path.join(__dirname, "package.json");
  try {
    await fs.access(packagePath);
    log("✓ package.json found", "green");
  } catch (error) {
    throw new Error("package.json not found");
  }
  
  // 检查server.js
  const serverPath = path.join(__dirname, "server.js");
  try {
    await fs.access(serverPath);
    log("✓ server.js found", "green");
  } catch (error) {
    throw new Error("server.js not found");
  }
}

async function installDependencies() {
  log("Installing Node.js dependencies...", "blue");
  
  return new Promise((resolve, reject) => {
    const npm = spawn("npm", ["install"], { cwd: __dirname });
    
    npm.stdout.on("data", (data) => {
      process.stdout.write(data.toString());
    });
    
    npm.stderr.on("data", (data) => {
      process.stderr.write(data.toString());
    });
    
    npm.on("close", (code) => {
      if (code === 0) {
        log("✓ Dependencies installed successfully", "green");
        resolve();
      } else {
        reject(new Error(`npm install failed with code ${code}`));
      }
    });
  });
}

async function checkClaudeConfig() {
  log("Checking Claude Code configuration...", "blue");
  
  const claudeConfigPath = path.join(__dirname, "..", "..", ".claude", "settings.local.json");
  
  try {
    const configContent = await fs.readFile(claudeConfigPath, "utf8");
    const config = JSON.parse(configContent);
    
    const mcpServers = config.mcpServers || {};
    if (mcpServers["extract-audio"]) {
      log("✓ extract-audio MCP server already configured", "green");
      return true;
    } else {
      log("⚠ extract-audio MCP server not found in configuration", "yellow");
      return false;
    }
  } catch (error) {
    log("⚠ Claude Code configuration not found or invalid", "yellow");
    return false;
  }
}

async function updateClaudeConfig() {
  log("Updating Claude Code configuration...", "blue");
  
  const claudeConfigPath = path.join(__dirname, "..", "..", ".claude", "settings.local.json");
  const claudeDir = path.dirname(claudeConfigPath);
  
  // 确保.claude目录存在
  await fs.mkdir(claudeDir, { recursive: true });
  
  let config = {};
  
  // 读取现有配置
  try {
    const configContent = await fs.readFile(claudeConfigPath, "utf8");
    config = JSON.parse(configContent);
  } catch (error) {
    // 文件不存在或无效，使用空配置
    log("Creating new Claude Code configuration", "yellow");
  }
  
  // 添加extract-audio服务器配置
  config.mcpServers = config.mcpServers || {};
  config.mcpServers["extract-audio"] = {
    command: "node",
    args: [path.join(__dirname, "server.js")],
    env: {}
  };
  
  // 写入配置
  await fs.writeFile(claudeConfigPath, JSON.stringify(config, null, 2));
  log("✓ Claude Code configuration updated", "green");
}

async function testServer() {
  log("Testing MCP server...", "blue");
  
  return new Promise((resolve, reject) => {
    const server = spawn("node", [path.join(__dirname, "server.js")], {
      stdio: ["pipe", "pipe", "pipe"]
    });
    
    let timeout = setTimeout(() => {
      server.kill();
      reject(new Error("Server test timeout"));
    }, 5000);
    
    server.stderr.on("data", (data) => {
      const output = data.toString();
      if (output.includes("Extract Audio MCP server started")) {
        clearTimeout(timeout);
        server.kill();
        log("✓ MCP server test successful", "green");
        resolve();
      }
    });
    
    server.on("close", (code) => {
      clearTimeout(timeout);
      if (code !== null && code !== 0) {
        reject(new Error(`Server test failed with code ${code}`));
      }
    });
  });
}

async function main() {
  try {
    log("=== Extract Audio MCP Server Setup ===", "bold");
    log("");
    
    // 检查依赖
    await checkDependencies();
    log("");
    
    // 安装依赖
    await installDependencies();
    log("");
    
    // 测试服务器
    await testServer();
    log("");
    
    // 检查Claude配置
    const configExists = await checkClaudeConfig();
    log("");
    
    if (!configExists) {
      // 更新Claude配置
      await updateClaudeConfig();
      log("");
    }
    
    log("=== Setup Complete! ===", "bold");
    log("🎉 Extract Audio MCP server has been successfully set up!");
    log("");
    log("Usage in Claude Code:");
    log("  extract_audio_tool(input_path='path/to/video.mp4')");
    log("  extract_audio_tool(input_path='https://example.com/video.mp4', audio_quality='high')");
    log("");
    log("Restart Claude Code to start using the new MCP server.");
    
  } catch (error) {
    log(`❌ Setup failed: ${error.message}`, "red");
    process.exit(1);
  }
}

main();