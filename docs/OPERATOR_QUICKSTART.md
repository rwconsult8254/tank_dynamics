# Tank Dynamics Simulator - Operator Quick Start Guide

## What Is This?

The Tank Dynamics Simulator is a real-time educational tool for learning process control principles. It simulates a liquid tank with:
- **Inlet flow**: Liquid entering the tank from the top
- **Outlet control**: A valve controlling how much liquid leaves
- **Level sensor**: Measures tank level continuously
- **Automatic controller**: Adjusts the valve to maintain a desired level

Think of it as a physics-based practice system for tuning PID (Proportional-Integral-Derivative) controllers, similar to what you'd encounter in a real chemical plant, water treatment facility, or manufacturing process.

## Who Should Use This?

- **Process operators**: Learning control system fundamentals
- **Control engineers**: Tuning and testing PID parameters
- **Students**: Understanding how feedback control works
- **Automation professionals**: Practicing controller tuning before real-world deployment

## What You Can Do

- **Monitor tank level** in real-time
- **Change the target level** (setpoint)
- **Adjust PID tuning parameters** to improve controller response
- **Create process disturbances** to test controller robustness
- **View historical trends** showing how the system responds over time
- **View trends** for analysis with interactive charts

## System Requirements

- **Web browser**: Chrome, Firefox, Safari, or Edge (recent versions)
- **Network connection**: To connect to the simulator server
- **No special software**: Everything runs in your browser

---

## Getting Started

### Step 1: Open the Application

1. Open your web browser
2. Navigate to the application URL (e.g., `http://localhost:3000`)
3. You should see the Tank Dynamics Simulator interface

### Step 2: Check Connection Status

Look at the top right of the screen for the **Connection Status** indicator:
- **Green "Connected"**: System is ready to use
- **Red "Disconnected"**: Backend server not running (contact system administrator)
- **Yellow "Connecting"**: Waiting for connection (give it a few seconds)

### Step 3: View the Tank

You'll see a visual representation of the tank showing:
- **Blue fill level**: Current liquid height
- **Target line**: Desired setpoint level
- **Inlet at top**: Where liquid enters
- **Outlet at bottom**: Where liquid leaves via the control valve

---

## Understanding the Process View

### The Tank Graphic

The left side shows a real-time visualization of the tank:

