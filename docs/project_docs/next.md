# Next Tasks - Tank Dynamics Simulator

**Generated:** 2026-02-13  
**Phase:** Phase 7 - Integration and Polish  
**Previous Phases:** Phase 6 (Trends View) ✅ COMPLETE, Phase 6.5 (HMI Redesign) ✅ COMPLETE

---

## Project Status Summary

**Completed Phases:**
- ✅ Phase 1: C++ Simulation Core (42/42 tests passing)
- ✅ Phase 2: Python Bindings (28/28 tests passing)
- ✅ Phase 3: FastAPI Backend (70+ tests passing)
- ✅ Phase 4: Next.js Frontend Foundation (Full implementation)
- ✅ Phase 5: Process View SCADA Interface (Full implementation)
- ✅ Phase 6: Trends View Enhancement (14 tasks complete)
- ✅ Phase 6.5: HMI Redesign (ISA-101 compliant)

**Current Phase:** Phase 7 - Integration and Polish

**System Status:** Production-ready with comprehensive functionality. Phase 7 focuses on quality assurance, testing, documentation, and deployment readiness.

---

## Current Phase: Phase 7 - Integration and Polish

### Overview

Phase 7 completes the proof-of-concept by ensuring all components work together seamlessly, adding production-grade error handling, implementing comprehensive testing, and preparing deployment documentation. This phase transforms a working prototype into a production-ready system.

### Goals

1. **End-to-End Testing:** Playwright test suite verifying complete user workflows
2. **Error Handling:** Comprehensive error boundaries and recovery mechanisms
3. **Loading States:** Professional loading and skeleton screens
4. **Documentation:** Complete operator and deployment guides
5. **Performance:** Profiling and optimization where needed

### Total Tasks: 12 micro-tasks (~5-6 hours total)

---

## Phase 7A: Error Handling and Resilience (4 tasks, ~90 minutes)

These tasks add production-grade error handling and recovery mechanisms to make the system robust under failure conditions.

---

## Task 30a: Add Error Boundary Component

**Phase:** 7A - Error Handling  
**Prerequisites:** Phase 6.5 complete  
**Estimated Time:** 20 minutes  
**Files:** 1 file

### File to Create
- `frontend/components/ErrorBoundary.tsx`

### Context and References

React Error Boundaries catch JavaScript errors in component trees and display fallback UI instead of crashing the entire application. This is critical for production applications.

**Reference:** React Error Boundaries documentation  
**Search:** "React Error Boundary class component"  
**Pattern:** Class component with `componentDidCatch` lifecycle method

### Requirements

Create a reusable ErrorBoundary component that wraps sections of the application and displays a user-friendly error message when child components throw errors.

**Component structure:**
- TypeScript class component extending `React.Component`
- Props type including `children` (ReactNode) and optional `fallback` (ReactNode)
- State type with `hasError` (boolean) and optional `error` (Error object)
- Implement `static getDerivedStateFromError(error)` to update state
- Implement `componentDidCatch(error, errorInfo)` to log error details
- Render method returns children when no error, fallback UI when error caught

**Fallback UI should display:**
- Friendly error title: "Something went wrong"
- Brief explanation: "An unexpected error occurred. Please reload the page."
- Reload button that calls `window.location.reload()`
- Technical details section (collapsed by default) showing error message and stack trace
- Use Tailwind classes for styling: red background for error state, white text, padding

**Error logging:**
- Log to console.error with full error object and component stack
- Include timestamp in log message
- Format: `[ErrorBoundary] Error at ${timestamp}: ${error.message}`

### Verification

Create the component, then test by adding a button that throws an error:

```bash
cd frontend && npm run dev
```

**Test scenario:**
1. Wrap a test component with ErrorBoundary
2. Add button that throws error when clicked
3. Click button - should see fallback UI, not blank page
4. Check console for error log
5. Click reload button - page should refresh

### Escalation Hints

**Escalate to Haiku if:**
- Unfamiliar with React class components (most examples use function components)
- Static methods in TypeScript classes are confusing
- Error boundary lifecycle methods unclear

**Search for these terms if stuck:**
- "React Error Boundary TypeScript example"
- "getDerivedStateFromError vs componentDidCatch"
- "React class component TypeScript"

### Acceptance Criteria
- [ ] ErrorBoundary.tsx file created in components directory
- [ ] Component is a TypeScript class extending React.Component
- [ ] Implements getDerivedStateFromError and componentDidCatch
- [ ] Displays user-friendly fallback UI when error occurs
- [ ] Logs errors to console with timestamp
- [ ] Includes reload button that works
- [ ] TypeScript types defined for props and state

---

## Task 30b: Wrap Application Sections with Error Boundaries

**Phase:** 7A - Error Handling  
**Prerequisites:** Task 30a complete  
**Estimated Time:** 15 minutes  
**Files:** 2 files

### Files to Modify
- `frontend/app/page.tsx`
- `frontend/components/TrendsView.tsx`

### Context and References

Error boundaries should wrap logical sections of the application so that an error in one section doesn't crash the entire page. Wrap charts and the main application independently.

Reference Task 30a for the ErrorBoundary component you just created.

### Requirements

**In page.tsx (main application):**
- Import the ErrorBoundary component
- Wrap the entire main content (after ConnectionStatus) with ErrorBoundary
- Do NOT wrap ConnectionStatus itself (it should always be visible)
- No custom fallback prop needed (use default)

**In TrendsView.tsx (charts section):**
- Import ErrorBoundary
- Wrap each chart component (LevelChart, FlowsChart, ValveChart) individually with ErrorBoundary
- Use custom fallback for chart errors: A simple div with gray background showing "Chart failed to load"
- Pattern: `<ErrorBoundary fallback={<div>Chart error UI</div>}><ChartComponent /></ErrorBoundary>`
- Each chart should fail independently without affecting other charts

**Rationale for separate boundaries:**
- Main app error: Shows full-page error (total failure)
- Individual chart error: Shows chart-specific error (partial failure)
- This provides graceful degradation

### Verification

```bash
cd frontend && npm run dev
```

**Test scenarios:**
1. Normal operation: All charts load normally, no error boundaries visible
2. Simulate chart error: Temporarily modify a chart component to throw error in render
3. Verify only that chart shows error, others continue working
4. Verify ConnectionStatus remains visible even if main content errors

### Escalation Hints

**Escalate to Haiku if:**
- Unclear where to place ErrorBoundary tags in JSX
- Unsure how to create custom fallback components
- Wrapping multiple levels of components is confusing

**Search for these terms if stuck:**
- "React Error Boundary wrapping components"
- "Error boundary custom fallback"

### Acceptance Criteria
- [ ] page.tsx wraps main content with ErrorBoundary
- [ ] ConnectionStatus NOT wrapped (stays visible during errors)
- [ ] TrendsView wraps each chart individually with ErrorBoundary
- [ ] Custom fallback UI implemented for chart errors
- [ ] Charts fail independently without affecting each other
- [ ] No TypeScript errors
- [ ] Application runs without errors in normal operation

---

