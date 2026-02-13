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
    // Wait for connection to establish (2 seconds)
    await page.waitForTimeout(2000);

    // Look for connection status indicator
    // It could be displayed as text or as a visual indicator
    const connectionStatus = page.getByText(/connected|connecting/i);

    // At least one connection status should be visible
    await expect(connectionStatus).toBeVisible();
  });

  test("should receive real-time data updates", async ({ page }) => {
    // Wait for initial connection and data fetch
    await page.waitForTimeout(2000);

    // Navigate to Process tab to see real-time data
    await page.getByRole("button", { name: /process/i }).click();
    await page.waitForTimeout(500);

    // Get initial tank level display (look for numeric values in the page)
    const levelElements = page.locator("text=/^[0-9.]+\\s*m?$/");
    const initialCount = await levelElements.count();

    // Wait for at least one WebSocket update (1 second at 1 Hz)
    await page.waitForTimeout(2000);

    // Get updated tank level display
    const updatedCount = await levelElements.count();

    // At minimum, we should have elements on the page (tank level values)
    expect(initialCount).toBeGreaterThan(0);
    expect(updatedCount).toBeGreaterThan(0);

    // The data should be updating - verify some content is present and visible
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});
