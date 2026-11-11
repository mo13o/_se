const { defineConfig } = require("@playwright/test");

module.exports = defineConfig({
  testDir: "./tests/e2e",
  fullyParallel: true,
  reporter: [["list"], ["html", { open: "never", outputFolder: "playwright-report" }]],
  use: {
    baseURL: "http://127.0.0.1:4175",
    channel: "chrome",
    headless: true,
    screenshot: "only-on-failure",
    trace: "retain-on-failure"
  },
  webServer: {
    command: "node server.js",
    url: "http://127.0.0.1:4175/api/health",
    env: { PORT: "4175" },
    reuseExistingServer: true,
    timeout: 30000
  }
});