## Task 30c: Add WebSocket Reconnection Logic with Exponential Backoff

**Phase:** 7A - Error Handling  
**Prerequisites:** Phase 4 complete  
**Estimated Time:** 30 minutes  
**Files:** 1 file

### File to Modify
- `frontend/lib/websocket.ts`

### Context and References

Currently, when the WebSocket connection drops, it may attempt to reconnect immediately and repeatedly, creating a connection storm. Implement exponential backoff to reduce server load during outages.

**Pattern:** Exponential backoff with jitter  
**Search:** "WebSocket reconnection exponential backoff JavaScript"

**Current behavior:** Likely no backoff or fixed delay  
**Desired behavior:** Increasing delay between reconnection attempts

### Requirements

Add exponential backoff logic to the WebSocketClient class reconnection mechanism.

**Add new private fields to WebSocketClient class:**
- `reconnectAttempts` (number): Counter starting at 0
- `maxReconnectDelay` (number): Maximum delay in milliseconds (e.g., 30000 for 30 seconds)
- `baseReconnectDelay` (number): Base delay in milliseconds (e.g., 1000 for 1 second)

**Modify reconnection logic:**
- On disconnect, calculate delay as: `Math.min(baseReconnectDelay * Math.pow(2, reconnectAttempts), maxReconnectDelay)`
- Add random jitter: multiply by random factor between 0.5 and 1.5 to prevent thundering herd
- Formula: `delay * (0.5 + Math.random())`
- Wait for calculated delay before attempting reconnection
- Increment `reconnectAttempts` after each failed attempt
- Reset `reconnectAttempts` to 0 on successful connection

**Example sequence:**
- Attempt 1: 1 second delay
- Attempt 2: 2 second delay
- Attempt 3: 4 second delay
- Attempt 4: 8 second delay
- Attempt 5: 16 second delay
- Attempt 6+: 30 second delay (capped at max)

**Add logging:**
- Log reconnection attempts with current delay: `console.log(\`Reconnecting in ${delay}ms (attempt ${attempts})\`)`
- Log successful reconnection: `console.log('WebSocket reconnected after ${attempts} attempts')`

### Verification

```bash
# Terminal 1: Start backend
cd /home/roger/dev/tank_dynamics
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Start frontend
cd frontend && npm run dev
```

**Test scenario:**
1. Open browser to http://localhost:3000
2. Open browser console to see logs
3. Kill backend process (Ctrl+C in terminal 1)
4. Observe reconnection attempts in console with increasing delays
5. Restart backend: `uvicorn api.main:app --host 0.0.0.0 --port 8000`
6. Observe successful reconnection message
7. Verify delays match exponential pattern (1s, 2s, 4s, etc.)

### Escalation Hints

**Escalate to Haiku if:**
- Unclear how to modify existing WebSocket reconnection code
- setTimeout/clearTimeout with exponential backoff is confusing
- Math.pow for exponential calculation unclear
- Random jitter implementation not working

**Search for these terms if stuck:**
- "JavaScript exponential backoff implementation"
- "WebSocket reconnect with backoff"
- "setTimeout exponential delay pattern"

### Acceptance Criteria
- [ ] Exponential backoff implemented in WebSocketClient
- [ ] Delays follow exponential pattern: 1s, 2s, 4s, 8s, 16s, 30s (capped)
- [ ] Random jitter added to prevent connection storms
- [ ] reconnectAttempts counter resets on successful connection
- [ ] Console logs show reconnection attempts and delays
- [ ] Successfully reconnects after backend restart
- [ ] No TypeScript errors

---

## Task 30d: Add Loading Skeleton for Charts

**Phase:** 7A - Error Handling  
**Prerequisites:** Phase 6 complete  
**Estimated Time:** 25 minutes  
**Files:** 2 files

### Files to Modify
- `frontend/components/TrendsView.tsx`
- `frontend/lib/hooks/useHistory.ts`

### Context and References

Currently when charts load, they may show empty or jump when data arrives. Add skeleton screens to show placeholder UI during loading.

**Reference:** Tailwind CSS skeleton screens (using animate-pulse utility)  
**Search:** "React skeleton screen Tailwind CSS"

### Requirements

**In useHistory.ts hook:**
- Add `loading` boolean to the hook's return value
- Set `loading = true` when fetch starts
- Set `loading = false` when fetch completes (success or error)
- Return type should be: `{ data, loading, error }`

**In TrendsView.tsx:**
- Import the updated useHistory hook
- Destructure `loading` from hook: `const { data, loading, error } = useHistory(...)`
- Create skeleton component inline or as separate component
- Show skeleton when `loading === true`
- Show chart when `loading === false && !error`
- Show error message when `error !== null`

**Skeleton design:**
- Same dimensions as actual chart (width/height match)
- Use Tailwind's `animate-pulse` class for pulsing effect
- Background: gray gradient (e.g., `bg-gradient-to-r from-gray-200 to-gray-300`)
- Rounded corners to match chart container
- Padding to match chart padding

**Pattern:**
```
{loading ? (
  <div className="animate-pulse bg-gray-200 h-64 rounded" />
) : error ? (
  <div className="text-red-500">Error loading chart</div>
) : (
  <ChartComponent data={data} />
)}
```

### Verification

```bash
cd frontend && npm run dev
```

**Test scenario:**
1. Open browser to http://localhost:3000, navigate to Trends tab
2. On page load, should see pulsing skeleton screens briefly
3. Charts should appear after data loads
4. Refresh page (Cmd+R / Ctrl+R) to see skeleton again
5. Verify skeleton has same dimensions as loaded chart
6. Simulate slow network in browser DevTools (throttling) to see skeleton longer

### Escalation Hints

**Escalate to Haiku if:**
- Unclear how to add loading state to custom hooks
- Conditional rendering pattern is confusing
- Tailwind animate-pulse not working as expected

**Search for these terms if stuck:**
- "React loading skeleton screen"
- "Tailwind CSS animate pulse"
- "React conditional rendering loading state"

### Acceptance Criteria
- [ ] useHistory hook returns loading boolean
- [ ] loading state correctly reflects fetch status
- [ ] Skeleton screens display while data is loading
- [ ] Skeleton dimensions match chart dimensions
- [ ] Skeleton uses animate-pulse effect
- [ ] Charts display after loading completes
- [ ] No TypeScript errors
- [ ] Loading → Chart transition is smooth

---

## Phase 7C: End-to-End Testing (3 tasks, ~90 minutes)

Implement Playwright test suite for automated end-to-end testing of user workflows.

---

## Task 32a: Setup Playwright Configuration

**Phase:** 7C - Testing  
**Prerequisites:** Frontend complete  
**Estimated Time:** 15 minutes  
**Files:** 2 files

### Files to Create
- `frontend/playwright.config.ts`
- `frontend/tests/e2e/setup.ts`

### Context and References

Playwright is a modern end-to-end testing framework that automates browser interactions to verify application behavior.

**Reference:** Playwright documentation for Next.js  
**Search:** "Playwright Next.js setup configuration"

