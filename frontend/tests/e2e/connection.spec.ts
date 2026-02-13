import { test, expect } from "@playwright/test";

/**
 * Test suite for verifying basic WebSocket connection and page functionality
 */
test.describe("WebSocket Connection", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto("/");
  });

  test("should load home page successfully", async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState("networkidle");

    // Expect page title to contain Tank Dynamics
    await expect(page).toHaveTitle(/Tank Dynamics/i);

    // Expect to see Process and Trends tabs
    await expect(page.getByText("Process")).toBeVisible();
    await expect(page.getByText("Trends")).toBeVisible();
  });

  test("should establish WebSocket connection", async ({ page }) => {
    // Wait for connection status to show "Connected"
    const connectionStatus = page.getByText(/connected/i);

    // Playwright will auto-retry until element is visible (default 30s timeout)
    await expect(connectionStatus).toBeVisible({ timeout: 10000 });
  });

  test("should receive real-time data updates", async ({ page }) => {
    // Wait for connection to be established first
    await expect(page.getByText(/connected/i)).toBeVisible({ timeout: 10000 });

    // Navigate to Process tab to see real-time data
    await page.getByRole("button", { name: /process/i }).click();

    // Wait for tank graphic or level display to be visible
    // This ensures the process view has loaded
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();

    // Look for numeric values in the page (tank level, flow rates)
    const levelElements = page.locator("text=/^[0-9.]+\\s*m?$/");

    // Verify we have process data displayed
    await expect(levelElements.first()).toBeVisible({ timeout: 5000 });

    // Count should be > 0, confirming data is present
    const count = await levelElements.count();
    expect(count).toBeGreaterThan(0);
  });
});
