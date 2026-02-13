# Tank Dynamics Simulator - Development Workflow Guide

## Quick Reference

### Development Environment Setup

```bash
# Clone and enter directory
git clone YOUR_REPOSITORY_URL  # Replace with actual repository URL
cd tank_dynamics

# Install system dependencies (Ubuntu)
sudo apt install build-essential cmake libeigen3-dev libgsl-dev

# Setup Python environment
uv venv && source .venv/bin/activate

# Install project
uv pip install -e ".[dev]"
```

### Running the Full Stack (3 terminals)

```bash
# Terminal 1: Backend API
source .venv/bin/activate
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend dev server
cd frontend && npm run dev

# Terminal 3: Open browser
# Navigate to http://localhost:3000
```

### Running Tests

```bash
# C++ tests
ctest --test-dir build --output-on-failure

# Python tests
uv run pytest api/tests/ -v

# Python bindings
uv run pytest tests/python/ -v

# E2E tests (requires backend/frontend running)
cd frontend && npm run test:e2e
```

---

## Development Environment Setup

### Prerequisites

- **CMake**: 3.20+
- **C++**: 17 compiler (GCC 11+, Clang 14+, MSVC 2019+)
- **Python**: 3.10+
- **Node.js**: 18+
- **Git**: Any recent version

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/tank_dynamics.git
cd tank_dynamics
```

### Step 2: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install \
  build-essential \
  cmake \
  git \
  libeigen3-dev \
  libgsl-dev \
  python3-dev
```

**Arch Linux:**
```bash
sudo pacman -S \
  base-devel \
  cmake \
  eigen \
  gsl
```

**macOS:**
```bash
brew install cmake eigen gsl
```

### Step 3: Setup Python Environment

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate (Linux/macOS)
source .venv/bin/activate
```

### Step 4: Install Project Dependencies

```bash
# Install project in editable mode with dev dependencies
uv pip install -e ".[dev]"

# Verify installation
python3 -c "from tank_sim import Simulator; print('OK')"
```

---

## Building Components

### C++ Core

```bash
# Configure CMake (Debug build for development)
cmake -B build -DCMAKE_BUILD_TYPE=Debug

# Build with parallel jobs
cmake --build build --parallel $(nproc)

# Run tests
ctest --test-dir build --output-on-failure -V

# Or use make directly (if available)
cd build && make -j$(nproc) && make test
```

### Python Bindings

```bash
# Rebuild (already done by pip install, but can rebuild manually)
cmake -B build
cmake --build build

# Test Python can import module
python3 -c "from tank_sim import Model, Simulator; print('Bindings OK')"

# Run Python binding tests
uv run pytest tests/python/ -v
```

### Frontend

```bash
cd frontend

# Install Node dependencies
npm install

# Run development server
npm run dev

# Build for production (creates .next/ directory)
npm run build

# Run in production mode
npm run start

# Run ESLint
npm run lint
```

---

## Running the Full Stack

### Method 1: Manual (3 Terminals Recommended)

**Terminal 1 - Backend:**
```bash
source .venv/bin/activate
cd $PROJECT_ROOT  # Or navigate to your tank_dynamics directory
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd $PROJECT_ROOT/frontend  # Or navigate to your tank_dynamics/frontend directory
npm run dev
```

**Terminal 3 - Testing:**
```bash
# Open browser to http://localhost:3000
# Or run tests from here
cd $PROJECT_ROOT  # Or navigate to your tank_dynamics directory
uv run pytest api/tests/ -v
```

### Method 2: Concurrent (Single Terminal)

```bash
# Use tmux or screen to run both in one terminal
tmux new-session -d -s tank
tmux send-keys -t tank 'source .venv/bin/activate && uvicorn api.main:app --reload' Enter
tmux new-window -t tank
tmux send-keys -t tank 'cd frontend && npm run dev' Enter
tmux select-window -t tank:0

# Attach to tmux session
tmux attach-session -t tank
```

---

## Testing

### C++ Unit Tests

```bash
# Build with tests
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build

# Run all tests
ctest --test-dir build --output-on-failure

# Run specific test
ctest --test-dir build -R TankModel -V