**Do NOT use npm to install** - use uv for consistency with project:

```bash
cd frontend
uv add --dev @playwright/test
npx playwright install chromium
```

### Requirements

**Create playwright.config.ts in frontend directory:**
- Import `defineConfig` and `devices` from '@playwright/test'
- Set `testDir` to './tests/e2e'
- Set `fullyParallel` to false (run tests sequentially)
- Set `forbidOnly` to true in CI (prevent .only in committed tests)
- Set `retries` to 1 (retry failed tests once)
- Set `workers` to 1 (single worker for sequential execution)
- Configure reporter: use 'html' for local, 'list' for CI
- Set `use.baseURL` to 'http://localhost:3000'
- Set `use.trace` to 'on-first-retry' (capture trace on failures)
- Configure single project for Chromium browser
- Add webServer configuration:
  - command: 'npm run dev'
  - url: 'http://localhost:3000'
  - reuseExistingServer: true (for local development)
  - timeout: 120000 (2 minutes for startup)

**Create tests/e2e/setup.ts:**
- Export a `beforeAll` function that verifies backend is running
- Make request to http://localhost:8000/api/health
- If health check fails, throw error with message: "Backend not running. Start with: uvicorn api.main:app"
- Add 2 second wait after successful health check (give backend time to stabilize)

**Add to package.json scripts:**
```json
"test:e2e": "playwright test",
"test:e2e:ui": "playwright test --ui",
"test:e2e:debug": "playwright test --debug"
```

### Verification

```bash
# Verify Playwright installed
cd frontend
npx playwright --version

# Run test command (should show "no tests found" - we'll add tests next)
npm run test:e2e
```

**Verify:**
1. Playwright CLI available
2. Config file has no TypeScript errors
3. Running test command doesn't crash (even with no tests)
4. Chromium browser installed (check for downloads in ~/.cache/ms-playwright)

### Escalation Hints

**Escalate to Haiku if:**
- Playwright configuration options are overwhelming
- webServer configuration unclear
- TypeScript types for playwright.config.ts confusing

**Search for these terms if stuck:**
- "Playwright configuration Next.js"
- "Playwright webServer configuration"
- "Playwright TypeScript setup"

### Acceptance Criteria
- [ ] @playwright/test installed via uv
- [ ] Chromium browser installed
- [ ] playwright.config.ts created with correct settings
- [ ] tests/e2e/setup.ts created with health check
- [ ] package.json includes test:e2e scripts
- [ ] No TypeScript errors
- [ ] Running npm run test:e2e works (no crashes)

---

## Task 32b: Write Basic Connection Test

**Phase:** 7C - Testing  
**Prerequisites:** Task 32a complete  
**Estimated Time:** 30 minutes  
**Files:** 1 file

### File to Create
- `frontend/tests/e2e/connection.spec.ts`

### Context and References

Write first Playwright test verifying basic application connectivity and WebSocket connection.

**Reference:** Playwright test writing guide  
**Search:** "Playwright test syntax expect assertions"

### Requirements

Create a test file with a single test suite covering basic connection scenarios.

**Test file structure:**
- Import `test` and `expect` from '@playwright/test'
- Use `test.describe` for test suite: "WebSocket Connection"
- Write 3 test cases (see below)

**Test 1: "should load home page successfully"**
- Navigate to '/' (baseURL configured in playwright.config.ts)
- Wait for page to load
- Expect page title to contain "Tank Dynamics"
- Expect page to have visible element with text "Process" (tab name)
- Expect page to have visible element with text "Trends" (tab name)

**Test 2: "should establish WebSocket connection"**
- Navigate to '/'
- Wait 2 seconds (allow WebSocket to connect)
- Expect connection status indicator to be visible
- Expect status text to contain "Connected" or show green indicator
- Use page.getByTestId if you add data-testid to ConnectionStatus component
- Alternative: use page.getByText or page.locator with appropriate selector

**Test 3: "should receive real-time data updates"**
- Navigate to '/'
- Wait 2 seconds for initial connection
- Get initial tank level value
- Wait 2 seconds for at least one WebSocket update (1 Hz rate)
- Get updated tank level value
- Expect values to be different OR verify time has changed (data is updating)
- This verifies WebSocket is streaming data

**Test helpers:**
- Add `test.beforeEach(async ({ page }) => { ... })` to navigate to home page
- This avoids repeating navigation in each test
- Use `page.waitForTimeout(2000)` for delays (WebSocket connection time)

### Verification

**Start both backend and frontend before running tests:**

```bash
# Terminal 1: Backend
uvicorn api.main:app --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Run tests
cd frontend && npm run test:e2e
```

**Expected output:**
- All 3 tests should pass
- Test execution time: ~10-15 seconds
- No timeout errors
- HTML report generated in playwright-report directory

**View HTML report:**
```bash
npx playwright show-report
```

### Escalation Hints

**Escalate to Haiku if:**
- Playwright selector syntax is confusing
- Async/await in test functions unclear
- Assertions with expect() not working as expected
- Test timeouts occurring

**Search for these terms if stuck:**
- "Playwright selectors getByText getByRole"
- "Playwright expect assertions"
- "Playwright wait for element visible"
- "Playwright async test functions"

### Acceptance Criteria
- [ ] connection.spec.ts file created in tests/e2e
- [ ] Test suite with 3 tests defined
- [ ] Test 1: Page loads with correct title and tabs
- [ ] Test 2: WebSocket connection establishes
- [ ] Test 3: Real-time data updates verified
- [ ] All tests pass when backend/frontend running
- [ ] No timeout errors
- [ ] Test execution time < 30 seconds
- [ ] No TypeScript errors

---

## Task 32c: Write Control Command Test

**Phase:** 7C - Testing  
**Prerequisites:** Task 32b complete  
**Estimated Time:** 45 minutes  
**Files:** 1 file

### File to Create
- `frontend/tests/e2e/controls.spec.ts`

### Context and References

Test user interactions with controls: changing setpoint, adjusting PID parameters, toggling inlet mode.

**Reference:** Playwright user interaction methods  
**Search:** "Playwright fill input click button"

### Requirements

Create test file with test suite covering control interactions.

**Test file structure:**
- Import test and expect from '@playwright/test'
- Test suite: "Control Commands"
- Write 4 test cases (see below)
- Use beforeEach to navigate to home page

**Test 1: "should update tank level setpoint"**
- Navigate to Process View (ensure correct tab selected)
- Find setpoint input field (use data-testid="setpoint-input" if you add it, or appropriate selector)
- Get current setpoint value
- Clear input field: `await page.getByLabel('Setpoint').clear()`
- Fill with new value: 3.5 meters
- Press Enter or click outside to trigger update
- Wait 1 second for WebSocket command
- Verify setpoint displayed updates to 3.5
- Alternative: check WebSocket message sent (advanced)

**Test 2: "should update PID controller gains"**
- Navigate to Process View
- Find PID control panel
- Locate Kc (controller gain) input field
- Change Kc from default (e.g., 2.0) to 5.0
- Locate tau_I (integral time) input field
- Change tau_I from default to 15.0
- Click outside inputs or press Tab to trigger updates
- Wait 1 second
- Verify inputs show new values
- Values should persist (not reset)

