import { test, expect } from "@playwright/test";

/**
 * Test suite for verifying user control interactions
 */
test.describe("Control Commands", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto("/");
    // Wait for connection to be established
    await expect(page.getByText(/connected/i)).toBeVisible({ timeout: 10000 });
  });

  test("should update tank level setpoint", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();

    // Find the setpoint input in the SVG foreignObject
    // Look for an input that might contain a setpoint value
    const inputs = page.locator("input[type='text']");

    // Verify at least one text input exists
    await expect(inputs.first()).toBeVisible({ timeout: 5000 });
    const count = await inputs.count();
    expect(count).toBeGreaterThan(0);

    // Get the first text input (likely setpoint input)
    const setpointInput = inputs.first();

    // Clear and set new value
    await setpointInput.clear();
    await setpointInput.fill("3.5");
    await setpointInput.press("Enter");

    // Verify the input shows the new value
    await expect(setpointInput).toHaveValue("3.5");
  });

  test("should update PID controller gains", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();

    // Look for PID button or popover trigger - search for text containing "PID" or similar
    const pidElements = page.locator("text=/PID|Tuning/i");

    // Verify PID elements exist
    await expect(pidElements.first()).toBeVisible({ timeout: 5000 });
    const pidCount = await pidElements.count();
    expect(pidCount).toBeGreaterThan(0);

    // Click to open PID popover
    await pidElements.first().click();

    // Find number inputs (for Kc, tau_I, tau_D)
    const numberInputs = page.locator("input[type='number']");

    // Wait for inputs to be visible and verify we have at least 2
    await expect(numberInputs.first()).toBeVisible({ timeout: 5000 });
    const inputCount = await numberInputs.count();
    expect(inputCount).toBeGreaterThanOrEqual(2);

    // Update first number input (Kc)
    const kcInput = numberInputs.nth(0);
    await kcInput.clear();
    await kcInput.fill("5.0");

    // Update second number input (tau_I)
    const tauInput = numberInputs.nth(1);
    await tauInput.clear();
    await tauInput.fill("15.0");

    // Verify values persisted
    await expect(kcInput).toHaveValue("5.0");
    await expect(tauInput).toHaveValue("15.0");
  });

  test("should toggle inlet flow mode", async ({ page }) => {
    // Ensure we're on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();

    // Look for Brownian mode option
    const brownianLabel = page.locator("text=/Brownian/i");

    // Verify element exists before proceeding
    await expect(brownianLabel).toBeVisible({ timeout: 5000 });

    // Find the radio button for Brownian mode
    const brownianRadio = brownianLabel.locator("input[type='radio']").first();

    // Get initial state
    const initialChecked = await brownianRadio.isChecked();

    // Click to toggle
    await brownianRadio.click();

    // Verify state changed
    await expect(brownianRadio).toBeChecked({ checked: !initialChecked });

    // Toggle back to manual
    const manualLabel = page.locator("text=/Manual/i");
    await expect(manualLabel).toBeVisible();

    const manualRadio = manualLabel.locator("input[type='radio']").first();
    await manualRadio.click();

    // Verify we're back to initial state
    await expect(manualRadio).toBeChecked({ checked: initialChecked });
  });

  test("should navigate between tabs", async ({ page }) => {
    // Start on Process View (default)
    const processTab = page.getByRole("button", { name: /process/i });
    await expect(processTab).toBeVisible();

    // Click Trends tab
    const trendsTab = page.getByRole("button", { name: /trends/i });
    await trendsTab.click();

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

    // Verify we're back on Process View
    const processHeader = page.getByText(/Process/i).first();
    await expect(processHeader).toBeVisible();

    // Tab switching should be smooth (page should still be responsive)
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});
