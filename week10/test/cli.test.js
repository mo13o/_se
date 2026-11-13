import assert from "node:assert/strict";
import { execFile } from "node:child_process";
import { mkdtemp, readFile, rm } from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { promisify } from "node:util";

const execFileAsync = promisify(execFile);
const packageRoot = path.resolve(import.meta.dirname, "..");
const cliPath = path.join(packageRoot, "bin", "create-booknest.js");

test("CLI 能建立可用的 BookNest 專案範本", async () => {
  const temporaryDirectory = await mkdtemp(path.join(os.tmpdir(), "booknest-cli-"));

  try {
    await execFileAsync(process.execPath, [cliPath, "demo-store"], {
      cwd: temporaryDirectory,
    });

    const generatedRoot = path.join(temporaryDirectory, "demo-store");
    const packageJson = JSON.parse(
      await readFile(path.join(generatedRoot, "package.json"), "utf8"),
    );
    const wranglerConfig = await readFile(
      path.join(generatedRoot, "wrangler.jsonc"),
      "utf8",
    );

    assert.equal(packageJson.name, "demo-store");
    assert.equal(packageJson.private, true);
    assert.match(wranglerConfig, /00000000-0000-0000-0000-000000000000/);
    assert.doesNotMatch(wranglerConfig, /b9fba87d-63f0-43d7-b412-bf239b9d1113/);
  } finally {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});

test("CLI 拒絕覆蓋非空資料夾", async () => {
  const temporaryDirectory = await mkdtemp(path.join(os.tmpdir(), "booknest-cli-"));

  try {
    await execFileAsync(process.execPath, ["-e", "require('fs').mkdirSync('used'); require('fs').writeFileSync('used/file.txt', 'keep');"], {
      cwd: temporaryDirectory,
    });

    await assert.rejects(
      execFileAsync(process.execPath, [cliPath, "used"], { cwd: temporaryDirectory }),
      /目標資料夾不是空的/,
    );
  } finally {
    await rm(temporaryDirectory, { recursive: true, force: true });
  }
});