| Part | What It Shows |
|------|--------------|
| **Blue area** | Actual liquid level in meters (0-5m) |
| **Red dashed line** | Target setpoint (what level we're trying to maintain) |
| **Top inlet arrow** | Inlet flow entering the tank |
| **Bottom outlet** | Outlet flow controlled by the valve position |
| **Gauge readings** | Current numerical values for all parameters |

### Control Panel (Right Side)

**Setpoint** (target level)
- Shows desired tank level in meters
- Range: 0 to 5 meters
- Click the number, enter new value, press Enter

**PID Parameters** (controller tuning)
- **Kc** (Controller Gain): Controls how aggressively the controller responds
  - Higher = faster response (but risk of oscillation)
  - Lower = slower, smoother response
  - Range: 0.5 to 10.0
  
- **τ_I** (Integral Time): How fast the controller eliminates steady-state error
  - Lower = faster correction of offset
  - Higher = slower but gentler correction
  - Range: 1 to 100 seconds
  
- **τ_D** (Derivative Time): Prevents overshoot by predicting level changes
  - Usually left at 0 for beginner tuning
  - Range: 0 to 10 seconds

**Inlet Flow Mode**
- **Manual**: Constant inlet flow (you set the flow rate)
- **Brownian**: Random flow variations (tests controller robustness)

### Real-Time Data

All values update **once per second**:
- Tank level (m)
- Inlet and outlet flows (m³/s)
- Valve position (%)
- Controller output

---

## Basic Operations

### How to Change the Setpoint

1. Look at the "SP" (setpoint) input field on the tank graphic
2. Click on the number field
3. Clear the current value and type your desired level (0-5 meters)
4. Press **Enter** or click outside the field
5. Watch the tank level move toward your new setpoint

**Example**: To set the tank to 3.5 meters:
- Click the setpoint input → Type `3.5` → Press Enter
- The controller automatically adjusts the outlet valve
- The tank level gradually rises or falls to reach 3.5m

### How to Adjust PID Tuning

The **PID parameters** control how the controller responds. To access them:

1. Look for the **"PID Tuning"** button or settings area
2. Adjust each parameter:
   - **Increase Kc** if response is too slow
   - **Decrease Kc** if the level oscillates or overshoots too much
   - **Decrease τ_I** for faster error correction
   - **Increase τ_I** for smoother response
   - Keep **τ_D** at 0 unless you understand derivative action

3. Press **Tab** or click elsewhere to apply changes
4. Observe the response in the tank level

**Tuning Tips**:
- Change one parameter at a time
- Wait 30-60 seconds to see the full effect
- Overshoot = reduce Kc or increase τ_I
- Too slow = increase Kc or reduce τ_I
- Oscillations = reduce Kc or increase τ_I

### How to Create Disturbances (Test Controller)

1. Find the **Inlet Flow Control** section
2. Choose your mode:

**Manual Mode**:
- Set a constant inlet flow (e.g., 0.1 m³/s)
- The controller must compensate to maintain setpoint
- Good for testing steady-state accuracy

**Brownian Mode**:
- Inlet flow varies randomly within bounds
- Tests how well the controller handles disturbances
- Set variance and bounds to control disturbance intensity
- Realistic model of real-world process variations

Example test:
1. Set setpoint to 3.0m
2. Find good PID tuning (minimal overshoot)
3. Switch to Brownian mode
4. Watch if controller maintains level despite varying inlet flow

---

## Using the Trends View

Click the **"Trends"** tab to see historical data visualized as charts.

### Three Charts Displayed

**1. Tank Level vs Setpoint**
- Green line = actual tank level
- Red line = setpoint (target)
- Good tuning = actual level follows setpoint closely

**2. Inlet and Outlet Flows**
- Blue line = inlet flow (coming in)
- Orange line = outlet flow (going out)
- When balanced = inlet equals outlet (steady state)

**3. Controller Output (Valve Position)**
- Shows the percentage position of the outlet valve (0-100%)
- Higher = more open = more flow out
- Shows the controller's corrective actions

### Time Range Selector

Choose how much history to view:
- **1 min**: Recent performance (fast dynamics)
- **5 min**: Moderate history
- **30 min**: Extended view of long-term behavior
- **1 hr**: Full hour of data
- **2 hr**: Maximum history available

### Analyzing Your Tuning

Look at the trends chart after a setpoint change:

| Response Characteristic | What It Means | Solution |
|------------------------|--------------|----------|
| Slow to reach setpoint | Controller gain too low | Increase Kc |
| Overshoots then oscillates | Controller too aggressive | Decrease Kc, increase τ_I |
| Reaches setpoint smoothly | Good tuning! | Keep current parameters |
| Steady error offset | Integral time too long | Decrease τ_I |
| Jerky valve movements | Gain too high | Decrease Kc |

---

## Common Tasks

### Task 1: Find Good PID Settings

1. Set setpoint to 2.5 meters
2. Start with these values:
   - Kc = 2.0
   - τ_I = 10.0
   - τ_D = 0.0
3. Change setpoint to 3.5 meters
4. Watch Trends View for 60 seconds
5. Adjust based on response:
   - If too slow: increase Kc by 0.5
   - If oscillates: decrease Kc by 0.5
   - If steady offset: decrease τ_I by 2.0
6. Repeat until satisfied

**Success criteria**: Setpoint reached within 30 seconds, minimal overshoot (<10%), no oscillations

### Task 2: Test Robustness with Disturbances

1. Achieve good tuning on constant inlet flow
2. Switch inlet to Brownian mode
3. Set variance to simulate realistic disturbances
4. Observe if controller maintains setpoint
5. Adjust tuning if level drifts too far
6. Test at different setpoints

**Success criteria**: Level stays within ±0.2m of setpoint despite flow variations

### Task 3: Observe Trends View

1. Run simulation for desired time (10 minutes recommended)
2. Switch to **Trends** tab
3. Use time range selector to view different periods (1 min, 5 min, 30 min, 1 hr, 2 hr)
4. Observe charts:
   - Tank Level vs Setpoint (identify peak overshoot and settling time)
   - Inlet and Outlet Flows (see disturbances and response)
   - Controller Output (valve position changes)
5. Use legend to toggle lines on/off for clearer view

### Task 4: Compare Different Tuning Methods

1. Use **Method A** (conservative tuning):
   - Kc = 1.5, τ_I = 15.0
   - Results: slow but stable
2. Use **Method B** (aggressive tuning):
   - Kc = 3.0, τ_I = 8.0
   - Results: fast but may oscillate
3. Use **Method C** (balanced):
   - Kc = 2.5, τ_I = 10.0
   - Results: good compromise
4. Compare results in Trends View

---

## Troubleshooting

### Problem: Connection Status Shows "Disconnected"

**Cause**: Backend server not running
**Solution**: Contact your system administrator to start the backend service
**Check**: Try refreshing the page (Ctrl+R or Cmd+R)

### Problem: Values Don't Update

**Cause**: Stale data from lost connection
**Solution**:
1. Check connection status (should be green)
2. Refresh the page
3. Wait 2-3 seconds for new data
4. If still not working, restart browser

### Problem: Control Changes Have No Effect

**Cause**: Value not properly submitted
**Solution**:
1. Verify you pressed **Enter** after changing value
2. Check that value is within valid range
3. Look at Trends View to confirm change was sent
4. Try using Tab key instead of Enter

### Problem: Charts Not Displaying

**Cause**: Not enough historical data yet
**Solution**:
1. Wait 10-20 seconds for data to accumulate
2. Check that Trends tab is selected
3. Verify time range selection (try 1 min)
4. Refresh page if charts remain blank

### Problem: Tank Level Goes Below 0 or Above 5

**Cause**: Process dynamics (extreme setpoint or disturbances)
**Solution**:
1. This can happen with poor tuning + large disturbances
2. Reduce setpoint to middle of range (2-3 meters)
3. Use conservative tuning values (lower Kc)
4. Reduce Brownian disturbance intensity

### Problem: Interface is Slow or Unresponsive

**Cause**: Browser performance or network latency
**Solution**:
1. Close other browser tabs/applications
2. Check network connection quality
3. Try a different browser (Chrome usually fastest)
4. Clear browser cache (settings → clear browsing data)

---

## Tips for Best Results

### Before Starting
- ✓ Ensure connection is green and stable
- ✓ Allow 5 seconds for initial data load
- ✓ Choose a setpoint in the middle range (2-4m)

### During Tuning
- ✓ Change one parameter at a time
- ✓ Wait 30-60 seconds between changes
- ✓ Use Trends View to visualize effects
- ✓ View trends charts for analysis if needed

### After Tuning
- ✓ Test with disturbances (Brownian mode)
- ✓ Try different setpoints (top, middle, bottom)
- ✓ Document your final parameters
- ✓ Compare with industry standards if known

---

## Safety Notes

⚠️ **This is a simulation, not a real process!**
- No physical danger
- No environmental impact
- Safe to experiment and make mistakes
- Use this to learn before working with real systems

---

## Getting Help

If you have questions:
1. **Connection issues**: Contact system administrator
2. **How controls work**: Review "Understanding the Process View" section
3. **PID tuning principles**: Search "PID tuning guide" online
4. **Specific software issues**: Report to development team with steps to reproduce

---

## Summary

**Quick Start Checklist**:
- [ ] Browser open, application loaded
- [ ] Connection status is green
- [ ] Setpoint visible on tank graphic
- [ ] Can change setpoint and see tank respond
- [ ] Can view Trends View with charts
- [ ] Can adjust PID parameters
- [ ] Ready to tune and experiment!

**Congratulations!** You're ready to start using the Tank Dynamics Simulator. Begin with the basic operations and work up to advanced tuning. Have fun learning!