**Test 3: "should toggle inlet flow mode"**
- Navigate to Process View
- Find inlet flow mode toggle (Manual/Brownian)
- If currently Manual, click to switch to Brownian
- Wait 500ms for mode change
- Verify toggle state changed (checkbox checked or button active)
- If Brownian mode shows parameters, verify they're visible
- Toggle back to Manual
- Verify parameters hidden again

**Test 4: "should navigate between tabs"**
- Start on Process View (default)
- Click Trends tab
- Wait 500ms for tab switch
- Verify charts are visible
- Expect to see "Level vs Setpoint" chart title
- Click Process tab
- Wait 500ms
- Verify tank graphic is visible
- Tab switching should be smooth (no errors)

**Helper: Add data-testid attributes**
- If selectors are difficult, add data-testid attributes to key controls
- Example: `<input data-testid="setpoint-input" .../>`
- Then use: `page.getByTestId('setpoint-input')`
- Document which components need data-testid added

### Verification

```bash
# Ensure backend and frontend running
# Terminal 1: uvicorn api.main:app --host 0.0.0.0 --port 8000
# Terminal 2: cd frontend && npm run dev

# Terminal 3: Run tests
cd frontend && npm run test:e2e

# Or run in UI mode for debugging
npm run test:e2e:ui
```

**Expected results:**
- All 4 tests pass
- No timeout errors
- Test execution time: ~20-30 seconds
- Controls respond correctly to user actions
- Application remains stable (no crashes)

**If tests fail:**
- Run in debug mode: `npm run test:e2e:debug`
- Check Playwright trace viewer
- Verify backend is responding to commands
- Check browser console for errors

### Escalation Hints

