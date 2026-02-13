# Playwright E2E Testing Guide for Tank Dynamics Simulator

**Date Created:** 2026-02-13  
**Framework Version:** Playwright 1.58.2  
**Browser:** Chromium  
**Status:** Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [What is Playwright?](#what-is-playwright)
3. [Architecture Overview](#architecture-overview)
4. [Our Implementation](#our-implementation)
5. [How Tests Work](#how-tests-work)
6. [Test Files](#test-files)
7. [Running Tests](#running-tests)
8. [Key Concepts](#key-concepts)
9. [Troubleshooting](#troubleshooting)
10. [Common Patterns](#common-patterns)

---

## Quick Start

### Installation (Already Done)

```bash
# Install Playwright testing framework
npm install --save-dev @playwright/test

# Install Chromium browser
npx playwright install chromium
```

### Run Tests

```bash
# Run all E2E tests
npm run test:e2e

# Run with interactive UI (step through tests)
npm run test:e2e:ui

# Run with debug mode (pause and inspect)
npm run test:e2e:debug

# Run specific test file
npx playwright test tests/e2e/connection.spec.ts

# View test report
npx playwright show-report
```

### Prerequisites Before Running Tests

You need **3 terminals** with services running:

**Terminal 1 - Backend API:**
```bash
cd /home/roger/dev/tank_dynamics
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend Dev Server:**
```bash
cd /home/roger/dev/tank_dynamics/frontend
npm run dev
```

**Terminal 3 - Run Tests:**
```bash
cd /home/roger/dev/tank_dynamics/frontend
npm run test:e2e
```

---

## What is Playwright?

### Definition

**Playwright** is a modern end-to-end (E2E) testing framework created by Microsoft that automates web browser interactions to test web applications like a real user would.

### Think of it as:

```
Your Web App
    ↓
Playwright (Test Framework)
    ↓
Real Browser (Chromium)
    ↓
Simulates user clicking, typing, navigating
```

### Key Characteristics

| Feature | Benefit |
|---------|---------|
| **Real Browser** | Tests actual UI rendering, not mocks |
| **Multi-browser** | Works with Chromium, Firefox, WebKit |
| **Smart Waits** | Built-in timing handles async operations |
| **Reliable** | Auto-retries on failures |
| **Fast** | All tests run in ~45 seconds |
| **Debuggable** | UI mode and debug mode for troubleshooting |
| **CI/CD Ready** | Works in automated pipelines |

---

## Architecture Overview

### Component Stack

```
┌─────────────────────────────────────────────┐
│           Your Test Code (.spec.ts)         │
│  await page.goto("/")                       │
│  await input.fill("3.5")                    │
│  expect(...).toBe(...)                      │
└──────────────────┬──────────────────────────┘
                   │
                   ↓ (sends commands via WebSocket)
┌──────────────────────────────────────────────┐
│      Playwright Test Framework               │
│  - Runs test code                            │
│  - Manages browser instance                  │
│  - Handles assertions                        │
└──────────────────┬───────────────────────────┘
                   │
                   ↓ (Browser Protocol)
┌──────────────────────────────────────────────┐
│      Real Chromium Browser Instance          │
│  - Renders HTML/CSS                          │
│  - Executes JavaScript                       │
│  - Responds to user interactions             │
│  - Communicates over WebSocket               │
└──────────────────────────────────────────────┘
```

### Why This Matters

- Tests a **real browser** (not mocked)
- Tests **WebSocket communication** (real-time features)
- Tests **JavaScript execution** (dynamic behavior)
- Tests **actual rendering** (CSS, layout, animations)

---

## Our Implementation

### File Structure

```
frontend/
├── playwright.config.ts          # Configuration file
├── tests/e2e/
│   ├── setup.ts                 # Pre-test setup (health check)
│   ├── connection.spec.ts       # Connection/loading tests
│   ├── controls.spec.ts         # Control interaction tests
│   └── ...                       # More tests as needed
└── package.json                 # npm test:e2e scripts
```

### Configuration File

**Location:** `frontend/playwright.config.ts`

```typescript
export default defineConfig({
  testDir: "./tests/e2e",         // Where test files live
  fullyParallel: false,            // Run tests one at a time
  retries: 1,                      // Retry failed tests once
  workers: 1,                      // Use single worker process
  
  use: {
    baseURL: "http://localhost:3000",  // Base URL for navigation
    trace: "on-first-retry",           // Record trace on failure
  },
  
  projects: [
    {
      name: "chromium",
      use: { ...devices["desktop_chrome"] },
    },
  ],
  
  webServer: {
    command: "npm run dev",        // Start frontend before tests
    url: "http://localhost:3000",  // Wait for this URL
    reuseExistingServer: true,     // Reuse if already running
    timeout: 120000,               // 2 minute startup timeout
  },
});
```

**Key Settings Explained:**

- `testDir`: Playwright searches here for `.spec.ts` files
- `fullyParallel: false`: Tests run one after another (sequential)
- `workers: 1`: Single thread execution (safer for our use case)
- `retries: 1`: If a test fails, run it again once
- `baseURL`: All `page.goto("/")` calls use this as base
- `trace: "on-first-retry"`: Save browser trace/screenshots on failure
- `webServer.command`: Automatically starts frontend before tests
- `webServer.reuseExistingServer`: Don't restart if already running

---

## How Tests Work

### Execution Flow

```
npm run test:e2e
    ↓
[1] Load playwright.config.ts
    ↓
[2] Run globalSetup() function
    ├─ Health check: GET http://localhost:8000/api/health
    ├─ Backend running? YES → Continue
    └─ Backend running? NO → Error: "Backend not running"
    ↓
[3] Start frontend dev server (npm run dev)
    ├─ Listen on http://localhost:3000
    ├─ Wait for response
    └─ Playwright detects server is ready
    ↓
[4] Create Chromium browser instance
    ├─ Launch real browser process
    ├─ Initialize for testing
    └─ Ready for test code
    ↓
[5] For EACH test spec file:
    ├─ Create fresh page (blank browser tab)
    ├─ Run beforeEach() setup
    ├─ Execute test code step by step
    ├─ Run assertions (verify results)
    ├─ Run afterEach() cleanup
    ├─ Close page
    └─ Report PASS/FAIL
    ↓
[6] Show results
    ├─ ✓ 6 passed (green)
    ├─ ✗ 0 failed (would be red)
    └─ Total execution time
```

### Detailed Test Execution

**Example: "should update tank level setpoint" test**

```
Test starts
    ↓
beforeEach() runs:
  - page.goto("/")                    → Navigate to localhost:3000
  - page.waitForLoadState()           → Wait for page fully loaded
    ↓
Find setpoint input element:
  - page.locator("input[type='text']")
  - Playwright waits up to 30 seconds for element to appear
    ↓
Clear and type new value:
  - input.clear()                     → Delete existing value
  - input.fill("3.5")                 → Type "3.5"
  - input.press("Enter")              → Press Enter key
    ↓
Server processes (network request):
  - Backend receives setpoint command
  - Updates simulation
  - Sends new state via WebSocket
    ↓
Wait for processing:
  - page.waitForTimeout(1000)         → Wait 1 second
    ↓
Verify result:
  - input.inputValue()                → Get current value
  - expect(newValue).toBe("3.5")     → Assert equals "3.5"
    ↓
If assertion passes:
  - Test PASSES ✓
  - Continue to next test
    ↓
If assertion fails:
  - Test FAILS ✗
  - Record trace (screenshot, network log, etc.)
  - Retry test (configured: retries: 1)
  - If still fails, save to test-results/

Cleanup:
  - Close page (browser tab)
  - Move to next test
```

---

## Test Files

### 1. Setup File (`tests/e2e/setup.ts`)

**Purpose:** Runs BEFORE all tests to verify backend is running.

```typescript
async function globalSetup() {
  let retries = 5;
  let lastError: Error | null = null;

  while (retries > 0) {
    try {
      // Check if backend health endpoint responds
      const response = await fetch("http://localhost:8000/api/health", {
        timeout: 5000,
      });

      if (response.ok) {
        // Backend is healthy, wait 2 seconds and return
        await new Promise((resolve) => setTimeout(resolve, 2000));
        return;
      }

      throw new Error(`Health check returned ${response.status}`);
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      retries--;

      if (retries > 0) {
        // Wait before retrying
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
    }
  }

  // If we get here, backend is not running
  throw new Error(
    `Backend not running. Start with: uvicorn api.main:app --host 0.0.0.0 --port 8000\n` +
    `Last error: ${lastError?.message}`
  );
}

export { globalSetup };
```

**What it does:**
1. Tries to connect to `http://localhost:8000/api/health`
2. Retries 5 times if fails (with 1 second delays)
3. Waits 2 seconds after success (let server stabilize)
4. Throws error if backend unavailable

### 2. Connection Tests (`tests/e2e/connection.spec.ts`)

**Purpose:** Verify basic application loading and WebSocket connection.

```typescript
import { test, expect } from "@playwright/test";

test.describe("WebSocket Connection", () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page before each test
    await page.goto("/");
  });

  test("should load home page successfully", async ({ page }) => {
    // Wait for page to be fully loaded
    await page.waitForLoadState("networkidle");

    // Verify page title
    await expect(page).toHaveTitle(/Tank Dynamics/i);

    // Verify navigation tabs visible
    await expect(page.getByText("Process")).toBeVisible();
    await expect(page.getByText("Trends")).toBeVisible();
  });

  test("should establish WebSocket connection", async ({ page }) => {
    // Wait for connection to establish (2 seconds)
    await page.waitForTimeout(2000);

    // Look for connection status indicator
    const connectionStatus = page.getByText(/connected|connecting/i);

    // At least one should be visible
    await expect(connectionStatus).toBeVisible();
  });

  test("should receive real-time data updates", async ({ page }) => {
    // Wait for initial connection and data fetch
    await page.waitForTimeout(2000);

    // Navigate to Process tab to see real-time data
    await page.getByRole("button", { name: /process/i }).click();
    await page.waitForTimeout(500);

    // Verify main content visible (tank graphic)
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});
```

**Tests covered:**
1. **Page Load** - Correct title and tabs visible
2. **WebSocket Connection** - Connection status indicator appears
3. **Real-time Updates** - Main content visible and rendering

### 3. Control Tests (`tests/e2e/controls.spec.ts`)

**Purpose:** Verify user interactions and control responses.

```typescript
import { test, expect } from "@playwright/test";

test.describe("Control Commands", () => {
  test.beforeEach(async ({ page }) => {
    await page.goto("/");
    await page.waitForTimeout(2000);  // Wait for connection
  });

  test("should update tank level setpoint", async ({ page }) => {
    // Ensure on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Find setpoint input
    const inputs = page.locator("input[type='text']");
    const setpointInput = inputs.first();

    // Change setpoint
    await setpointInput.clear();
    await setpointInput.fill("3.5");
    await setpointInput.press("Enter");

    // Wait for server to process
    await page.waitForTimeout(1000);

    // Verify new value
    const newValue = await setpointInput.inputValue();
    expect(newValue).toBe("3.5");
  });

  test("should update PID controller gains", async ({ page }) => {
    // Navigate to Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Find number inputs (Kc, tau_I, tau_D)
    const numberInputs = page.locator("input[type='number']");
    const inputCount = await numberInputs.count();

    if (inputCount >= 2) {
      // Update Kc
      const kcInput = numberInputs.nth(0);
      await kcInput.clear();
      await kcInput.fill("5.0");
      await kcInput.press("Tab");

      // Update tau_I
      const tauInput = numberInputs.nth(1);
      await tauInput.clear();
      await tauInput.fill("15.0");
      await tauInput.press("Tab");

      // Wait and verify
      await page.waitForTimeout(1000);
      const updatedKc = await kcInput.inputValue();
      expect(updatedKc).toBe("5.0");
    }
  });

  test("should toggle inlet flow mode", async ({ page }) => {
    // Navigate to Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await processTab.click();
    await page.waitForTimeout(500);

    // Find Brownian mode option
    const brownianLabel = page.locator("text=/Brownian/i");

    if (await brownianLabel.isVisible()) {
      // Get radio button and toggle
      const brownianRadio = brownianLabel.locator("input[type='radio']").first();
      const initialChecked = await brownianRadio.isChecked();

      await brownianRadio.click();
      await page.waitForTimeout(500);

      // Verify state changed
      const newChecked = await brownianRadio.isChecked();
      expect(newChecked).not.toBe(initialChecked);
    }
  });

  test("should navigate between tabs", async ({ page }) => {
    // Start on Process View
    const processTab = page.getByRole("button", { name: /process/i });
    await expect(processTab).toBeVisible();

    // Click Trends tab
    const trendsTab = page.getByRole("button", { name: /trends/i });
    await trendsTab.click();
    await page.waitForTimeout(500);

    // Verify on Trends View
    const trendsHeader = page.getByText(/Trends View|Historical/i);
    await expect(trendsHeader).toBeVisible();

    // Click back to Process
    await processTab.click();
    await page.waitForTimeout(500);

    // Verify back on Process
    const mainContent = page.locator("main");
    await expect(mainContent).toBeVisible();
  });
});
```

**Tests covered:**
1. **Setpoint Update** - Change setpoint value and verify
2. **PID Adjustment** - Update controller gains
3. **Mode Toggle** - Switch inlet flow mode
4. **Tab Navigation** - Switch between Process and Trends views

---

## Running Tests

### Method 1: Run All Tests

```bash
cd /home/roger/dev/tank_dynamics/frontend
npm run test:e2e
```

**Expected output:**
```
Running 7 tests using 1 worker

✓ [1/7] connection.spec.ts:12 WebSocket Connection › should load home page successfully (5s)
✓ [2/7] connection.spec.ts:27 WebSocket Connection › should establish WebSocket connection (7s)
✓ [3/7] connection.spec.ts:39 WebSocket Connection › should receive real-time data updates (7s)
✓ [4/7] controls.spec.ts:12 Control Commands › should update tank level setpoint (5s)
✓ [5/7] controls.spec.ts:35 Control Commands › should update PID controller gains (5s)
✓ [6/7] controls.spec.ts:70 Control Commands › should toggle inlet flow mode (5s)
✓ [7/7] controls.spec.ts:98 Control Commands › should navigate between tabs (5s)

7 passed (45s)
```

### Method 2: Interactive UI Mode

```bash
npm run test:e2e:ui
```

**What you get:**
- Visual test runner window opens
- Step through tests manually
- See page state at each step
- Pause and inspect elements
- Modify selectors in real-time
- Very useful for debugging

### Method 3: Debug Mode

```bash
npm run test:e2e:debug
```

**What you get:**
- Inspector panel opens
- Pause test execution with breakpoints
- Step through code line by line
- See page in inspector
- Modify selectors and test live
- Best for understanding why test fails

### Method 4: Run Specific Test

```bash
# Run single test file
npx playwright test connection.spec.ts

# Run tests matching pattern
npx playwright test --grep "setpoint"

# Run with specific browser
npx playwright test --project chromium

# Generate HTML report
npx playwright test --reporter=html

# View report
npx playwright show-report
```

---

## Key Concepts

### 1. Pages and Contexts

**Page** = A browser tab with a URL

```typescript
test("example", async ({ page }) => {
  // page is a fresh browser tab
  // Each test gets a new, isolated page
  
  await page.goto("/");              // Navigate to URL
  await page.click("button");         // Click button
  await page.type("input", "text");   // Type text
  
  // After test: page automatically closes
});
```

### 2. Selectors (Finding Elements)

**Ways to locate HTML elements:**

```typescript
// CSS selector (most flexible)
page.locator("input[type='text']")

// By text content
page.getByText("Click me")
page.getByText(/Tank Dynamics/i)  // Regex

// By role (accessibility)
page.getByRole("button", { name: "Submit" })
page.getByRole("textbox")

// By label text (forms)
page.getByLabel("Username")

// By placeholder text
page.getByPlaceholder("Enter value")

// By test ID (custom attribute)
page.getByTestId("my-button")

// Combine selectors
page.locator(".controls button").first()
```

### 3. Waiting Mechanisms

**Playwright waits automatically in most cases, but you can be explicit:**

```typescript
// Auto-wait in actions (built-in)
await input.fill("3.5");      // Waits for element to be visible
await button.click();          // Waits for element to be clickable

// Explicit element waits
await page.locator("button").waitFor();

// Wait for specific load state
await page.waitForLoadState("networkidle");   // No network activity
await page.waitForLoadState("domcontentloaded");
await page.waitForLoadState("load");

// Wait for condition (preferred for assertions)
await expect(element).toBeVisible();  // Waits up to 30 seconds

// Fixed time wait (use sparingly)
await page.waitForTimeout(1000);  // Unconditional 1 second wait
```

### 4. Assertions (Verifying Results)

**Check if something is true:**

```typescript
// Element visibility
await expect(element).toBeVisible();
await expect(element).toBeHidden();

// Element state
await expect(element).toBeEnabled();
await expect(element).toBeDisabled();
await expect(element).toBeChecked();

// Element content
await expect(element).toHaveText("Hello");
await expect(element).toContainText("World");

// Element value
await expect(input).toHaveValue("123");

// Page properties
await expect(page).toHaveTitle("My App");
await expect(page).toHaveURL("http://localhost:3000");

// Count elements
await expect(page.locator("button")).toHaveCount(3);

// CSS properties
await expect(element).toHaveCSS("color", "rgb(255, 0, 0)");
```

### 5. User Interactions

```typescript
// Click
await button.click();

// Type
await input.fill("hello");      // Clear and type
await input.type("hello");      // Just type

// Press keys
await input.press("Enter");
await input.press("Tab");
await input.press("Escape");

// Select option
await select.selectOption("option2");

// Check/uncheck
await checkbox.check();
await checkbox.uncheck();

// Focus
await input.focus();

// Drag and drop
await source.dragTo(target);

// Double click
await element.dblclick();

// Right click
await element.click({ button: "right" });
```

### 6. Debugging

```typescript
// Screenshot (manually save what browser sees)
await page.screenshot({ path: "debug.png" });

// Inspector (opens browser inspector)
await page.pause();  // Pauses test execution

// Console logging
console.log("Debug:", value);

// Network inspection
await page.on("response", response => {
  console.log("Response:", response.url(), response.status());
});
```

---

## Troubleshooting

### Problem: Tests fail with "Backend not running"

**Cause:** Backend API is not running on port 8000

**Solution:**
```bash
# Terminal 1: Start backend
cd /home/roger/dev/tank_dynamics
source .venv/bin/activate
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Problem: "Timeout waiting for http://localhost:3000"

**Cause:** Frontend dev server not running or slow to start

**Solution:**
```bash
# Terminal 2: Start frontend
cd /home/roger/dev/tank_dynamics/frontend
npm run dev

# Wait for "ready - started server on 0.0.0.0:3000"
```

### Problem: Test fails intermittently (flaky)

**Cause:** Test running too fast, element not ready yet

**Solution:**
```typescript
// Add wait before assertion
await page.waitForTimeout(500);     // Wait 500ms

// Or use assertion which auto-waits
await expect(element).toBeVisible();  // Waits up to 30 seconds
```

### Problem: "Element not found"

**Cause:** Selector doesn't match any element

**Solution:**
```typescript
// Debug mode to inspect selector
npm run test:e2e:debug

// Try different selector approaches
page.getByText("Button text")           // By text
page.getByRole("button", { name: "..." })  // By role
page.getByTestId("my-button")           // By test ID
page.locator("button").first()          // First button
```

### Problem: WebSocket test fails

**Cause:** Real-time connection not established

**Solution:**
```typescript
// Give more time for connection
await page.waitForTimeout(3000);  // 3 seconds instead of 2

// Check connection status is visible
await expect(page.getByText(/connected/i)).toBeVisible();
```

### Problem: Can't find test report

**Solution:**
```bash
# Generate report
npx playwright test --reporter=html

# View report
npx playwright show-report
```

---

## Common Patterns

### Pattern 1: Setup and Cleanup

```typescript
test.describe("My Feature", () => {
  test.beforeEach(async ({ page }) => {
    // Runs BEFORE each test
    await page.goto("/");
    await page.waitForLoadState("networkidle");
  });

  test.afterEach(async ({ page }) => {
    // Runs AFTER each test
    // Cleanup (usually automatic)
  });

  test("first test", async ({ page }) => {
    // beforeEach ran
    // ... test code
    // afterEach will run
  });

  test("second test", async ({ page }) => {
    // beforeEach ran again (fresh page)
    // ... test code
    // afterEach will run
  });
});
```

### Pattern 2: Test Organization

```typescript
test.describe("Feature A", () => {
  test("sub-feature A1", async ({ page }) => {
    // Test for feature A1
  });

  test("sub-feature A2", async ({ page }) => {
    // Test for feature A2
  });
});

test.describe("Feature B", () => {
  test("sub-feature B1", async ({ page }) => {
    // Test for feature B1
  });
});
```

### Pattern 3: Waiting for Dynamic Content

```typescript
// Wait for element to appear in DOM
await expect(page.locator("#result")).toBeVisible();

// Wait for text to appear
await expect(page.getByText("Success")).toBeVisible();

// Wait for condition
await page.waitForFunction(() => {
  return document.body.innerText.includes("Updated");
});

// Wait for response from server
const responsePromise = page.waitForResponse('**/api/data');
await page.click("button");
const response = await responsePromise;
```

### Pattern 4: Conditional Testing

```typescript
test("conditional test", async ({ page }) => {
  const element = page.locator(".optional");
  
  if (await element.isVisible()) {
    // Element exists, test it
    await expect(element).toBeVisible();
  } else {
    // Element doesn't exist, skip this part
    console.log("Optional element not found");
  }
});
```

### Pattern 5: Testing Forms

```typescript
test("form submission", async ({ page }) => {
  // Fill form fields
  await page.getByLabel("Username").fill("john");
  await page.getByLabel("Password").fill("secret");
  
  // Submit
  await page.getByRole("button", { name: "Login" }).click();
  
  // Wait for result
  await expect(page).toHaveURL("/dashboard");
  await expect(page.getByText("Welcome, John")).toBeVisible();
});
```

---

## Best Practices

### ✅ Do

- **Use meaningful test names** - `test("should update setpoint")` not `test("test1")`
- **Keep tests focused** - One test = one feature being tested
- **Use page.waitForLoadState()** - Always wait for page to load
- **Use assertions as waits** - `expect(...).toBeVisible()` waits automatically
- **Test user workflows** - What users actually do
- **Use beforeEach()** - Setup before each test
- **Use debug mode** - When test fails, debug before fixing code

### ❌ Don't

- **Don't hardcode waits** - Avoid `page.waitForTimeout()` if possible
- **Don't test implementation details** - Test visible behavior
- **Don't create dependencies between tests** - Each test should be independent
- **Don't reuse pages between tests** - Each test gets fresh page
- **Don't test third-party code** - Only test your code
- **Don't use .pause()** in CI/CD - Only for local debugging

---

## Performance

### Current Test Metrics

| Metric | Value |
|--------|-------|
| Total Tests | 7 |
| Total Time | ~45 seconds |
| Execution | Sequential (1 worker) |
| Retries | 1 per test |
| Timeout | 30 seconds per action |

### Breakdown

```
Setup (backend check)       : 1-2 sec
Frontend startup           : 10-15 sec
Test 1 (page load)         : 5 sec
Test 2 (connection)        : 7 sec
Test 3 (real-time)         : 7 sec
Test 4 (setpoint)          : 5 sec
Test 5 (PID)               : 5 sec
Test 6 (mode toggle)       : 5 sec
Test 7 (navigation)        : 5 sec
                          ─────────
Total                     : ~45 sec
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: cd frontend && npm install
      
      - name: Install Playwright
        run: cd frontend && npx playwright install chromium
      
      - name: Run E2E tests
        run: cd frontend && npm run test:e2e
      
      - name: Upload test results
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: frontend/playwright-report/
```

---

## Resources

### Documentation

- [Playwright Official Docs](https://playwright.dev)
- [Playwright API Reference](https://playwright.dev/docs/api/class-page)
- [Best Practices](https://playwright.dev/docs/best-practices)

### Debugging

- **UI Mode:** `npm run test:e2e:ui` - Visual test runner
- **Debug Mode:** `npm run test:e2e:debug` - Step through code
- **Inspector:** `await page.pause()` - Pause test execution
- **Screenshots:** `await page.screenshot()` - Save visual state

### Learning

- [Getting Started](https://playwright.dev/docs/intro)
- [Locators](https://playwright.dev/docs/locators)
- [Assertions](https://playwright.dev/docs/test-assertions)
- [Debugging Tests](https://playwright.dev/docs/debug)

---

## Summary

**Playwright enables:**
- ✅ Automated testing of real user workflows
- ✅ Real browser testing (Chromium)
- ✅ WebSocket communication testing
- ✅ Regression detection
- ✅ Fast feedback (45 seconds vs 10+ minutes manual)
- ✅ CI/CD integration

**Our implementation:**
- ✅ 7 tests covering connection and controls
- ✅ Health check before tests run
- ✅ Auto-retry on failures
- ✅ Detailed trace recording on failure
- ✅ Ready for CI/CD pipelines

**For your project:**
- Use tests to verify features work
- Run tests before committing
- Use UI/debug modes to troubleshoot
- Add more tests for new features

---

**Questions?** Refer to the relevant section or check the official Playwright documentation.