# Run with more details
ctest --test-dir build --verbose --output-on-failure
```

### Python Tests

```bash
# Run all Python tests
uv run pytest api/tests/ -v

# Run specific test file
uv run pytest api/tests/test_api.py -v

# Run specific test function
uv run pytest api/tests/test_api.py::test_create_simulator -v

# Run with coverage
uv run pytest api/tests/ --cov=api --cov-report=html

# Show coverage report
open htmlcov/index.html
```

### E2E Tests (Playwright)

Requires backend and frontend running.

```bash
cd frontend

# Run all E2E tests
npm run test:e2e

# Run specific test file
npx playwright test connection.spec.ts

# Run in UI mode (helpful for debugging)
npm run test:e2e:ui

# Run in debug mode with step-through
npm run test:e2e:debug

# Show HTML report
npx playwright show-report
```

### Test Coverage

```bash
# Python coverage
uv run pytest api/tests/ --cov=api --cov-report=term-missing

# Generate HTML report
uv run pytest api/tests/ --cov=api --cov-report=html
open htmlcov/index.html
```

---

## Code Organization

### Directory Structure

```
tank_dynamics/
├── src/                    # C++ core
│   ├── Model.h            # Tank model equations
│   ├── PID.h              # PID controller implementation
│   ├── Stepper.h          # Integration methods
│   └── Simulator.h        # Main simulation engine
├── bindings/              # pybind11 Python bindings
│   └── bindings.cpp       # Python interface
├── tests/                 # C++ unit tests
│   └── test_*.cpp         # Individual test files
├── api/                   # FastAPI backend
│   ├── main.py            # FastAPI application
│   ├── simulation.py      # Simulation manager
│   ├── models.py          # Pydantic models
│   └── tests/             # API tests
│       └── test_api.py
├── frontend/              # Next.js frontend
│   ├── app/               # Next.js App Router
│   │   ├── page.tsx       # Home page
│   │   └── providers.tsx  # React context providers
│   ├── components/        # React components
│   │   ├── TankGraphic.tsx
│   │   ├── TrendsView.tsx
│   │   ├── ProcessView.tsx
│   │   └── ...
│   ├── lib/               # Utilities
│   │   ├── types.ts       # TypeScript types
│   │   ├── utils.ts       # Helper functions
│   │   └── websocket.ts   # WebSocket client
│   ├── hooks/             # React custom hooks
│   │   └── useHistory.ts  # Historical data hook
│   ├── tests/e2e/         # Playwright E2E tests
│   └── playwright.config.ts
├── docs/                  # Documentation
│   ├── specs.md           # Project specification
│   ├── plan.md            # Implementation plan
│   ├── DEPLOYMENT.md      # Production deployment
│   ├── OPERATOR_QUICKSTART.md
│   └── ...
└── README.md              # Project overview
```

### Module Responsibilities

| Module | Purpose | Language |
|--------|---------|----------|
| `src/Model.h` | Tank dynamics equations | C++ |
| `src/PID.h` | PID control algorithm | C++ |
| `src/Simulator.h` | Main simulation loop | C++ |
| `bindings/` | Python interface to C++ | C++/Python |
| `api/main.py` | HTTP/WebSocket server | Python |
| `api/simulation.py` | Simulation management | Python |
| `frontend/` | Web UI | TypeScript/React |
| `frontend/lib/websocket.ts` | Real-time communication | TypeScript |

---

## Common Development Tasks

### Add New C++ Class

1. **Create header:**
   ```bash
   touch src/NewClass.h
   ```

2. **Define interface:**
   ```cpp
   #pragma once
   
   class NewClass {
   public:
     NewClass();
     void update(double dt);
     double getValue() const;
   private:
     double value_;
   };
   ```

3. **Create implementation:**
   ```bash
   touch src/NewClass.cpp
   ```

4. **Add to CMakeLists.txt:**
   ```cmake
   set(SOURCES
     src/NewClass.cpp
     # ... other files
   )
   ```

5. **Add Python binding:**
   ```cpp
   // In bindings/bindings.cpp
   py::class_<NewClass>(m, "NewClass")
     .def(py::init<>())
     .def("update", &NewClass::update)
     .def("get_value", &NewClass::getValue);
   ```

6. **Test:**
   ```bash
   cmake -B build && cmake --build build
   python3 -c "from tank_sim import NewClass; print('OK')"
   ```

### Add New API Endpoint

1. **Define Pydantic model** (if needed):
   ```python
   # In api/models.py
   class MyRequest(BaseModel):
       param1: str
       param2: float
   ```

2. **Add endpoint to main.py:**
   ```python
   from api.models import MyRequest

   @app.post("/api/my-endpoint")
   async def my_endpoint(request: MyRequest):
       # Implementation
       return {"result": "success"}
   ```

3. **Add test:**
   ```python
   # In api/tests/test_api.py
   def test_my_endpoint(client):
       response = client.post("/api/my-endpoint", json={"param1": "value", "param2": 1.5})
       assert response.status_code == 200
       assert response.json()["result"] == "success"
   ```

4. **Test:**
   ```bash
   uv run pytest api/tests/test_api.py::test_my_endpoint -v
   ```

### Add New React Component

1. **Create component:**
   ```bash
   touch frontend/components/MyComponent.tsx
   ```

2. **Define component:**
   ```typescript
   import React from "react";

   interface MyComponentProps {
     title: string;
     onAction: () => void;
   }

   export function MyComponent({ title, onAction }: MyComponentProps) {
     return (
       <div className="bg-gray-800 p-4 rounded">
         <h2 className="text-white text-lg">{title}</h2>
         <button onClick={onAction} className="bg-blue-600 text-white px-4 py-2 rounded">
           Action
         </button>
       </div>
     );
   }
   ```

3. **Use in page/component:**
   ```tsx
   import { MyComponent } from "@/components/MyComponent";

   export default function Home() {
     return (
       <div>
         <MyComponent title="My Title" onAction={() => console.log("Clicked")} />
       </div>
     );
   }
   ```

4. **Test manually:**
   ```bash
   npm run dev
   # Navigate to page in browser, verify component renders
   ```

### Add E2E Test

1. **Create test file:**
   ```bash
   touch frontend/tests/e2e/my-feature.spec.ts
   ```

2. **Write test:**
   ```typescript
   import { test, expect } from "@playwright/test";

   test.describe("My Feature", () => {
     test("should work correctly", async ({ page }) => {
       await page.goto("/");
       await page.waitForLoadState("networkidle");
       
       const element = page.getByText("My Feature");
       await expect(element).toBeVisible();
       
       await element.click();
       await page.waitForTimeout(500);
       
       const result = page.getByText("Success");
       await expect(result).toBeVisible();
     });
   });
   ```

3. **Run test:**
   ```bash
   npm run test:e2e my-feature.spec.ts
   ```

---

## Code Style and Standards

### C++

- Follow Google C++ Style Guide
- Use descriptive variable names
- Comment complex algorithms
- Add public method documentation
- Example:
  ```cpp
  /**
   * Updates the tank model with control input
   * @param dt Time step (seconds)
   * @param u_in Inlet flow (m³/s)
   * @param u_valve Valve position (0-1)
   */
  void update(double dt, double u_in, double u_valve);
  ```

### Python

- Follow PEP 8
- Use type hints on all functions
- Add docstrings to public functions
- Use `uv` not `pip`
- Example:
  ```python
  def calculate_error(actual: float, setpoint: float) -> float:
      """Calculate control error as difference from setpoint."""
      return setpoint - actual
  ```

### TypeScript/React

- Use functional components with hooks
- Proper TypeScript types (avoid `any`)
- Descriptive variable/function names
- Extract reusable logic into custom hooks
- Example:
  ```typescript
  interface TankData {
    level: number;
    setpoint: number;
  }

  export function TankDisplay({ data }: { data: TankData }) {
    return <div>{data.level}m / {data.setpoint}m</div>;
  }
  ```

---

## Git Workflow

### Branch Naming

- Feature: `feature/description` (e.g., `feature/pid-tuning`)
- Bug fix: `bugfix/description` (e.g., `bugfix/websocket-reconnect`)
- Release: `release/version` (e.g., `release/1.0.0`)

### Commit Messages

```
[Type] Brief description (50 chars max)