**Escalate to Haiku if:**
- Playwright input interactions (fill, clear, type) not working
- Selector specificity too complex (can't find elements reliably)
- Test timing issues (race conditions, flakiness)
- Assertions for dynamic content failing

**Search for these terms if stuck:**
- "Playwright fill input clear type"
- "Playwright click button checkbox"
- "Playwright wait for element stable"
- "Playwright data-testid best practices"

### Acceptance Criteria
- [ ] controls.spec.ts file created
- [ ] Test 1: Setpoint update works correctly
- [ ] Test 2: PID gains update correctly
- [ ] Test 3: Inlet mode toggle works
- [ ] Test 4: Tab navigation works smoothly
- [ ] All tests pass reliably
- [ ] No flaky tests (consistent pass rate)
- [ ] Test execution time < 45 seconds
- [ ] No TypeScript errors
- [ ] HTML report shows detailed results

---

## Phase 7D: Documentation and Deployment (5 tasks, ~2.5 hours)

Complete operator documentation and deployment guides for production use.

---

## Task 33a: Write Operator Quick Start Guide

**Phase:** 7D - Documentation  
**Prerequisites:** All features complete  
**Estimated Time:** 30 minutes  
**Files:** 1 file

### File to Create
- `docs/OPERATOR_QUICKSTART.md`

### Context and References

Create a concise guide for process operators to start using the tank simulator without needing technical background.

**Audience:** Process operators, not developers  
**Tone:** Clear, simple, jargon-free  
**Format:** Step-by-step with screenshots (placeholders for now)

### Requirements

Create operator guide with the following sections:

**Section 1: Getting Started (What is this?)**
- Brief description: "Tank level control simulator for PID tuning practice"
- Who should use it: Process operators, control engineers, students
- What you can do: Monitor tank level, adjust PID settings, view trends
- System requirements: Web browser (Chrome, Firefox, Safari)

**Section 2: Launching the Application**
- Step-by-step instructions to open application
- Default URL: http://localhost:3000 (or production URL if deployed)
- What you should see: Process View with tank graphic
- Connection status indicator explanation

**Section 3: Understanding the Process View**
- Tank graphic explanation:
  - Blue level indicator shows current tank height
  - Inlet flow (top) brings liquid in
  - Outlet valve (bottom) controls liquid out
  - Numbers show current values
- Control panel:
  - Setpoint: desired tank level
  - PID parameters: controller tuning
  - Inlet flow: manual or automatic disturbances
- Real-time updates: values update once per second

**Section 4: Basic Operations**

**How to change the setpoint:**
1. Locate "Setpoint" input field
2. Click field and enter desired level (0 to 5 meters)
3. Press Enter or click elsewhere
4. Watch tank level move toward new setpoint

**How to adjust PID tuning:**
1. Locate PID control panel
2. Adjust Kc (controller gain): higher = more aggressive
3. Adjust tau_I (integral time): lower = faster setpoint tracking
4. Adjust tau_D (derivative time): usually keep at 0
5. Observe response in tank level

**How to create disturbances:**
1. Find inlet flow control
2. Toggle between Manual and Brownian mode
3. Manual: set constant inlet flow
4. Brownian: random fluctuations test controller

**Section 5: Using the Trends View**
- Click "Trends" tab
- See three charts:
  - Level vs Setpoint: how well controller tracks target
  - Inlet vs Outlet Flow: flow balance
  - Valve Position: controller output over time
- Time range selector: choose how much history to display
- Export button: download data as CSV for Excel

**Section 6: Common Tasks**

**Task: Find good PID settings**
1. Start with Kc=2.0, tau_I=10.0, tau_D=0.0
2. Change setpoint from 2.5m to 3.5m
3. Watch Trends View: does level overshoot? oscillate?
4. Increase Kc if response too slow
5. Decrease Kc if response oscillates
6. Adjust tau_I to fine-tune

**Task: Test controller with disturbances**
1. Enable Brownian inlet mode
2. Watch controller compensate for flow changes
3. Good tuning = level stays near setpoint despite disturbances

**Task: Export data for analysis**
1. Let simulation run for desired time
2. Click "Export CSV" in Trends View
3. Open CSV in Excel or Google Sheets
4. Analyze response characteristics

**Section 7: Troubleshooting**

**Problem: Connection status shows "Disconnected"**
- Solution: Backend server not running. Contact system administrator.

**Problem: Values not updating**
- Solution: Check connection status. Refresh page (F5 or Cmd+R).

**Problem: Control changes don't take effect**
- Solution: Verify you pressed Enter after changing values.

**Problem: Charts not displaying**
- Solution: Wait a few seconds for data to accumulate. Refresh page if needed.

### Verification

After writing the guide:
1. Read through as if you're an operator (not developer)
2. Check for technical jargon - replace with plain language
3. Verify every step is actionable (clear "click this, type that")
4. Ensure screenshots placeholders are marked clearly
5. Test instructions by following them yourself

### Escalation Hints

**Escalate to Haiku if:**
- Unsure what level of detail operators need
- Struggling to explain technical concepts simply
- Guide structure unclear

**Search for these terms if stuck:**
- "Technical writing for non-technical users"
- "Operator manual best practices"

### Acceptance Criteria
- [ ] OPERATOR_QUICKSTART.md created in docs directory
- [ ] All 7 sections included
- [ ] Language is clear and non-technical
- [ ] Step-by-step instructions actionable
- [ ] Common tasks documented
- [ ] Troubleshooting section included
- [ ] Screenshot placeholders marked
- [ ] No technical jargon unexplained
- [ ] File is well-formatted (headings, lists, emphasis)

---

## Task 33b: Write Deployment Guide for Production

**Phase:** 7D - Documentation  
**Prerequisites:** All components complete  
**Estimated Time:** 40 minutes  
**Files:** 1 file

### File to Create
- `docs/DEPLOYMENT.md`

### Context and References

Create comprehensive deployment guide for setting up the tank simulator in production environments.

**Audience:** System administrators, DevOps engineers  
**Tone:** Technical, detailed, complete  
**Format:** Step-by-step with configuration examples

### Requirements

Create deployment guide with these sections:

**Section 1: System Requirements**

**Minimum Requirements:**
- CPU: 2 cores
- RAM: 4GB (2GB for backend, 2GB for frontend)
- Storage: 500MB
- OS: Linux (Ubuntu 22.04+, Arch Linux) or macOS
- Python: 3.10 or higher
- Node.js: 18 or higher

**Recommended for Production:**
- CPU: 4 cores
- RAM: 8GB
- Storage: 1GB (for logs)
- OS: Ubuntu 22.04 LTS (long-term support)

**Section 2: Dependencies Installation**

**Ubuntu 22.04:**
```bash
# System packages
sudo apt update
sudo apt install -y build-essential cmake libeigen3-dev libgsl-dev

# Python uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
```

**Arch Linux:**
```bash
sudo pacman -S base-devel cmake eigen gsl nodejs npm
yay -S uv  # or install from AUR
```

**Section 3: Building the Application**

**Clone repository:**
```bash
git clone https://github.com/yourusername/tank_dynamics.git
cd tank_dynamics
```

**Build C++ core:**
```bash
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --parallel $(nproc)
```

**Install Python package:**
```bash
uv venv
source .venv/bin/activate
uv pip install -e .
```

**Build frontend:**
```bash
cd frontend
npm install
npm run build
```

**Section 4: Production Configuration**

**Backend (FastAPI):**
- Create production config file: `api/config.prod.py`
- Environment variables:
  - `ENVIRONMENT=production`
  - `LOG_LEVEL=INFO`
  - `CORS_ORIGINS=https://yourdomain.com`
- Logging: Configure structured JSON logging
- Error handling: Don't expose stack traces in production

**Frontend (Next.js):**
- Create `.env.production` file:
  - `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`
  - `NEXT_PUBLIC_WS_URL=wss://api.yourdomain.com/ws`
- Build optimization: Enable minification, tree-shaking
- Static asset CDN: Consider serving from CDN for performance

**Section 5: Running in Production**

**Option 1: Systemd Services (Recommended)**

Create `/etc/systemd/system/tank-simulator-backend.service`:
```ini
[Unit]
Description=Tank Simulator Backend
After=network.target

[Service]
Type=simple
User=tanksim
WorkingDirectory=/opt/tank_dynamics
Environment="PATH=/opt/tank_dynamics/.venv/bin"
ExecStart=/opt/tank_dynamics/.venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/tank-simulator-frontend.service`:
```ini
[Unit]
Description=Tank Simulator Frontend
After=network.target

[Service]
Type=simple
User=tanksim
WorkingDirectory=/opt/tank_dynamics/frontend
Environment="PATH=/usr/bin:/bin"
Environment="PORT=3000"
ExecStart=/usr/bin/npm run start
Restart=always

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable tank-simulator-backend tank-simulator-frontend
sudo systemctl start tank-simulator-backend tank-simulator-frontend
```

**Check status:**
```bash
sudo systemctl status tank-simulator-backend
sudo systemctl status tank-simulator-frontend
```

**Option 2: Docker (Alternative)**
- Provide Dockerfile for backend
- Provide Dockerfile for frontend
- Include docker-compose.yml for orchestration
- Document volume mounts for logs

**Section 6: Reverse Proxy Setup (Nginx)**

Example Nginx configuration for production:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

**Section 7: Monitoring and Maintenance**

**Logs:**
- Backend logs: `/var/log/tank-simulator/backend.log`
- Frontend logs: `/var/log/tank-simulator/frontend.log`
- Systemd logs: `journalctl -u tank-simulator-backend -f`

**Health checks:**
- Backend: `curl http://localhost:8000/api/health`
- Frontend: `curl http://localhost:3000`
- Expected: 200 OK responses

**Maintenance tasks:**
- Restart services: `sudo systemctl restart tank-simulator-*`
- View logs: `journalctl -u tank-simulator-backend --since today`
- Update application: Pull latest code, rebuild, restart services

**Section 8: Security Considerations**

- Run services as non-root user (tanksim)
- Use firewall to restrict access (ufw or iptables)
- Enable HTTPS with Let's Encrypt SSL certificates
- Set appropriate CORS origins (don't use "*" in production)
- Regularly update dependencies (npm audit, pip-audit)
- Monitor for unusual activity (failed connections, high CPU)

**Section 9: Backup and Recovery**

**What to backup:**
- Application code: git repository
- Configuration files: .env files, service files
- Logs (if needed for compliance)

**Recovery procedure:**
1. Restore code from git
2. Restore configuration files
3. Rebuild application
4. Restart services
5. Verify health checks pass

**Section 10: Troubleshooting**

**Service won't start:**
- Check logs: `journalctl -u tank-simulator-backend -n 50`
- Verify dependencies installed
- Check file permissions
- Ensure ports not already in use

**High CPU usage:**
- Check number of connected WebSocket clients
- Verify simulation not running too fast (should be 1 Hz)
- Monitor with htop or top

**Connection errors:**
- Verify firewall rules allow ports 8000, 3000
- Check Nginx configuration
- Test WebSocket connection directly: `wscat -c ws://localhost:8000/ws`

### Verification

After writing guide:
1. Test instructions on clean Ubuntu 22.04 system (VM or container)
2. Follow every step exactly as written
3. Verify application starts and runs correctly
4. Document any missing steps or errors encountered
5. Update guide based on testing

### Escalation Hints

**Escalate to Sonnet if:**
- Complex systemd configuration unclear
- Nginx reverse proxy setup difficult
- Docker configuration needed but unfamiliar
- Production security best practices uncertain

**Search for these terms if stuck:**
- "systemd service file Python application"
- "Nginx reverse proxy WebSocket"
- "FastAPI production deployment"
- "Next.js production deployment"

### Acceptance Criteria
- [ ] DEPLOYMENT.md created in docs directory
- [ ] All 10 sections complete
- [ ] System requirements documented
- [ ] Installation steps for Ubuntu and Arch
- [ ] Build instructions complete
- [ ] Systemd service files provided
- [ ] Nginx configuration example included
- [ ] Monitoring and logging documented
- [ ] Security considerations addressed
- [ ] Troubleshooting section included
- [ ] Verified on clean system (if possible)

---

## Task 33c: Create Development Workflow Guide

**Phase:** 7D - Documentation  
**Prerequisites:** None  
**Estimated Time:** 30 minutes  
**Files:** 1 file

### File to Create
- `docs/DEVELOPMENT.md`

### Context and References

Document the development workflow for future contributors or yourself when returning to the project after time away.

**Audience:** Software developers  
**Tone:** Technical, concise, complete  
**Format:** Quick reference with commands

### Requirements

Create development guide with these sections:

**Section 1: Development Environment Setup**

**Prerequisites:**
- CMake 3.20+
- C++17 compiler (GCC 11+ or Clang 14+)
- Python 3.10+
- Node.js 18+
- uv package manager

**Quick setup:**
```bash
# Clone repository
git clone https://github.com/yourusername/tank_dynamics.git
cd tank_dynamics

# Install system dependencies (Ubuntu)
sudo apt install build-essential cmake libeigen3-dev libgsl-dev

# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Section 2: Building Components**

**C++ Core:**
```bash
# Configure with CMake
cmake -B build -DCMAKE_BUILD_TYPE=Debug

# Build
cmake --build build

# Run C++ tests
ctest --test-dir build --output-on-failure
```

**Python Bindings:**
```bash
# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate

# Install in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Run Python tests
uv run pytest -v
```

**Frontend:**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

**Section 3: Running the Full Stack**

**Method 1: Manual (3 terminals)**

Terminal 1 - Backend:
```bash
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Terminal 3 - Access:
```bash
# Open browser to http://localhost:3000
```

**Method 2: Script (recommended)**
```bash
./scripts/dev.sh
```

**Section 4: Testing**

**Run all tests:**
```bash
# C++ tests
ctest --test-dir build --output-on-failure

# Python tests
uv run pytest api/tests/ -v

# Python bindings tests
uv run pytest tests/python/ -v

# Frontend E2E tests (requires backend/frontend running)
cd frontend && npm run test:e2e
```

**Run specific test:**
```bash
# Single C++ test
ctest --test-dir build -R TankModel

# Single Python test file
uv run pytest api/tests/test_api.py -v

# Single E2E test
cd frontend && npx playwright test connection.spec.ts
```

**Section 5: Code Organization**

**Directory structure:**
```
tank_dynamics/
├── src/               # C++ core (Model, PID, Stepper, Simulator)
├── bindings/          # pybind11 Python bindings
├── tests/             # C++ unit tests
├── api/               # FastAPI backend
│   ├── main.py        # Application entry point
│   ├── simulation.py  # Simulation manager
│   └── tests/         # API tests
├── frontend/          # Next.js frontend
│   ├── app/           # Next.js pages (App Router)
│   ├── components/    # React components
│   ├── lib/           # Utilities and hooks
│   └── tests/e2e/     # Playwright tests
└── docs/              # Documentation
```

**Section 6: Development Workflow**

**Making changes:**
1. Create feature branch: `git checkout -b feature/your-feature`
2. Make changes
3. Run relevant tests
4. Commit with descriptive message
5. Push and create pull request

**Testing changes:**
- C++ changes: Run C++ tests + Python binding tests
- Python changes: Run Python tests + API tests
- Frontend changes: Manual testing + E2E tests (if applicable)
- Always test full stack integration for significant changes

**Section 7: Common Development Tasks**

**Add new C++ class:**
1. Create header in `src/your_class.h`
2. Create implementation in `src/your_class.cpp`
3. Add to `src/CMakeLists.txt`
4. Create tests in `tests/test_your_class.cpp`
5. Update bindings in `bindings/bindings.cpp`
6. Add Python tests in `tests/python/test_your_class.py`

**Add new API endpoint:**
1. Define endpoint in `api/main.py`
2. Add Pydantic models if needed in `api/models.py`
3. Update API reference docs
4. Add tests in `api/tests/test_api.py`
5. Update frontend types if needed

**Add new React component:**
1. Create component in `frontend/components/YourComponent.tsx`
2. Define TypeScript types
3. Import and use in appropriate page/component
4. Add E2E test if user-facing feature
5. Test manually in development server

**Section 8: Troubleshooting**

**C++ build fails:**
- Clear build directory: `rm -rf build && cmake -B build`
- Verify dependencies installed: `cmake --version`, `gcc --version`
- Check CMake output for missing libraries

**Python import errors:**
- Verify virtual environment activated: `which python`
- Reinstall package: `uv pip install -e .`
- Check pybind11 module built: `ls .venv/lib/python3.*/site-packages/tank_sim/`

**Frontend not connecting to backend:**
- Verify backend running: `curl http://localhost:8000/api/health`
- Check WebSocket URL in frontend code
- Check CORS configuration in `api/main.py`
- Inspect browser console for errors

**Tests failing unexpectedly:**
- Run tests in isolation: `ctest --test-dir build --output-on-failure`
- Check for race conditions in concurrent tests
- Verify test setup/teardown working correctly
- Clear caches: `rm -rf build` and `rm -rf frontend/.next`

**Section 9: Code Style and Standards**

**C++:**
- Follow Google C++ Style Guide
- Use descriptive variable names
- Add comments for complex logic
- All public methods documented

**Python:**
- Follow PEP 8
- Type hints on all functions
- Docstrings for public APIs
- Use uv for dependency management (never pip directly)

**TypeScript/React:**
- Use functional components with hooks
- Proper TypeScript types (no `any`)
- Descriptive component and variable names
- Extract reusable logic into custom hooks

**Section 10: Resources**

**Documentation:**
- Project Spec: `docs/specs.md`
- Implementation Plan: `docs/plan.md`
- Lessons Learned: `docs/LESSONS_LEARNED.md`
- API Reference: `docs/API_REFERENCE.md`

**External Resources:**
- CMake: https://cmake.org/documentation/
- pybind11: https://pybind11.readthedocs.io/
- FastAPI: https://fastapi.tiangolo.com/
- Next.js: https://nextjs.org/docs
- Playwright: https://playwright.dev/

### Verification

After writing guide:
1. Test all commands work as written
2. Verify directory structure matches actual project
3. Check all file paths are correct
4. Ensure common tasks are actionable
5. Test troubleshooting solutions actually solve problems

### Escalation Hints

**Escalate if:**
- Complex build system explanations needed
- Git workflow unclear
- Code style standards need team discussion

### Acceptance Criteria
- [ ] DEVELOPMENT.md created in docs directory
- [ ] All 10 sections complete
- [ ] Setup instructions clear and tested
- [ ] Build commands verified working
- [ ] Test commands documented
- [ ] Common tasks actionable
- [ ] Troubleshooting covers known issues
- [ ] Code style guidelines included
- [ ] Resource links provided
- [ ] File paths and structure accurate

---

## Task 33d: Update Main README with Phase 7 Completion

**Phase:** 7D - Documentation  
**Prerequisites:** Phase 7 tasks complete  
**Estimated Time:** 20 minutes  
**Files:** 1 file

### File to Modify
- `README.md`

### Context and References

Update the project README to reflect completion of Phase 7 and production readiness.

Current README may be outdated - update status, features, testing, and documentation sections.

### Requirements

**Update these sections in README.md:**

**1. Project Status section:**
- Change status from "In Development" to "Production Ready"
- Update phase completion list:
  - ✅ Phase 1: C++ Core
  - ✅ Phase 2: Python Bindings
  - ✅ Phase 3: FastAPI Backend
  - ✅ Phase 4: Next.js Frontend
  - ✅ Phase 5: Process View
  - ✅ Phase 6: Trends View
  - ✅ Phase 7: Integration and Polish ⭐ NEW
- Add test statistics: "140+ tests passing (42 C++, 28 Python, 70+ API, E2E)"

**2. Features section:**
- Add new features from Phase 7:
  - Error boundaries for graceful failure handling
  - WebSocket reconnection with exponential backoff
  - Loading skeletons for better UX
  - CSV data export functionality
  - Time range selector for trend analysis
  - Comprehensive E2E test suite

**3. Testing section:**
- Add E2E testing information:
  - Playwright test suite
  - Connection tests
  - Control command tests
  - Run command: `cd frontend && npm run test:e2e`
- Update test counts (include E2E tests)

**4. Documentation section:**
- Add links to new docs:
  - Operator Quick Start: `docs/OPERATOR_QUICKSTART.md`
  - Deployment Guide: `docs/DEPLOYMENT.md`
  - Development Workflow: `docs/DEVELOPMENT.md`
- Keep existing doc links (plan, specs, API reference, etc.)

**5. Quick Start section:**
- Simplify to point to detailed guides:
  - For operators: See `docs/OPERATOR_QUICKSTART.md`
  - For developers: See `docs/DEVELOPMENT.md`
  - For deployment: See `docs/DEPLOYMENT.md`
- Keep basic "run the system" commands

**6. Add Production Deployment section (new):**
```markdown
## Production Deployment

This application is production-ready and can be deployed to:
- On-premise servers (Linux/Ubuntu recommended)
- Cloud platforms (AWS, GCP, Azure)
- Docker containers

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed deployment instructions.
```

**7. Update Contributing section (if exists):**
- Reference DEVELOPMENT.md for development workflow
- Keep or add standard contribution guidelines

**Do NOT remove:**
- Architecture overview
- Technology stack
- License information
- Author/contributor information

### Verification

After updating:
1. Read README from top to bottom as if you're a new user
2. Verify all internal links work (point to existing files)
3. Check markdown formatting renders correctly (headers, lists, code blocks)
4. Ensure status accurately reflects project state
5. Confirm no broken links or outdated information

```bash
# Check markdown rendering (if you have markdown preview tool)
# Or just push and view on GitHub

# Verify internal links exist
ls docs/OPERATOR_QUICKSTART.md
ls docs/DEPLOYMENT.md
ls docs/DEVELOPMENT.md
```

### Escalation Hints

**Escalate if:**
- Unsure what level of detail README needs
- Conflicting information between README and other docs
- Markdown formatting complex (tables, nested lists)

### Acceptance Criteria
- [ ] README.md updated
- [ ] Status changed to "Production Ready"
- [ ] Phase 7 marked complete with ⭐ indicator
- [ ] New features listed
- [ ] E2E testing documented
- [ ] New doc links added and working
- [ ] Production deployment section added
- [ ] Test counts updated
- [ ] Markdown renders correctly
- [ ] No broken internal links
- [ ] Information accurate and current

---

## Task 33e: Create Release Checklist

**Phase:** 7D - Documentation  
**Prerequisites:** All Phase 7 tasks complete  
**Estimated Time:** 20 minutes  
**Files:** 1 file

### File to Create
- `docs/RELEASE_CHECKLIST.md`

### Context and References

Create a comprehensive checklist for verifying the system is ready for production release.

**Purpose:** Ensure nothing is forgotten before deploying or sharing the system  
**Format:** Checkbox list organized by category

### Requirements

Create release checklist with these sections:

**Section 1: Code Quality**
```markdown
- [ ] All C++ tests passing (42/42)
- [ ] All Python tests passing (28/28)
- [ ] All API tests passing (70+/70+)
- [ ] All E2E tests passing (6/6)
- [ ] No compiler warnings in Release build
- [ ] No linter errors in Python code
- [ ] No TypeScript errors in frontend
- [ ] No ESLint warnings in frontend
- [ ] Code review completed (if applicable)
```

**Section 2: Functionality**
```markdown
- [ ] WebSocket connection establishes successfully
- [ ] Real-time data updates at 1 Hz
- [ ] Setpoint changes take effect
- [ ] PID parameter updates work correctly
- [ ] Inlet mode toggle (Manual/Brownian) works
- [ ] Charts display data correctly
- [ ] Time range selector filters data
- [ ] CSV export downloads successfully
- [ ] Error boundaries catch and display errors gracefully
- [ ] WebSocket reconnection with exponential backoff works
- [ ] Loading skeletons display during data fetch
```

**Section 3: Documentation**
```markdown
- [ ] README.md updated with current status
- [ ] OPERATOR_QUICKSTART.md complete
- [ ] DEPLOYMENT.md includes all setup steps
- [ ] DEVELOPMENT.md covers development workflow
- [ ] API_REFERENCE.md accurate
- [ ] LESSONS_LEARNED.md updated
- [ ] Code comments updated
- [ ] Docstrings complete for public APIs
```

**Section 4: Performance**
```markdown
- [ ] C++ step time < 2ms (target: ~0.5ms)
- [ ] Python binding overhead < 0.5ms
- [ ] WebSocket latency < 500ms
- [ ] Chart render time < 500ms
- [ ] API response time < 100ms
- [ ] Frontend bundle size < 200KB gzipped
- [ ] No memory leaks over 1 hour run
- [ ] CPU usage reasonable (< 20% on typical hardware)
```

**Section 5: Security**
```markdown
- [ ] CORS configuration set appropriately
- [ ] Input validation on all API endpoints
- [ ] No sensitive data in error messages (production)
- [ ] No debug logs in production build
- [ ] Dependencies up to date (no critical vulnerabilities)
- [ ] HTTPS configuration ready (if deploying)
```

**Section 6: Deployment**
```markdown
- [ ] Build succeeds on clean Ubuntu 22.04 system
- [ ] Build succeeds on clean Arch Linux system
- [ ] Systemd service files tested
- [ ] Nginx configuration tested (if using)
- [ ] Firewall rules documented
- [ ] Backup procedure documented
- [ ] Recovery procedure tested
```

**Section 7: User Experience**
```markdown
- [ ] Application loads without errors
- [ ] UI is responsive (no lag or stuttering)
- [ ] Tab navigation smooth
- [ ] Form inputs work on first try
- [ ] Error messages are user-friendly
- [ ] Loading states provide feedback
- [ ] Connection status indicator visible and accurate
- [ ] Tested on Chrome, Firefox, Safari
- [ ] Tested on desktop and tablet (if applicable)
```

**Section 8: Operational**
```markdown
- [ ] Health check endpoint responds correctly
- [ ] Logs are structured and informative
- [ ] Log rotation configured (production)
- [ ] Monitoring alerts configured (production)
- [ ] Graceful shutdown works correctly
- [ ] Restart recovery works (simulation state resets properly)
```

**Section 9: Version Control**
```markdown
- [ ] All changes committed
- [ ] Commit messages descriptive
- [ ] No uncommitted changes
- [ ] Branch merged to main (if feature branch)
- [ ] Version tag created (e.g., v1.0.0)
- [ ] CHANGELOG.md updated (if exists)
```

**Section 10: Final Verification**
```markdown
- [ ] Run full test suite one final time
- [ ] Manual smoke test of entire application
- [ ] Review all documentation for accuracy
- [ ] Verify all checklist items above completed
- [ ] Sign-off from reviewers (if applicable)
```

**At the bottom, add:**
```markdown
---

## Release Sign-Off

**Version:** 1.0.0  
**Date:** YYYY-MM-DD  
**Released By:** [Name]  
**Reviewed By:** [Name] (if applicable)

**Notes:**
- [Any special notes about this release]
- [Known limitations or issues]
- [Future work planned]

**Deployment Target:**
- [ ] Development
- [ ] Staging
- [ ] Production

**Status:** ✅ Ready for Release | ⏸️ Hold | ❌ Not Ready
```

### Verification

After creating checklist:
1. Go through entire checklist yourself
2. Check every box you can verify
3. Note any items that fail
4. Update docs/code to address failures
5. Recheck until all boxes checked

### Escalation Hints

**Escalate if:**
- Unsure what constitutes "passing" for certain criteria
- Performance benchmarks need verification
- Security items unclear

### Acceptance Criteria
- [ ] RELEASE_CHECKLIST.md created
- [ ] All 10 sections included
- [ ] Checklist items specific and verifiable
- [ ] Sign-off template included at end
- [ ] Markdown formatting correct
- [ ] Items correspond to actual project state
- [ ] Checklist is actionable (clear what to verify)

---

## Summary of Phase 7 Tasks

### Phase 7A: Error Handling (4 tasks, ~90 minutes)
1. Task 30a: Create ErrorBoundary component (20 min)
2. Task 30b: Wrap app sections with error boundaries (15 min)
3. Task 30c: Add WebSocket exponential backoff (30 min)
4. Task 30d: Add loading skeletons for charts (25 min)

### Phase 7C: Testing (3 tasks, ~90 minutes)
5. Task 32a: Setup Playwright configuration (15 min)
6. Task 32b: Write connection test (30 min)
7. Task 32c: Write control command test (45 min)

### Phase 7D: Documentation (5 tasks, ~150 minutes)
8. Task 33a: Operator quick start guide (30 min)
9. Task 33b: Deployment guide (40 min)
10. Task 33c: Development workflow guide (30 min)
11. Task 33d: Update main README (20 min)
12. Task 33e: Create release checklist (20 min)

**Total: 12 tasks, ~330 minutes (~5.5 hours)**

---

## Post-Phase 7: System Complete

After completing Phase 7, the Tank Dynamics Simulator will be:

✅ **Production Ready:**
- Comprehensive error handling and resilience
- Complete end-to-end test coverage
- Professional loading states and UX
- Data export capability for analysis

✅ **Well Documented:**
- Operator quick start guide
- Complete deployment documentation
- Development workflow guide
- Up-to-date README

✅ **Quality Assured:**
- 140+ automated tests passing
- E2E tests verify user workflows
- Performance benchmarked
- Security considerations addressed

✅ **Deployment Ready:**
- Systemd service files
- Nginx configuration examples
- Monitoring and logging setup
- Backup and recovery procedures

---

## Next Steps (Optional Future Work)

### Phase 8: Advanced Features (Future)

See `docs/PHASE4_CONTINUATION_ROADMAP.md` for:
- Configuration save/load
- Process alarms and alerts
- Advanced chart features (zoom, pan)
- Touch-optimized controls
- Theme customization
- Real-time control analysis (Bode plots)

These features are enhancements beyond the proof-of-concept scope. The system is fully functional and production-ready after Phase 7.

---

## Development Workflow Notes

### Git Workflow for Phase 7
```bash
# Create feature branch for each task or small group of tasks
git checkout -b phase7-error-handling    # Tasks 30a-30d
git checkout -b phase7-e2e-tests         # Tasks 32a-32c
git checkout -b phase7-documentation     # Tasks 33a-33e

# After completing each group, merge to main
git checkout main
git merge phase7-error-handling
# ... repeat for each feature branch
```

### Task Execution Best Practices

1. **Read task completely before starting**
2. **Check prerequisites are actually complete**
3. **Follow verification steps exactly**
4. **Commit after each task:** `git commit -m "Task 30a: Add ErrorBoundary component"`
5. **Test integration after related tasks** (e.g., after 30a-30d, test error handling fully)
6. **Update next.md to mark tasks complete**

### When to Escalate

Escalate to Haiku when:
- Stuck for > 15 minutes on implementation detail
- Task requirements unclear after re-reading
- Verification fails repeatedly
- Framework/library pattern unfamiliar

Escalate to Sonnet when:
- Task itself seems incorrect or incomplete
- Requirements conflict with existing code
- Major architectural decision needed

### Testing Strategy

**After each task:**
- Run verification steps in task description
- Check for console errors
- Verify no TypeScript errors
- Test in browser manually

**After each phase section (7A, 7B, etc.):**
- Run full test suite
- Manual smoke test of entire application
- Check all related functionality works together

**After completing all Phase 7:**
- Run RELEASE_CHECKLIST.md
- Full integration test (all features working)
- Performance check (no degradation)
- Documentation review (all docs current)

---

## Key Principles for Phase 7

### 1. Production Quality Focus
Phase 7 is about polish and readiness, not new features. Prioritize:
- Robustness over features
- Documentation over code
- Testing over implementation
- User experience over developer convenience

### 2. Incremental Verification
Every task has verification steps. Follow them precisely:
- Don't skip verification
- If verification fails, fix before next task
- Document any deviations from expected behavior

### 3. Documentation as Code
Documentation is as important as code in Phase 7:
- Write docs as if for someone else
- Test all instructions yourself
- Keep docs updated as you work
- Clear, concise, actionable

### 4. Test-Driven Quality
E2E tests verify the system works end-to-end:
- Tests should pass reliably
- No flaky tests allowed
- If test fails, fix the code or the test (not both)
- Tests document expected behavior

### 5. Operator-Centric Thinking
Remember the end user (operator, not developer):
- Error messages should be friendly
- Loading states prevent confusion
- Export functionality enables offline work
- Documentation helps them succeed

---

**Phase 7 Ready to Begin!**

Start with Task 30a (ErrorBoundary component) and work through sequentially. Each task builds toward a production-ready, well-documented, thoroughly tested system.

**Estimated completion time:** 6-8 hours across all 15 tasks, depending on familiarity with tools and frameworks.
