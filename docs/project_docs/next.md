# Next Tasks - Tank Dynamics Simulator

## Current Phase: Phase 4 - Next.js Frontend (Initial Setup)

**Phase Status:** Starting Phase 4
**Branch:** phase4-initial

**Context:** Phases 1-3 are complete with all tests passing. The C++ simulation core, Python bindings, and FastAPI backend are fully operational with comprehensive test coverage. Phase 3 delivered a production-ready API with WebSocket real-time updates at 1 Hz, REST endpoints, Brownian inlet flow mode, and complete documentation.

**Phase 4 Goals:** Build a modern SCADA-style web interface using Next.js 14 with App Router, Tailwind CSS, and Recharts. The interface will provide real-time process visualization, control inputs, and historical trend plotting.

---

## Task 19: Next.js Project Initialization and Basic Structure

**Phase:** 4 - Next.js Frontend
**Prerequisites:** Phase 3 complete (FastAPI backend operational)

### Files to Create

Create a new Next.js project in the `frontend/` directory:

```
frontend/
├── package.json
├── tsconfig.json
├── next.config.js
├── tailwind.config.js
├── postcss.config.js
├── app/
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   └── providers.tsx
├── components/
│   └── ui/
│       └── (shadcn/ui components will go here)
├── hooks/
│   └── useWebSocket.ts
├── lib/
│   ├── utils.ts
│   └── types.ts
└── public/
    └── (static assets)
```

### Requirements

#### Project Initialization

Initialize a new Next.js 14 project with TypeScript support in the frontend directory. Use the App Router (not Pages Router). The project should be configured with modern tooling and best practices.