Optional longer explanation:
- What was changed
- Why it was changed
- Any important details

Footer: Closes #123 (if applicable)
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Example Workflow

```bash
# Create feature branch
git checkout -b feature/new-chart

# Make changes
# ... edit files ...

# Stage changes
git add frontend/components/NewChart.tsx

# Commit
git commit -m "feat: Add new trend chart visualization

- Displays real-time trend data
- Includes time range selector
- Responsive to data updates"

# Push to remote
git push origin feature/new-chart

# Create pull request on GitHub
# Wait for review
# Merge when approved
```

---

## Debugging

### Backend Debugging

```python
# Add debug statements
print(f"Debug: value={value}")  # Simple print
import pdb; pdb.set_trace()     # Breakpoint

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug(f"Debug info: {data}")
logger.error(f"Error occurred: {error}")
```

### Frontend Debugging

```typescript
// Browser console (F12)
console.log("Debug:", value);
console.error("Error:", error);

// React DevTools extension
// Inspect components, props, state

// Playwright debug mode
npm run test:e2e:debug

// VS Code debugging
// Add launch configuration in .vscode/launch.json
```

### Performance Profiling

```python
# Python profiling
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()
# ... run code ...
profiler.disable()
stats = pstats.Stats(profiler)
stats.print_stats()
```

