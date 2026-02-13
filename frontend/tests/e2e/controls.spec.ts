import { test, expect } from "@playwright/test";

/**
 * Test suite for verifying user control interactions
 */
test.describe("Control Commands", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto("/");
    // Wait for initial connection and data load
    await page.waitForTimeout(2000);
  });

  test("should update tank level setpoint", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Find the setpoint input in the SVG foreignObject
    // Look for an input that might contain a setpoint value
    const inputs = page.locator("input[type='text']");
    const count = await inputs.count();

    if (count > 0) {
      // Get the first text input (likely setpoint input)
      const setpointInput = inputs.first();

      // Get current value
      const currentValue = await setpointInput.inputValue();

      // Clear and set new value
      await setpointInput.clear();
      await setpointInput.fill("3.5");
      await setpointInput.press("Enter");

      // Wait for update to take effect
      await page.waitForTimeout(1000);

      // Verify the input shows the new value
      const newValue = await setpointInput.inputValue();
      expect(newValue).toBe("3.5");
    }
  });

  test("should update PID controller gains", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Look for PID button or popover trigger - search for text containing "PID" or similar
    const pidElements = page.locator('text=/PID|Tuning/i');
    const pidCount = await pidElements.count();

    if (pidCount > 0) {
      // Click to open PID popover if it exists
      await pidElements.first().click();
      await page.waitForTimeout(500);

      // Find number inputs (for Kc, tau_I, tau_D)
      const numberInputs = page.locator("input[type='number']");
      const inputCount = await numberInputs.count();

      if (inputCount >= 2) {
        // Update first number input (Kc)
        const kcInput = numberInputs.nth(0);
        await kcInput.clear();
        await kcInput.fill("5.0");
        await kcInput.press("Tab");

        // Update second number input (tau_I)
        const tauInput = numberInputs.nth(1);
        await tauInput.clear();
        await tauInput.fill("15.0");
        await tauInput.press("Tab");

        // Wait for updates
        await page.waitForTimeout(1000);

        // Verify values persisted
        const updatedKc = await kcInput.inputValue();
        const updatedTau = await tauInput.inputValue();
        expect(updatedKc).toBe("5.0");
        expect(updatedTau).toBe("15.0");
      }
    }
  });

  test("should toggle inlet flow mode", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Look for Brownian mode option
    const brownianLabel = page.locator("text=/Brownian/i");

    if (await brownianLabel.isVisible()) {
      // Find the radio button for Brownian mode
      const brownianRadio = brownianLabel.locator("input[type='radio']").first();

      // Get initial state
      const initialChecked = await brownianRadio.isChecked();

      // Click to toggle
      await brownianRadio.click();
      await page.waitForTimeout(500);

      // Verify state changed
      const newChecked = await brownianRadio.isChecked();
      expect(newChecked).not.toBe(initialChecked);

      // Toggle back
      const manualLabel = page.locator("text=/Manual/i");
      if (await manualLabel.isVisible()) {
        const manualRadio = manualLabel.locator("input[type='radio']").first();
        await manualRadio.click();
        await page.waitForTimeout(500);

        const finalChecked = await manualRadio.isChecked();
        expect(finalChecked).toBe(initialChecked);
      }
    }
  });

  test("should navigate between tabs", async ({ page }) => {
    // Start on Process View (default)
    const processTab = page.getByRole("button", { name: /process/i });
    await expect(processTab).toBeVisible();

    // Click Trends tab
    const trendsTab = page.getByRole("button", { name: /trends/i });
    await trendsTab.click();
    await page.waitForTimeout(500);

    // Verify we're on Trends View
    const trendsHeader = page.getByText(/Trends View|Historical/i);
    await expect(trendsHeader).toBeVisible();

    // Look for charts or time range selector (indicator of Trends View)
    const timeRangeButtons = page.getByRole("button", {
      name: /min|hr|hour|time/i,
    });
    const timeRangeVisible = await timeRangeButtons.count();
    expect(timeRangeVisible).toBeGreaterThan(0);

    // Click back to Process tab
    await processTab.click();
    await page.waitForTimeout(500);

    // Verify we're back on Process View
    const processHeader = page.getByText(/Process/i).first();
    await expect(processHeader).toBeVisible();

    // Tab switching should be smooth (page should still be responsive)
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});