The initialization should:
- Use Next.js 14 or later with App Router
- Enable TypeScript with strict mode
- Configure ESLint for code quality
- Set up the `src/` directory structure is optional (we'll use the app directory at root level)

#### Package Dependencies

Install and configure these core dependencies:

**Framework and Build Tools:**
- next (version 14.x or later)
- react (version 18.x)
- react-dom (version 18.x)
- typescript (version 5.x)

**Styling:**
- tailwindcss (version 3.x)
- postcss
- autoprefixer
- @tailwindcss/forms (for better form styling)

**Charting Library:**
- recharts (version 2.x) for time-series plotting

**WebSocket and Data:**
- No additional WebSocket library needed (use native WebSocket API)

**Development Dependencies:**
- @types/node
- @types/react
- @types/react-dom
- eslint
- eslint-config-next

#### Tailwind CSS Configuration

Configure Tailwind CSS to support the SCADA-style dark theme that will be the primary interface theme. The configuration file should:

- Extend the default theme with custom colors for process states (normal, warning, alarm)
- Define custom colors for tank visualization (liquid, empty space, borders)
- Include spacing values appropriate for industrial UI layouts
- Support dark mode as the default theme
- Configure content paths to scan all TypeScript and TSX files in app and components directories

Custom color palette should include:
- Process normal state (green tones)
- Process warning state (yellow/amber tones)
- Process alarm state (red tones)
- Tank liquid color (blue tones)
- Background colors (dark grays for SCADA aesthetic)
- Text colors (light grays and white for readability on dark)
- Border and separator colors (medium grays)

#### TypeScript Configuration

Configure TypeScript with strict mode enabled for type safety. The configuration should:
- Enable strict type checking
- Set module resolution to bundler
- Configure path aliases (e.g., @/components, @/lib, @/hooks)
- Enable JSX support with React 18
- Include appropriate lib files for DOM and ES2022 features
- Set target to ES2022 or later

#### Root Layout (app/layout.tsx)

Create the root layout component that wraps all pages. This layout should:
- Define the HTML structure with proper doctype and lang attribute
- Include metadata for the application title and description
- Set up the dark theme as default using Tailwind dark mode classes
- Apply base font styles (system font stack or custom font)
- Include any global providers that will be needed
- Set viewport configuration for responsive design

The layout should establish the visual foundation of the SCADA interface with dark backgrounds and appropriate text contrast.

#### Home Page (app/page.tsx)

Create the main page component that will serve as the container for the simulation interface. For now, this should be a placeholder that:
- Displays the application title "Tank Dynamics Simulator"
- Shows a subtitle describing it as a "Real-time SCADA Interface"
- Includes a simple connection status indicator (placeholder)
- Uses Tailwind classes to demonstrate the dark theme is working
- Applies proper spacing and typography for an industrial interface look

The actual tab navigation and views will be added in subsequent tasks.

#### Global Styles (app/globals.css)

Create the global stylesheet that imports Tailwind and defines any custom CSS. This should:
- Import Tailwind base, components, and utilities layers
- Define CSS custom properties for colors if needed
- Include any base element styling (scrollbars, focus rings, etc.)
- Set smooth scrolling behavior
- Define any animation keyframes needed for process indicators

Consider SCADA interface conventions:
- Low visual noise
- High contrast for readability
- Clear focus indicators for keyboard navigation
- Smooth but not distracting animations

#### Type Definitions (lib/types.ts)

Create TypeScript interfaces that mirror the API data structures. These types should match the Pydantic models from the FastAPI backend to ensure type safety across the stack.

Define interfaces for:

**SimulationState:** The complete state snapshot sent via WebSocket every second, containing:
- time (number in seconds)
- level (current tank level in meters)
- setpoint (target level in meters)
- error (difference between setpoint and level)
- inlet_flow (current inlet flow rate in m³/s)
- outlet_flow (current outlet flow rate in m³/s)
- valve_position (current valve opening fraction, 0 to 1)
- inlet_mode (string: "constant" or "brownian")
- inlet_config (object with min, max, variance if brownian mode)

**ConfigResponse:** The simulation configuration returned by GET /api/config, containing:
- tank_height (maximum tank height in meters)
- tank_area (cross-sectional area in m²)
- valve_coefficient (k_v value)
- initial_level (starting level)
- initial_setpoint (starting setpoint)
- pid_gains (object with Kc, tau_I, tau_D)
- timestep (simulation dt)
- history_capacity (maximum history size)
- history_size (current history entries)

**HistoryPoint:** A single historical data point, same structure as SimulationState

**WebSocketMessage:** Union type for messages sent from client to server:
- type: "setpoint" | "pid" | "inlet_flow" | "inlet_mode"
- plus type-specific payload fields

Export all types for use across components.

#### Utility Functions (lib/utils.ts)

Create utility helper functions for the frontend. Include:

A utility function for conditionally joining Tailwind class names (commonly called `cn`). This is useful for component variants and conditional styling. It should handle string concatenation, filter falsy values, and optionally integrate with clsx or a similar library.

A utility function to format numbers for display with appropriate precision:
- Tank level: 2 decimal places
- Flow rates: 3 decimal places
- Valve position: 1 decimal place (as percentage)
- PID gains: variable precision based on magnitude

A utility function to format timestamps for trend charts. This should convert simulation time (seconds) to human-readable format like "MM:SS" or "HH:MM:SS" depending on duration.

A utility function to clamp values to valid ranges. Used for input validation before sending to API.

#### Next.js Configuration (next.config.js)

Configure Next.js build settings. The configuration should:
- Enable React strict mode
- Configure image domains if needed (none required initially)
- Set environment variables if needed
- Configure rewrites or redirects if needed to proxy API requests during development
- Enable experimental features if required (unlikely for this project)

For development, consider adding a rewrite rule to proxy API requests from `/api/*` to `http://localhost:8000/api/*` to avoid CORS issues, though the FastAPI backend already has CORS configured.

### Verification Strategy

After completing this task, verify:

**Project Structure:**
- Run `npm install` in the frontend directory - should complete without errors
- Verify all configuration files are present and valid
- Check that TypeScript compilation works without errors

**Development Server:**
- Start the Next.js dev server with `npm run dev`
- Server should start on port 3000 without errors
- Navigate to http://localhost:3000 in browser
- Verify the placeholder page renders with dark theme
- Check browser console for any errors
- Verify hot reload works by editing page.tsx

**Build Process:**
- Run `npm run build` to verify production build works
- No TypeScript errors should be present
- Build should complete successfully

**Code Quality:**
- Run `npm run lint` - should pass with no errors
- TypeScript strict mode should be catching type errors
- All imports should resolve correctly

### Edge Cases

**Port Conflicts:**
If port 3000 is already in use, Next.js will prompt to use an alternative port. This is acceptable for development. Document the actual port in use.

**Node Version Compatibility:**
Next.js 14 requires Node.js 18.17 or later. If an older version is detected during npm install, the task should note this requirement clearly.

**Path Resolution:**
If TypeScript path aliases don't resolve correctly in the IDE, verify that tsconfig.json includes the correct `baseUrl` and `paths` configuration, and that the IDE has reloaded the configuration.

**Tailwind IntelliSense:**
For optimal development experience, ensure the Tailwind CSS IntelliSense extension is installed in the code editor. This provides autocompletion for Tailwind classes.

### Acceptance Criteria

- [ ] Next.js project initialized in `frontend/` directory with App Router
- [ ] TypeScript configured with strict mode enabled
- [ ] Tailwind CSS configured with custom SCADA dark theme colors
- [ ] All required dependencies installed and listed in package.json
- [ ] Root layout (layout.tsx) created with dark theme and proper HTML structure
- [ ] Placeholder home page (page.tsx) created and renders successfully
- [ ] Global styles (globals.css) created with Tailwind imports
- [ ] Type definitions (lib/types.ts) created matching API models
- [ ] Utility functions (lib/utils.ts) created with helpers for formatting and styling
- [ ] Next.js config (next.config.js) created with appropriate settings
- [ ] Development server starts without errors on `npm run dev`
- [ ] Build process completes successfully on `npm run build`
- [ ] ESLint runs without errors on `npm run lint`
- [ ] Page displays in browser with dark theme at http://localhost:3000
- [ ] Hot reload works when editing files
- [ ] No TypeScript compilation errors
- [ ] All imports resolve correctly

---

## Task 20: WebSocket Connection Hook and State Management

**Phase:** 4 - Next.js Frontend
**Prerequisites:** Task 19 (Next.js project structure)

### Files to Create/Modify

```
frontend/
├── hooks/
│   ├── useWebSocket.ts        (create)
│   └── useSimulationState.ts  (create)
├── lib/
│   └── websocket.ts           (create - WebSocket client class)
└── app/
    └── providers.tsx          (create - Context providers)
```

### Requirements

#### WebSocket Client Class (lib/websocket.ts)

Create a WebSocket client class that manages the connection to the FastAPI backend at `ws://localhost:8000/ws`. This class should encapsulate all WebSocket logic and provide a clean interface for components.

The class should handle:

**Connection Management:**
- Connect to the WebSocket endpoint on instantiation
- Track connection state (connecting, connected, disconnected, error)
- Emit connection state changes via callbacks or events
- Support manual connect and disconnect methods

**Reconnection Logic:**
- Automatically reconnect on disconnection (not on manual close)
- Use exponential backoff for reconnection attempts starting at 1 second
- Maximum backoff delay of 30 seconds
- Maximum reconnection attempts: unlimited (keep trying)
- Reset backoff timer on successful connection
- Do not reconnect if disconnect was intentional (user action or component unmount)

**Message Handling:**
- Parse incoming JSON messages from server
- Validate message structure (should have "type" and "data" fields)
- Emit parsed messages to registered callbacks
- Handle malformed messages gracefully (log error, don't crash)
- Queue outgoing messages if connection is not ready (optional enhancement)

**Sending Commands:**
- Provide methods to send each command type to the server
- Setpoint command: accepts value (number)
- PID tuning command: accepts Kc, tau_I, tau_D (numbers)
- Inlet flow command: accepts value (number)
- Inlet mode command: accepts mode (string), min, max, variance (numbers)
- Serialize commands to JSON format expected by server
- Validate input ranges before sending (raise error on invalid input)

**Error Handling:**
- Catch and log WebSocket errors
- Emit error events to consumers
- Gracefully handle connection failures
- Distinguish between network errors and protocol errors

**Cleanup:**
- Provide a method to close connection and clean up resources
- Cancel any pending reconnection timers on cleanup
- Remove event listeners on cleanup

The class should not use React hooks internally - it should be a plain TypeScript class that can be used anywhere. The React integration will be in the custom hooks.

#### useWebSocket Hook (hooks/useWebSocket.ts)

Create a React hook that integrates the WebSocket client class with React component lifecycle. This hook manages the WebSocket instance and provides a clean interface to components.

The hook should:

**Instance Management:**
- Create a WebSocket client instance on mount (or lazily)
- Store instance in a ref to persist across renders
- Initialize connection automatically on mount
- Clean up connection on unmount

**State Exposure:**
- Return connection state (connecting, connected, disconnected, error)
- Return the most recent simulation state received
- Return error information if connection fails
- Use React state hooks to trigger re-renders on updates

**Command Functions:**
- Return stable callback functions (use useCallback) for sending commands
- Provide: setSetpoint(value)
- Provide: setPIDGains(Kc, tau_I, tau_D)
- Provide: setInletFlow(value)
- Provide: setInletMode(mode, min, max, variance)
- Each callback should handle errors and provide user feedback mechanism

**Message Processing:**
- Subscribe to incoming messages from WebSocket client
- Update React state when new simulation state arrives
- Handle state updates efficiently (only re-render when data changes)
- Parse and validate incoming message structure

**Effect Management:**
- Use useEffect to set up and tear down WebSocket connection
- Use useEffect to subscribe to WebSocket events
- Properly clean up all subscriptions and timers on unmount
- Handle strict mode double-mounting in development (connection should be resilient)

The hook signature should be:
```typescript
function useWebSocket(): {
  state: SimulationState | null;
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error';
  error: string | null;
  setSetpoint: (value: number) => void;
  setPIDGains: (Kc: number, tau_I: number, tau_D: number) => void;
  setInletFlow: (value: number) => void;
  setInletMode: (mode: string, min: number, max: number, variance: number) => void;
  reconnect: () => void;
}
```

#### Simulation State Context (app/providers.tsx)

Create a React Context provider that wraps the useWebSocket hook and makes simulation state available to all components in the tree. This centralizes WebSocket management and prevents multiple connections.

The provider should:

**Context Creation:**
- Create a SimulationContext using React.createContext
- Define context value type matching useWebSocket return type
- Provide default values (null state, disconnected status, no-op functions)

**Provider Component:**
- Create a SimulationProvider component that accepts children
- Call useWebSocket hook internally (single instance for entire app)
- Pass hook return value to context provider value
- Wrap children with the context provider

**Consumer Hook:**
- Export a useSimulation hook that calls useContext(SimulationContext)
- Throw error if used outside provider (helps catch usage errors)
- Return the full context value for components to consume

**Integration:**
- Update app/layout.tsx to wrap the app with SimulationProvider
- Ensure provider is inside the body element but wraps page content
- This makes simulation state available to all page components

The provider pattern ensures:
- Single WebSocket connection for entire application
- Centralized state management
- Easy access from any component via useSimulation hook
- Proper cleanup when app unmounts

#### useSimulationState Hook (hooks/useSimulationState.ts)

Create a derived hook that provides convenient access to specific parts of simulation state. This hook should use useSimulation internally and return computed values.

The hook should:

**Consume Context:**
- Call useSimulation to get the full context
- Extract simulation state and connection status
- Return null-safe accessors for state fields

**Computed Values:**
- Calculate derived metrics if needed (e.g., tank fill percentage)
- Format values for display (apply proper decimal precision)
- Provide boolean flags for state checks (isConnected, hasData, isStable)

**Convenience Accessors:**
- Provide individual state field getters (level, setpoint, flows, valve)
- Return undefined or null for missing data (don't throw errors)
- Type guard to ensure consumers handle missing data gracefully

This hook is optional but improves component ergonomics by handling null checks and providing computed values in one place.

### Implementation Notes

**WebSocket URL Configuration:**
The WebSocket URL should be configurable via environment variable. Use `NEXT_PUBLIC_WS_URL` environment variable with fallback to `ws://localhost:8000/ws`. Next.js environment variables prefixed with `NEXT_PUBLIC_` are embedded in the browser bundle.

**Connection Timing:**
The WebSocket connection should be established when the component tree mounts, not during SSR (server-side rendering). Use `useEffect` to ensure connection happens client-side only.

**Type Safety:**
All message payloads should be validated against the TypeScript interfaces defined in lib/types.ts. Consider using a runtime validation library like Zod if needed.

**Performance:**
The simulation sends updates at 1 Hz (once per second). This is a low update rate and should not cause performance issues. No throttling or debouncing is needed.

**State Updates:**
React state updates from WebSocket messages should use functional updates if they depend on previous state. For simple replacement (like simulation state), direct updates are fine.

### Verification Strategy

After completing this task:

**Unit Testing (manual for now):**
- Create a test page component that uses useSimulation hook
- Display connection status on screen
- Display all simulation state fields when connected
- Add buttons to trigger each command function
- Verify WebSocket connection establishes automatically

**Integration with Backend:**
- Ensure FastAPI backend is running on port 8000
- Start Next.js dev server
- Open browser to http://localhost:3000
- Check browser DevTools network tab for WebSocket connection
- Verify WebSocket shows "connected" status in network panel
- Verify messages are flowing (one per second)

**Command Testing:**
- Add temporary controls to test page
- Click setpoint button - verify command sends via WebSocket
- Check backend logs - command should be received and processed
- Verify simulation state updates reflect the command
- Test all four command types (setpoint, PID, inlet flow, inlet mode)

**Reconnection Testing:**
- With frontend and backend running, stop the backend server
- Verify frontend shows "disconnected" status
- Restart backend server
- Verify frontend automatically reconnects within a few seconds
- Verify simulation state resumes updating

**Cleanup Testing:**
- Navigate away from page
- Verify WebSocket connection closes (check network panel)
- Navigate back to page
- Verify new WebSocket connection establishes

### Edge Cases

**Initial Connection Failure:**
If backend is not running when frontend starts, the WebSocket should show "connecting" status and keep retrying. When backend starts, connection should succeed automatically.

**Mid-Stream Disconnection:**
If connection drops during usage (network issue, backend restart), the frontend should show "disconnected" and attempt to reconnect. No user action should be required.

**Malformed Messages:**
If the backend sends a message that doesn't match expected format, log an error to console but don't crash. The application should remain usable with stale data.

**Multiple Tabs:**
If multiple browser tabs open to the application, each will create its own WebSocket connection. This is acceptable behavior. Each connection sends commands independently and receives the same state updates.

**React Strict Mode:**
In development, React 18 strict mode mounts components twice. The WebSocket hook should handle this gracefully by cleaning up the first connection before creating the second.

**SSR Considerations:**
WebSocket connections must only be created in the browser, never during server-side rendering. Use `useEffect` to ensure client-side only execution. The connection state should be "disconnected" during SSR.

### Acceptance Criteria

- [ ] WebSocket client class (lib/websocket.ts) created with all features
- [ ] Connection management with automatic reconnection implemented
- [ ] Exponential backoff reconnection logic working correctly
- [ ] Message parsing and validation implemented
- [ ] Command sending methods for all four command types
- [ ] Error handling and logging in place
- [ ] useWebSocket hook (hooks/useWebSocket.ts) created
- [ ] Hook manages WebSocket lifecycle correctly (mount/unmount)
- [ ] Hook returns connection status and simulation state
- [ ] Hook provides stable callback functions for commands
- [ ] SimulationProvider context created in app/providers.tsx
- [ ] Context makes simulation state available to all components
- [ ] useSimulation hook exports context consumer with error checking
- [ ] Root layout wraps app with SimulationProvider
- [ ] Test page can consume simulation state via useSimulation hook
- [ ] WebSocket connection establishes automatically when page loads
- [ ] Incoming simulation state updates trigger React re-renders
- [ ] Command functions send correctly formatted messages to backend
- [ ] Reconnection works automatically after disconnection
- [ ] Connection cleans up properly on component unmount
- [ ] No TypeScript errors
- [ ] Connection status visible in browser DevTools network panel
- [ ] Backend logs show received commands when triggered from frontend

---

## Task 21: Tab Navigation and Layout Structure

**Phase:** 4 - Next.js Frontend
**Prerequisites:** Task 20 (WebSocket connection functional)

### Files to Create/Modify

```
frontend/
├── components/
│   ├── TabNavigation.tsx      (create)
│   ├── ProcessView.tsx        (create - placeholder)
│   ├── TrendsView.tsx         (create - placeholder)
│   └── ConnectionStatus.tsx   (create)
└── app/
    └── page.tsx               (modify - add tabs)
```

### Requirements

#### Tab Navigation Component (components/TabNavigation.tsx)

Create a tab navigation component that allows switching between Process View and Trends View. This should follow SCADA interface conventions with clear, high-contrast styling.

The component should:

**Visual Design:**
- Display two tabs: "Process" and "Trends"
- Active tab should be visually distinct (different background, border, or underline)
- Inactive tabs should have hover state for interactivity feedback
- Use dark theme colors consistent with SCADA aesthetic
- Tab labels should be clearly readable (good contrast ratio)
- Consider using a subtle border or shadow to separate tabs from content

**State Management:**
- Accept activeTab and onTabChange props
- activeTab: string ("process" or "trends")
- onTabChange: callback function that receives new tab name
- Parent component manages which tab is active
- Component is controlled (doesn't manage its own state)

**Interaction:**
- Click on tab to activate it
- Keyboard navigation support (arrow keys to move between tabs)
- Enter or Space to activate focused tab
- Proper ARIA attributes for accessibility (role="tablist", role="tab")
- Focus indicators for keyboard users

**Responsive Design:**
- Tabs should work on both desktop and mobile screens
- On narrow screens, tabs might stack or use full width
- Font size and padding should be appropriate for touch targets

The component should be purely presentational and not depend on any simulation state. It simply provides navigation UI.

#### Connection Status Component (components/ConnectionStatus.tsx)

Create a small indicator component that shows the WebSocket connection status. This should be visible at all times so users know if they're seeing live data.

The component should:

**Consume Simulation Context:**
- Use the useSimulation hook to get connection status
- Display different states: connecting, connected, disconnected, error

**Visual Indicators:**
- Show a colored dot or icon indicating status
- Green dot: connected
- Yellow dot: connecting
- Red dot: disconnected or error
- Include text label next to indicator (e.g., "Connected", "Reconnecting...")
- Update in real-time as connection state changes

**Visual Design:**
- Small, unobtrusive component (top-right corner or near tabs)
- High contrast against dark background
- Use semantic colors (green = good, red = bad)
- Optional: show connection uptime or last update timestamp
- Optional: show reconnection attempt count when reconnecting

**Error Details:**
- If connection status is "error", display error message
- Show error in a tooltip or expandable section
- Don't overwhelm the UI with error details in normal view

**Positioning:**
- Component should be absolutely or fixed positioned
- Common locations: top-right corner, bottom-right corner, near tabs
- Should not interfere with main content area

This component provides crucial feedback about data freshness and system health.

#### Process View Placeholder (components/ProcessView.tsx)

Create a placeholder component for the Process view that will later contain the tank visualization and controls. For now, this should display:

**Placeholder Content:**
- Heading: "Process View"
- Brief description: "Tank visualization and real-time controls"
- Connection status (using ConnectionStatus component)
- Current simulation time (if connected)
- Current tank level (if connected)
- Current setpoint (if connected)
- Display values formatted with appropriate precision

**Consume Simulation State:**
- Use useSimulation hook to access simulation state
- Display "Waiting for data..." if state is null
- Display actual values when data is available
- Update in real-time as state changes (1 Hz)

**Layout:**
- Center content in the view
- Use card or panel styling for information display
- Apply SCADA dark theme colors
- Good spacing and typography

This placeholder demonstrates that the WebSocket integration is working and data is flowing. The actual tank graphic and controls will be added in Task 22.

#### Trends View Placeholder (components/TrendsView.tsx)

Create a placeholder component for the Trends view that will later contain historical trend charts. For now, this should display:

**Placeholder Content:**
- Heading: "Trends View"
- Brief description: "Historical process trends and analytics"
- Message: "Charts will be implemented in next phase"
- Optional: show last 10 state updates as a simple list or table
- Display timestamp, level, setpoint, flows for each update

**Consume Simulation State:**
- Use useSimulation hook (will need to maintain short history in state)
- Store last N state updates in component state
- Display in reverse chronological order (newest first)

**Layout:**
- Similar styling to Process View for consistency
- Use monospace font for numeric data display
- Table or list layout for historical data
- Scrollable if data exceeds viewport height

This placeholder shows that tab switching works and prepares the structure for the actual charts.

#### Home Page Update (app/page.tsx)

Modify the home page to integrate the tab navigation and view components.

The page should:

**State Management:**
- Maintain activeTab state using useState hook
- Default to "process" tab
- Persist tab selection across WebSocket reconnections

**Layout Structure:**
```
- Page wrapper (full height, dark background)
  - Header section
    - Application title
    - Subtitle
    - ConnectionStatus component (top-right)
  - TabNavigation component
    - Pass activeTab and onTabChange
  - Main content area
    - Conditionally render ProcessView or TrendsView based on activeTab
  - Optional: Footer with version or credits
```

**Styling:**
- Full viewport height layout
- Header with padding and border-bottom
- Tab navigation just below header
- Main content area fills remaining vertical space
- Use Tailwind classes for dark theme
- Smooth transitions when switching tabs (optional)

**Data Flow:**
- SimulationProvider wraps the entire app (in layout.tsx from Task 20)
- Page component doesn't directly use useSimulation
- Child components (views) consume simulation state independently
- Tab state is local to the page component

The page orchestrates the overall layout but delegates specific functionality to child components.

### Implementation Notes

**Tab Switching Performance:**
Both views should remain mounted when switching tabs (just hide with CSS). This preserves state and avoids re-initializing WebSocket connections. Use CSS display:none or Tailwind hidden class to hide inactive view.

Alternatively, unmount inactive view if you want to reset its state. For this application, keeping both mounted is simpler.

**ARIA Attributes:**
For accessibility, use proper ARIA roles:
- TabNavigation: role="tablist"
- Each tab button: role="tab", aria-selected (true/false), aria-controls (ID of panel)
- Each view: role="tabpanel", aria-labelledby (ID of corresponding tab)

This enables screen readers to announce tab structure correctly.

**Styling Approach:**
Use Tailwind utility classes for all styling. Avoid writing custom CSS unless absolutely necessary. Define custom colors in tailwind.config.js from Task 19.

**Component Organization:**
All components should be in the `components/` directory. Use PascalCase naming. Export as default from each file.

### Verification Strategy

After completing this task:

**Visual Verification:**
- Start both backend (port 8000) and frontend (port 3000)
- Open http://localhost:3000 in browser
- Verify page shows header with title
- Verify connection status indicator appears (should show "Connected" with green dot)
- Verify tab navigation shows "Process" and "Trends" tabs
- Verify Process tab is active by default

**Tab Switching:**
- Click on "Trends" tab
- Verify tab switches (visual change)
- Verify Trends view content appears
- Click back to "Process" tab
- Verify Process view content appears
- Repeat several times - should be smooth and instant

**Data Display:**
- In Process view, verify current simulation values are displayed
- Verify values update approximately once per second
- Verify formatting is correct (2 decimals for level, 3 for flows)
- Watch connection status - should remain "Connected"

**Reconnection Handling:**
- Stop the backend server
- Verify connection status changes to "Disconnected" or "Reconnecting"
- Verify Process view still shows last received data (or "Waiting for data...")
- Restart backend
- Verify connection status returns to "Connected"
- Verify data updates resume

**Keyboard Navigation:**
- Tab through the interface with keyboard
- Verify tabs can be focused and activated with keyboard
- Verify focus indicators are visible
- Test arrow keys on tab navigation (if implemented)

**Responsive Behavior:**
- Resize browser window to mobile size
- Verify tabs still work and are readable
- Verify content doesn't overflow
- Verify on narrow screens layout remains usable

### Edge Cases

**No Backend Connection:**
If backend is not running, connection status should show "Connecting" or "Disconnected", and both views should handle null state gracefully by showing "Waiting for data..." message.

**Fast Tab Switching:**
Clicking rapidly between tabs should not cause any errors or visual glitches. Each tab should render correctly regardless of switching speed.

**Stale Data Display:**
When disconnected, views should display the last received data with a clear indication that it's stale (connection status shows disconnected). Don't show empty state if data was previously received.

**Long Tab Labels:**
If in the future tab labels get longer, ensure they don't wrap awkwardly. Use appropriate text sizing and truncation if needed.

### Acceptance Criteria

- [ ] TabNavigation component created with two tabs (Process, Trends)
- [ ] Tab switching works via click interaction
- [ ] Active tab is visually distinct from inactive tabs
- [ ] Keyboard navigation works (tab focus, enter/space activation)
- [ ] ARIA attributes present for accessibility
- [ ] ConnectionStatus component created and displays correct status
- [ ] Connection status updates in real-time based on WebSocket state
- [ ] Visual indicators (colored dots) clearly show connection health
- [ ] ProcessView placeholder component created
- [ ] ProcessView displays current simulation values when connected
- [ ] ProcessView handles null state gracefully (shows waiting message)
- [ ] TrendsView placeholder component created
- [ ] TrendsView displays placeholder content
- [ ] Home page (app/page.tsx) updated with full layout
- [ ] Page includes header with title and connection status
- [ ] Page includes tab navigation
- [ ] Page conditionally renders correct view based on active tab
- [ ] Switching tabs updates the displayed view immediately
- [ ] Both views can access simulation state via useSimulation hook
- [ ] Dark theme styling applied throughout
- [ ] All components use Tailwind classes for styling
- [ ] No TypeScript errors
- [ ] Layout is responsive and works on mobile sizes
- [ ] Browser DevTools console shows no errors
- [ ] Visual appearance matches SCADA interface aesthetic

---

## Upcoming Work (After Task 21)

### Task 22: Process View - Tank Visualization and Basic Controls

**Scope:** Build the tank SVG graphic with animated fill level, flow indicators, valve indicator, and basic control inputs for setpoint and inlet flow.

**Key Deliverables:**
- SVG tank graphic component with responsive sizing
- Animated liquid fill level reflecting real-time state
- Flow rate indicators for inlet and outlet (with arrows and values)
- Valve position indicator
- Setpoint input control with validation
- Inlet flow input control with validation
- Integration with WebSocket commands

### Task 23: Process View - PID Control Panel

**Scope:** Add PID tuning controls and display PID state information.

**Key Deliverables:**
- PID gains input controls (Kc, tau_I, tau_D)
- Current PID state display (error, integral term)
- Preset tuning configurations (conservative, moderate, aggressive)
- Live tuning capability (update while running)
- Input validation and range checking

### Task 24: Process View - Inlet Mode Controls

**Scope:** Add controls for switching between constant and Brownian inlet modes.

**Key Deliverables:**
- Mode selector (constant vs. Brownian)
- Brownian parameters inputs (min, max, variance)
- Current mode indicator
- Mode-specific help text
- Integration with WebSocket inlet_mode command

### Task 25: Trends View - Recharts Integration

**Scope:** Implement historical trend plotting using Recharts library.

**Key Deliverables:**
- Fetch historical data from REST API on mount
- Plot level vs setpoint on first chart
- Plot inlet flow vs outlet flow on second chart
- Plot valve position on third chart
- Time axis formatting
- Responsive chart sizing
- Auto-scrolling with live data
- Zoom and pan controls (if needed)

### Task 26: Trends View - Time Range Selector

**Scope:** Add controls to adjust the time range displayed in trends.

**Key Deliverables:**
- Time range dropdown or slider
- Options: 5 min, 15 min, 30 min, 1 hour, 2 hours
- Fetch appropriate historical data on selection change
- Chart updates smoothly when range changes
- Display current selection clearly

### Task 27: UI Polish and Production Ready

**Scope:** Final refinements, error handling, loading states, and production build.

**Key Deliverables:**
- Loading spinners for async operations
- Error boundaries for graceful error handling
- Toast notifications for user actions
- Confirmation dialogs for destructive actions (reset simulation)
- Production build optimization
- Environment variable configuration
- Docker container for frontend (optional)
- Deployment documentation

### Phase 5: Integration and Testing (Future)

After Phase 4 frontend is complete, Phase 5 will focus on:
- End-to-end testing with Playwright
- Integration testing of full stack
- Performance testing and optimization
- Security review
- Documentation updates
- User acceptance testing

---

## Notes on Phase 4 Development

### Development Workflow

1. **Start Backend First:** Always ensure the FastAPI backend is running before developing frontend features that depend on it. This allows real-time testing of WebSocket and REST integrations.

2. **Hot Reload:** Next.js dev server provides hot module replacement. Changes to components will reflect immediately in the browser without full page reload.

3. **Type Safety:** Leverage TypeScript strict mode throughout. The types in lib/types.ts should match the FastAPI Pydantic models exactly to catch integration issues at compile time.

4. **Component Testing:** Create small test pages to verify each component in isolation before integrating into the main application.

### Styling Guidelines

**SCADA Aesthetic Principles:**
- **High Contrast:** Text and indicators should have high contrast against dark backgrounds for readability
- **Minimal Decoration:** Avoid unnecessary visual flourishes; focus on functionality
- **Semantic Colors:** Use colors consistently (green = normal, yellow = warning, red = alarm)
- **Clear Hierarchy:** Important information should be larger or more prominent
- **Monospace for Numbers:** Use monospace font for numeric displays to prevent layout shift

**Tailwind Dark Theme:**
- Use `bg-gray-900` or `bg-gray-950` for main backgrounds
- Use `bg-gray-800` for cards and panels
- Use `text-gray-100` or `text-white` for primary text
- Use `text-gray-400` for secondary text
- Use `border-gray-700` for borders and dividers

### WebSocket Considerations

**Update Frequency:**
The simulation sends updates at 1 Hz (once per second). This is intentionally slow for:
- Easier debugging and observation of control behavior
- Reduced network traffic
- More realistic SCADA update rates

Components should not expect updates faster than 1 Hz. Don't implement animations that assume 60 FPS data.

**Command Throttling:**
User input controls (sliders, inputs) should throttle or debounce commands to avoid overwhelming the WebSocket with messages. A reasonable approach:
- Debounce text inputs (wait 300ms after user stops typing)
- Throttle sliders (send at most once per 200ms during drag)
- Send button clicks immediately (no throttling needed)

### Next.js App Router Patterns

**Server vs Client Components:**
- All components in this project will be Client Components (use "use client" directive)
- Server Components can't use hooks, event handlers, or browser APIs
- Since we need WebSocket connections, everything must be client-side

**File Conventions:**
- `layout.tsx`: Shared layout for routes
- `page.tsx`: Page component for a route
- `loading.tsx`: Loading UI (optional)
- `error.tsx`: Error boundary (optional)

**Data Fetching:**
For the initial config fetch (GET /api/config), use useEffect in a client component. Server Components are not beneficial for this real-time application since everything depends on client-side WebSocket state.

### TypeScript Best Practices

**Type Everything:**
- All props interfaces should be explicitly defined
- Use `type` or `interface` for prop definitions
- Avoid `any` type - use `unknown` if type is truly unknown
- Enable strict mode in tsconfig.json

**Import Organization:**
- React imports first
- Third-party imports next
- Local imports last
- Use absolute imports with @ alias for local modules

**Component Typing:**
```typescript
interface ComponentProps {
  // prop definitions
}

export default function Component({ prop1, prop2 }: ComponentProps) {
  // component implementation
}
```

### Performance Considerations

**Rendering Optimization:**
- Use React.memo for expensive components that receive the same props often
- Use useCallback for callback props to prevent unnecessary re-renders
- Use useMemo for expensive computations
- For this application, these are likely not needed initially - optimize if performance issues arise

**State Updates:**
- Simulation state updates (1 Hz) should not cause performance issues
- Recharts can handle 7200 data points (2 hours of history) without problems
- If chart performance becomes an issue, consider data downsampling for longer time ranges

**Bundle Size:**
- Next.js automatically code-splits by route
- Recharts is a relatively heavy library - it will only load when Trends view is rendered
- No additional bundle optimization needed initially

### Accessibility Requirements

**Minimum Standards:**
- All interactive elements must be keyboard accessible
- All images and icons must have alt text or aria-labels
- Color should not be the only indicator of state (use text labels too)
- Form inputs must have associated labels
- Tab navigation should follow logical order

**ARIA Attributes:**
- Use semantic HTML elements when possible (button, input, label)
- Add ARIA roles only when semantic HTML is insufficient
- Use aria-label for icon-only buttons
- Use aria-live for dynamic content updates (connection status, simulation values)

### Testing Strategy

**Manual Testing (Current Phase):**
- Test in Chrome, Firefox, and Safari
- Test on desktop and mobile screen sizes
- Test keyboard navigation
- Test with backend stopped/started to verify reconnection
- Test all user interactions

**Future Automated Testing:**
- Unit tests for hooks and utility functions (Vitest or Jest)
- Component tests for UI components (React Testing Library)
- E2E tests for complete workflows (Playwright)

### Known Limitations and Future Enhancements

**Current Scope Limitations:**
- Single simulation instance (no multi-user support)
- No authentication or authorization
- No data persistence beyond 2-hour ring buffer
- No export functionality for historical data
- No configurable chart axes or customization

**Potential Future Enhancements:**
- User accounts and saved configurations
- Multiple simulation instances
- Data export to CSV
- Advanced charting features (annotations, custom time ranges)
- Alarm configuration and notification system
- Comparison mode (run two simulations side-by-side)
- Integration with machine learning models for predictive control

---

**Tasks Summary:**
- Task 19: Next.js project setup and basic structure ✨ READY TO START
- Task 20: WebSocket connection and state management
- Task 21: Tab navigation and layout structure

**Estimated Completion:** Tasks 19-21 should take 2-3 engineer sessions to complete, assuming no major blockers. This establishes the foundational frontend infrastructure that subsequent tasks will build upon.
