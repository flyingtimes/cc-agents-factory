#!/usr/bin/env node

import { spawn } from "child_process";
import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";
import { v4 as uuidv4 } from "uuid";

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

async function testFFmpeg() {
  log("Testing FFmpeg availability...", "blue");
  
  return new Promise((resolve, reject) => {
    const ffmpeg = spawn("ffmpeg", ["-version"]);
    ffmpeg.on("close", (code) => {
      if (code === 0) {
        log("✓ FFmpeg is working correctly", "green");
        resolve();
      } else {
        reject(new Error("FFmpeg test failed"));
      }
    });
  });
}

async function testUUIDGeneration() {
  log("Testing UUID generation...", "blue");
  
  try {
    const uuid = uuidv4();
    if (uuid && uuid.match(/^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i)) {
      log("✓ UUID generation working", "green");
    } else {
      throw new Error("Invalid UUID generated");
    }
  } catch (error) {
    throw new Error(`UUID generation failed: ${error.message}`);
  }
}

async function testDirectoryCreation() {
  log("Testing directory creation...", "blue");
  
  const testDir = path.join(__dirname, "test_output");
  
  try {
    await fs.mkdir(testDir, { recursive: true });
    await fs.access(testDir);
    log("✓ Directory creation working", "green");
    
    // 清理
    await fs.rmdir(testDir);
  } catch (error) {
    throw new Error(`Directory creation failed: ${error.message}`);
  }
}

async function testServerStartup() {
  log("Testing server startup...", "blue");
  
  return new Promise((resolve, reject) => {
    const server = spawn("node", [path.join(__dirname, "server.js")], {
      stdio: ["pipe", "pipe", "pipe"]
    });
    
    let timeout = setTimeout(() => {
      server.kill();
      reject(new Error("Server startup timeout"));
    }, 3000);
    
    server.stderr.on("data", (data) => {
      const output = data.toString();
      if (output.includes("Extract Audio MCP server started")) {
        clearTimeout(timeout);
        server.kill();
        log("✓ Server startup successful", "green");
        resolve();
      }
    });
    
    server.on("close", (code) => {
      clearTimeout(timeout);
      if (code !== null && code !== 0) {
        reject(new Error(`Server startup failed with code ${code}`));
      }
    });
  });
}

async function testPackageDependencies() {
  log("Testing package dependencies...", "blue");
  
  const packagePath = path.join(__dirname, "package.json");
  
  try {
    const packageContent = await fs.readFile(packagePath, "utf8");
    const packageJson = JSON.parse(packageContent);
    
    const requiredDeps = ["@modelcontextprotocol/sdk", "fluent-ffmpeg", "uuid"];
    const missingDeps = [];
    
    for (const dep of requiredDeps) {
      if (!packageJson.dependencies[dep]) {
        missingDeps.push(dep);
      }
    }
    
    if (missingDeps.length > 0) {
      throw new Error(`Missing dependencies: ${missingDeps.join(", ")}`);
    }
    
    log("✓ All required dependencies are listed in package.json", "green");
  } catch (error) {
    throw new Error(`Package dependency test failed: ${error.message}`);
  }
}

async function testFilePermissions() {
  log("Testing file permissions...", "blue");
  
  const filesToTest = [
    path.join(__dirname, "server.js"),
    path.join(__dirname, "setup_claude_integration.js"),
    path.join(__dirname, "package.json")
  ];
  
  for (const filePath of filesToTest) {
    try {
      await fs.access(filePath, fs.constants.R_OK);
      log(`✓ ${path.basename(filePath)} is readable`, "green");
    } catch (error) {
      throw new Error(`Cannot read ${path.basename(filePath)}: ${error.message}`);
    }
  }
}

async function runComprehensiveTest() {
  log("Running comprehensive tests...", "blue");
  
  const tests = [
    { name: "FFmpeg", fn: testFFmpeg },
    { name: "UUID Generation", fn: testUUIDGeneration },
    { name: "Directory Creation", fn: testDirectoryCreation },
    { name: "Server Startup", fn: testServerStartup },
    { name: "Package Dependencies", fn: testPackageDependencies },
    { name: "File Permissions", fn: testFilePermissions }
  ];
  
  let passed = 0;
  let failed = 0;
  
  for (const test of tests) {
    try {
      await test.fn();
      passed++;
    } catch (error) {
      log(`❌ ${test.name}: ${error.message}`, "red");
      failed++;
    }
  }
  
  log(`\nTest Results: ${passed} passed, ${failed} failed`, failed > 0 ? "red" : "green");
  
  if (failed > 0) {
    throw new Error(`${failed} test(s) failed`);
  }
}

async function main() {
  try {
    log("=== Extract Audio MCP Server Test Suite ===", "bold");
    log("");
    
    await runComprehensiveTest();
    
    log("\n=== All Tests Passed! ===", "bold");
    log("🎉 The MCP server is ready to use!");
    log("");
    log("Next steps:");
    log("1. Run 'npm run setup' to configure Claude Code integration");
    log("2. Restart Claude Code");
    log("3. Use the extract_audio tool in your conversations");
    
  } catch (error) {
    log(`\n❌ Test suite failed: ${error.message}`, "red");
    log("");
    log("Troubleshooting:");
    log("1. Make sure FFmpeg is installed and in PATH");
    log("2. Run 'npm install' to install dependencies");
    log("3. Check file permissions");
    process.exit(1);
  }
}

main();