const { test, expect } = require("@playwright/test");

async function login(page) {
  await page.goto("/");
  await page.locator("#account").fill("S112345678");
  await page.locator("#password").fill("demo1234");
  await page.locator("#captchaInput").fill((await page.locator("#captcha").innerText()).trim());
  await page.getByRole("button", { name: /登入校務系統/ }).click();
}

test("學生可以登入並加選課程", async ({ page }) => {
  await login(page);
  await expect(page.getByRole("heading", { name: "課程查詢" })).toBeVisible();
  await expect(page.locator("#credits")).toHaveText("5");
  const courseRow = page.locator("tr", { hasText: "DMD428" });
  await courseRow.getByRole("button", { name: "加選" }).click();
  await expect(page.locator("#credits")).toHaveText("8");
  await expect(courseRow.getByRole("button", { name: "已選" })).toBeVisible();
});

test("使用者可以搜尋課程", async ({ page }) => {
  await login(page);
  await page.locator("#courseSearch").fill("跨文化");
  await expect(page.locator("#courseRows tr")).toHaveCount(1);
  await expect(page.locator("#courseRows")).toContainText("跨文化溝通");
});
