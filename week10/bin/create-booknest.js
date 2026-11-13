#!/usr/bin/env node

import { cp, mkdir, readFile, readdir, writeFile } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import process from "node:process";
import { fileURLToPath } from "node:url";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const templateDirectory = path.join(packageRoot, "template");

function showHelp() {
  console.log(`
建立 BookNest Cloudflare Workers + D1 專案

用法：
  npx create-booknest-cloudflare <專案資料夾>

範例：
  npx create-booknest-cloudflare my-bookstore
`);
}

function validateProjectName(name) {
  if (!name) {
    throw new Error("請提供專案資料夾名稱，例如：npx create-booknest-cloudflare my-bookstore");
  }

  if (name === "." || name === ".." || path.isAbsolute(name)) {
    throw new Error("請使用相對資料夾名稱，不可使用絕對路徑或目前資料夾。 ");
  }
}

async function ensureEmptyDirectory(targetDirectory) {
  if (!existsSync(targetDirectory)) {
    await mkdir(targetDirectory, { recursive: true });
    return;
  }

  const entries = await readdir(targetDirectory);
  if (entries.length > 0) {
    throw new Error(`目標資料夾不是空的：${targetDirectory}`);
  }
}

async function updateProjectMetadata(targetDirectory, projectName) {
  const packagePath = path.join(targetDirectory, "package.json");
  const packageJson = JSON.parse(await readFile(packagePath, "utf8"));
  packageJson.name = path.basename(projectName).toLowerCase().replace(/[^a-z0-9-_]/g, "-");
  await writeFile(packagePath, `${JSON.stringify(packageJson, null, 2)}\n`, "utf8");
}

async function main() {
  const argument = process.argv[2];
  if (argument === "--help" || argument === "-h") {
    showHelp();
    return;
  }

  validateProjectName(argument);
  const targetDirectory = path.resolve(process.cwd(), argument);
  await ensureEmptyDirectory(targetDirectory);
  await cp(templateDirectory, targetDirectory, { recursive: true });
  await updateProjectMetadata(targetDirectory, argument);

  console.log(`
✅ BookNest 專案已建立：${targetDirectory}

下一步：
  cd ${argument}
  npm install
  npm run db:migrate:local
  npm run dev

部署前請先建立 Cloudflare D1，並更新 wrangler.jsonc 的 database_id。
`);
}

main().catch((error) => {
  console.error(`\n❌ 建立失敗：${error.message}\n`);
  process.exitCode = 1;
});