---

## Troubleshooting

### C++ Build Issues

**Error: `cmake: command not found`**
- Install CMake: `sudo apt install cmake`

**Error: `fatal error: eigen3/Eigen/Dense: No such file`**
- Install Eigen: `sudo apt install libeigen3-dev`

**Error: `fatal error: gsl/gsl_odeiv2.h: No such file`**
- Install GSL: `sudo apt install libgsl-dev`

### Python Issues

**Error: `ModuleNotFoundError: No module named 'tank_sim'`**
```bash
cmake -B build && cmake --build build
source .venv/bin/activate
uv pip install -e .
```

**Error: `version conflicts / requirements not satisfied`**
```bash
uv lock --upgrade
uv sync
```

### Frontend Issues

**Error: `Cannot find module '@/components/...'`**
- Verify `jsconfig.json` or `tsconfig.json` has correct path aliases
- Check file actually exists
- Clear `.next` cache: `rm -rf frontend/.next`

**Error: `Port 3000 already in use`**
```bash
lsof -i :3000
kill -9 <PID>
npm run dev
```

**Tests timing out**
- Increase timeout: `test.setTimeout(60000)` for 60 seconds
- Check backend is running
- Check network latency

### WebSocket Issues

**Connection refused / Can't connect**
- Verify backend running on port 8000
- Check CORS configuration
- Verify WebSocket URL correct
- Check browser console for errors

---

## Resources

### Documentation
- [Plan](docs/plan.md): Implementation strategy
- [Specs](docs/specs.md): Project specification
- [API Reference](docs/API_REFERENCE.md): API endpoints

### External Resources
- [CMake](https://cmake.org/cmake/help/latest/)
- [pybind11](https://pybind11.readthedocs.io/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Next.js](https://nextjs.org/docs)
- [Playwright](https://playwright.dev/)
- [Tailwind CSS](https://tailwindcss.com/)

### Testing Resources
- [pytest](https://docs.pytest.org/)
- [Playwright Best Practices](https://playwright.dev/docs/best-practices)

---

## Quick Checklist for New Developers

- [ ] Clone repository
- [ ] Install system dependencies
- [ ] Create Python venv with `uv venv`
- [ ] Install project with `uv pip install -e ".[dev]"`
- [ ] Build C++: `cmake -B build && cmake --build build`
- [ ] Run C++ tests: `ctest --test-dir build`
- [ ] Run backend: `uvicorn api.main:app --reload`
- [ ] Run frontend: `cd frontend && npm run dev`
- [ ] Verify at http://localhost:3000
- [ ] Read docs/LESSONS_LEARNED.md for project insights
- [ ] Start with small changes and work up

Welcome to the team! 🚀
