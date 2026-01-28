# Tennessee Eastman Process Simulation: Equations and Mathematical Model

## Table of Contents

1. [Introduction](#introduction)
2. [Process Overview](#process-overview)
3. [Chemical Reactions](#chemical-reactions)
4. [Process Components](#process-components)
   - [Reactor](#reactor)
   - [Separator](#separator)
   - [Stripper](#stripper)
   - [Compressor](#compressor)
5. [Thermodynamic Models](#thermodynamic-models)
6. [State Variables and Differential Equations](#state-variables-and-differential-equations)
7. [Measurements and Control](#measurements-and-control)
8. [Process Disturbances](#process-disturbances)

---

## Introduction

The Tennessee Eastman Process is a realistic industrial chemical process simulation originally developed by Downs and Vogel (1993) for testing process control strategies. It represents a complete chemical plant with:

- **8 chemical components** (A, B, C, D, E, F, G, H)
- **4 chemical reactions**
- **50 state variables**
- **12 manipulated variables** (control inputs)
- **41 measured variables** (sensors)
- **20 programmed disturbances** (fault scenarios)

The simulation runs in continuous time, with differential equations describing the dynamic behavior of the plant.

---

## Process Overview

### Physical Description

The Tennessee Eastman process produces products G and H from four reactants (A, C, D, E) through an exothermic, irreversible reaction process:

```
Stream Inputs:
- Stream 1: Pure A feed
- Stream 2: Pure D feed
- Stream 3: Pure E feed
- Stream 4: A and C feed (mixed)

Main Process Flow:
1. Reactants → Reactor (with cooling)
2. Reactor output → Separator (vapor/liquid separation)
3. Separator vapor → Compressor → Recycle
4. Separator liquid → Stripper
5. Stripper products → Product stream (G & H)
```

### Component Molecular Weights

From `teprob.f:941-948`:

| Component | Molecular Weight (kg/kmol) |
|-----------|---------------------------|
| A         | 2.0                       |
| B         | 25.4                      |
| C         | 28.0                      |
| D         | 32.0                      |
| E         | 46.0                      |
| F         | 48.0                      |
| G         | 62.0                      |
| H         | 76.0                      |

---

## Chemical Reactions

The process involves four simultaneous reactions occurring in the gas phase within the reactor.

### Reaction Stoichiometry

**Reaction 1 (Product G formation):**
```
A(g) + C(g) + D(g) → G(g)
```

**Reaction 2 (Product H formation):**
```
A(g) + C(g) + E(g) → H(g)
```

**Reaction 3 (Byproduct F formation):**
```
A(g) + E(g) → F(g)
```

**Reaction 4 (Byproduct F formation, alternate):**
```
3A(g) + 2D(g) → 2F(g)
```

### Reaction Kinetics

From `teprob.f:503-520`, the reaction rates are calculated using Arrhenius-type expressions:

**Rate Equations (conceptual form):**

```
r₁ = k₁(T) × P_A^1.1544 × P_C^0.3735 × P_D × V_vr

r₂ = k₂(T) × P_A^1.1544 × P_C^0.3735 × P_E × V_vr

r₃ = k₃(T) × P_A × P_E × V_vr

r₄ = k₄(T) × P_A × P_D × V_vr
```

Where:
- `k_i(T)` = Temperature-dependent rate constant
- `P_i` = Partial pressure of component i (kPa)
- `V_vr` = Reactor vapor volume (m³)

**Detailed Rate Constants (from code):**

```fortran
! Line 503-506
RR(1) = exp(31.5859536 - 40000.0/(1.987×T_Kr)) × R1F
RR(2) = exp(3.00094014 - 20000.0/(1.987×T_Kr)) × R2F
RR(3) = exp(53.4060443 - 60000.0/(1.987×T_Kr))
RR(4) = RR(3) × 0.767488334
```

Where:
- `T_Kr` = Reactor temperature in Kelvin
- `R1F`, `R2F` = Adjustable kinetic factors (for disturbances)
- The denominators contain activation energies (E/R): 40000, 20000, 60000 K

**Pressure dependency (lines 507-517):**

```fortran
R1F = P_A^1.1544
R2F = P_C^0.3735
RR(1) = RR(1) × R1F × R2F × P_D
RR(2) = RR(2) × R1F × R2F × P_E
RR(3) = RR(3) × P_A × P_E
RR(4) = RR(4) × P_A × P_D
```

### Component Generation/Consumption Rates

From `teprob.f:521-527`, the net production rate for each component (kmol/hr):

```
CRXR(A) = -r₁ - r₂ - r₃             (A consumed in reactions 1,2,3)
CRXR(B) = 0                           (B is inert)
CRXR(C) = -r₁ - r₂                    (C consumed in reactions 1,2)
CRXR(D) = -r₁ - 1.5×r₄                (D consumed)
CRXR(E) = -r₂ - r₃                    (E consumed)
CRXR(F) = r₃ + r₄                     (F produced)
CRXR(G) = r₁                          (G produced)
CRXR(H) = r₂                          (H produced)
```

### Heat of Reaction

From line 528:
```
RH = r₁ × HTR(1) + r₂ × HTR(2)
```

Where:
- `HTR(1) = 0.06899381054` (kcal/kmol for reaction 1)
- `HTR(2) = 0.05` (kcal/kmol for reaction 2)
- `RH` = Total heat released by reactions (kcal/hr)

---

## Process Components

### Reactor

**Purpose:** Gas-phase reactions with heat removal via cooling water

**Key Variables:**
- `VTR = 1300 m³` - Total reactor volume
- `VLR` - Liquid volume in reactor (m³)
- `VVR = VTR - VLR` - Vapor volume (m³)
- `TCR` - Reactor temperature (°C)
- `PTR` - Reactor pressure (kPa)
- `XLR(i)` - Liquid mole fraction of component i
- `XVR(i)` - Vapor mole fraction of component i

#### Reactor Material Balances

From `teprob.f:763`, the differential equations for component moles in vapor phase:

**Vapor phase (components 1-8):**
```
dUCVR(i)/dt = FCM(i,7) - FCM(i,8) + CRXR(i)
```

Where:
- `UCVR(i)` = Moles of component i in reactor vapor (kmol)
- `FCM(i,7)` = Inlet molar flow of i to reactor (kmol/hr)
- `FCM(i,8)` = Outlet molar flow of i from reactor (kmol/hr)
- `CRXR(i)` = Net generation of i by reaction (kmol/hr)

**Explanation:** The change in moles equals inlet minus outlet plus chemical reaction.

#### Reactor Energy Balance

From `teprob.f:771-772`:

```
dETR/dt = HST(7)×FTM(7) - HST(8)×FTM(8) + RH + QUR
```

Where:
- `ETR` = Total enthalpy of reactor vapor (kcal)
- `HST(7)` = Specific enthalpy of reactor inlet (kcal/kmol)
- `FTM(7)` = Total molar flow to reactor (kmol/hr)
- `HST(8)` = Specific enthalpy of reactor outlet (kcal/kmol)
- `FTM(8)` = Total outlet flow (kmol/hr)
- `RH` = Heat of reaction (kcal/hr)
- `QUR` = Heat removed by cooling water (kcal/hr)

**Cooling water heat transfer (lines 670-673):**

```
UAR = UARLEV × (-0.5×AGSP² + 2.75×AGSP - 2.5) × 855490×10⁻⁶

QUR = UAR × (TWR - TCR) × (1 - 0.35×disturbance)
```

Where:
- `UAR` = Overall heat transfer coefficient (kcal/hr/°C)
- `UARLEV` = Level-dependent factor (0 to 1)
- `AGSP` = Agitator speed factor
- `TWR` = Cooling water temperature (°C)
- `TCR` = Reactor temperature (°C)

**Cooling water temperature dynamics (line 789-790):**

```
dTWR/dt = (FWR×500.53×(TCWR - TWR) - QUR×10⁶/1.8) / HWR
```

Where:
- `FWR` = Cooling water flow rate (m³/hr)
- `TCWR` = Cooling water inlet temperature (°C)
- `HWR = 7060` = Cooling water thermal mass constant

#### Reactor Pressure Calculation

The reactor pressure is the sum of partial pressures from the ideal gas law and vapor pressures.

**Gas components (A, B, C) - Ideal gas law (lines 478-483):**

```
P_i = (n_i × R × T) / V_vr
PTR = Σ P_i
```

Where:
- `R = 998.9` (gas constant in compatible units)
- `n_i = UCVR(i)` = moles of component i

**Liquid components (D, E, F, G, H) - Raoult's law (lines 484-491):**

```
P_i^vapor = exp(AVP(i) + BVP(i)/(TCR + CVP(i))) × XLR(i)
```

This is the **Antoine equation** for vapor pressure:

| Component | AVP    | BVP     | CVP   |
|-----------|--------|---------|-------|
| D         | 15.92  | -1444.0 | 259.0 |
| E         | 16.35  | -2114.0 | 265.5 |
| F         | 16.35  | -2114.0 | 265.5 |
| G         | 16.43  | -2748.0 | 232.9 |
| H         | 17.21  | -3318.0 | 249.6 |

### Separator

**Purpose:** Separate vapor (recycled) from liquid (sent to stripper)

**Key Variables:**
- `VTS = 3500 m³` - Total separator volume
- `VLS` - Liquid volume (m³)
- `VVS = VTS - VLS` - Vapor volume (m³)
- `TCS` - Separator temperature (°C)
- `PTS` - Separator pressure (kPa)

#### Separator Material Balances

From `teprob.f:764-765`:

```
dUCLS(i)/dt = FCM(i,8) - FCM(i,9) - FCM(i,10) - FCM(i,11)
```

Where:
- `UCLS(i)` = Moles of component i in separator liquid
- `FCM(i,8)` = Inlet from reactor
- `FCM(i,9)` = Vapor to compressor (recycle)
- `FCM(i,10)` = Purge stream
- `FCM(i,11)` = Liquid to stripper

#### Separator Flow Calculations

**Vapor flow to compressor (lines 589-600):**

The compressor creates a pressure difference that drives flow:

```
ΔP = PTV - PTS
FLMS = CPFLMX + FLCOEF×(1 - PR³) - VPOS(5)×53.349×√(ΔP)
FTM(9) = FLMS / XMWS(9)
```

Where:
- `PTV` = Compressor suction pressure
- `PR = PTV/PTS` = Pressure ratio
- `CPFLMX = 280275` = Maximum compressor flow (kg/hr)
- `VPOS(5)` = Compressor recycle valve position (0-100%)

**Purge flow (lines 585-588):**

```
ΔP = PTS - 760 kPa
FTM(10) = VPOS(6)×0.151169×√(ΔP) / XMWS(10)
```

Where `VPOS(6)` is the purge valve position.

**Liquid to stripper (line 570):**

```
FTM(11) = VPOS(7) × VRNG(7) / 100
```

Where:
- `VPOS(7)` = Separator pot liquid flow valve position
- `VRNG(7) = 1500` = Valve range (kmol/hr)

#### Separator Energy Balance

From `teprob.f:773-777`:

```
dETS/dt = HST(8)×FTM(8) - HST(9)×FTM(9) - HST(10)×FTM(10) - HST(11)×FTM(11) + QUS
```

Where:
- `QUS` = Heat removed by separator cooling (kcal/hr)

**Separator cooling (lines 674-676):**

```
UAS = 0.404655 × (1 - 1/(1 + (FTM(8)/3528.73)⁴))

QUS = UAS × (TWS - TST(8)) × (1 - 0.25×disturbance)
```

### Stripper

**Purpose:** Separate products (G, H) from lighter components via steam stripping

**Key Variables:**
- `VTC = 156.5 m³` - Total stripper volume
- `VLC` - Liquid volume (m³)
- `TCC` - Stripper temperature (°C)

#### Stripper Material Balances

From `teprob.f:766`:

```
dUCLC(i)/dt = FCM(i,12) - FCM(i,13)
```

Where:
- `FCM(i,12)` = Component i in feed from separator
- `FCM(i,13)` = Component i in product stream

#### Stripper Separation Model

The stripper uses a simplified separation model based on temperature and flow ratio (lines 614-634):

```
If FTM(11) > 0.1:
    TMPFAC = f(TCC)  [temperature factor]
    VOVRL = FTM(4)/FTM(11) × TMPFAC

    SFR(i) = α(i)×VOVRL / (1 + α(i)×VOVRL)
```

Where:
- `SFR(i)` = Separation factor for component i (fraction to vapor)
- `α(i)` = Component-specific separation coefficient:

| Component | α value |
|-----------|---------|
| D         | 8.5010  |
| E         | 11.402  |
| F         | 11.795  |
| G         | 0.0480  |
| H         | 0.0242  |

**Physical meaning:** Components D, E, F (lighter) preferentially go to vapor phase, while G, H (heavier products) stay in liquid.

#### Product Stream Composition

From `teprob.f:643-644`:

```
FCM(i,12) = FIN(i) - FCM(i,5)
```

Where `FCM(i,5)` is the vapor stream (recycled) and `FCM(i,12)` goes to product.

#### Stripper Energy Balance

From `teprob.f:778-782`:

```
dETC/dt = HST(4)×FTM(4) + HST(11)×FTM(11) - HST(5)×FTM(5) - HST(13)×FTM(13) + QUC
```

Where:
- `QUC` = Heat added by steam (kcal/hr)

**Steam heating (lines 677-678):**

```
If TCC < 100°C:
    QUC = UAC × (100 - TCC)
```

Where `UAC` is controlled by the steam valve (manipulated variable 9).

### Compressor

**Purpose:** Recycle vapor from separator back to reactor

**Key Variables:**
- `VTV = 5000 m³` - Compressor volume
- `TCV` - Compressor discharge temperature (°C)
- `PTV` - Compressor discharge pressure (kPa)

#### Compressor Material Balance

From `teprob.f:767-769`:

```
dUCVV(i)/dt = FCM(i,1) + FCM(i,2) + FCM(i,3) + FCM(i,5) + FCM(i,9) - FCM(i,6)
```

Where the inputs are:
- `FCM(i,1)` = Pure D feed
- `FCM(i,2)` = Pure E feed
- `FCM(i,3)` = Pure A feed
- `FCM(i,5)` = Vapor from stripper
- `FCM(i,9)` = Recycle from separator

And output:
- `FCM(i,6)` = Feed to reactor

#### Compressor Work and Temperature Rise

From `teprob.f:594-595`, the compression adds heat to the gas:

```
CPDH = FLMS×(TCS + 273.15)×1.8×10⁻⁶×1.9872×(PTV - PTS)/(XMWS(9)×PTS)
```

This represents the **compressor work** converted to enthalpy rise:

```
ΔH = (C_p × T × ΔP) / (MW × P)
```

The measured compressor work (line 698-699):

```
XMEAS(20) = CPDH × 0.29307×10³  [kW]
```

#### Compressor Energy Balance

From `teprob.f:783-788`:

```
dETV/dt = HST(1)×FTM(1) + HST(2)×FTM(2) + HST(3)×FTM(3) + HST(5)×FTM(5) + HST(9)×FTM(9) - HST(6)×FTM(6)
```

---

## Thermodynamic Models

### Enthalpy Calculations

The simulation uses polynomial enthalpy models for liquid and gas phases.

#### Liquid Phase Enthalpy (TESUB1, lines 1392-1398)

```
H_i = T × (AH(i) + BH(i)×T/2 + CH(i)×T²/3) × 1.8 × MW(i)
```

Polynomial coefficients for liquid enthalpy:

| Comp | AH (×10⁶)     | BH (×10⁹)    | CH (×10¹¹)   |
|------|---------------|--------------|--------------|
| A    | 1.0           | 0.0          | 0.0          |
| B    | 1.0           | 0.0          | 0.0          |
| C    | 1.0           | 0.0          | 0.0          |
| D    | 0.960         | 8.70         | 4.81         |
| E    | 0.573         | 2.41         | 1.82         |
| F    | 0.652         | 2.18         | 1.94         |
| G    | 0.515         | 0.565        | 0.382        |
| H    | 0.471         | 0.870        | 0.262        |

#### Gas Phase Enthalpy (TESUB1, lines 1400-1407)

```
H_i = T × (AG(i) + BG(i)×T/2 + CG(i)×T²/3) × 1.8 × MW(i) + AV(i)
```

Where `AV(i)` is the heat of vaporization:

| Comp | AG (×10⁶)     | BG (×10¹⁰)   | CG (×10¹³)   | AV (×10⁶)    |
|------|---------------|--------------|--------------|--------------|
| A    | 3.411         | 7.18         | 6.0          | 1.0          |
| B    | 0.3799        | 10.8         | -3.98        | 1.0          |
| C    | 0.2491        | 0.136        | -0.393       | 1.0          |
| D    | 0.3567        | 8.51         | -3.12        | 86.7         |
| E    | 0.3463        | 8.96         | -3.27        | 160.0        |
| F    | 0.3930        | 10.2         | -3.12        | 160.0        |
| G    | 0.170         | 0.0          | 0.0          | 225.0        |
| H    | 0.150         | 0.0          | 0.0          | 209.0        |

#### Temperature from Enthalpy (TESUB2, lines 1433-1439)

Given total enthalpy H, find temperature T using Newton-Raphson iteration:

```
Iteration:
    H_test = f(T)         [calculate enthalpy at current T]
    error = H_test - H
    dH/dT = f'(T)         [derivative from TESUB3]
    T_new = T - error/(dH/dT)
Repeat until |T_new - T| < 10⁻¹²
```

### Density Calculations

From TESUB4 (lines 1498-1503), liquid density using polynomial model:

```
V = Σ X(i) × MW(i) / (AD(i) + (BD(i) + CD(i)×T)×T)
ρ = 1/V
```

Polynomial coefficients:

| Comp | AD    | BD (×10²)    | CD (×10⁴)    |
|------|-------|--------------|--------------|
| A    | 1.0   | 0.0          | 0.0          |
| B    | 1.0   | 0.0          | 0.0          |
| C    | 1.0   | 0.0          | 0.0          |
| D    | 23.3  | -7.00        | -0.2         |
| E    | 33.9  | -9.57        | -0.152       |
| F    | 32.8  | -9.95        | -0.233       |
| G    | 49.9  | -1.91        | -0.425       |
| H    | 50.5  | -5.41        | -0.150       |

---

## State Variables and Differential Equations

### State Vector Structure

The simulation has **50 state variables** organized as follows:

| States   | Variable              | Description                          |
|----------|-----------------------|--------------------------------------|
| YY(1-3)  | UCVR(1-3)             | Reactor vapor moles (A, B, C)       |
| YY(4-8)  | UCLR(4-8)             | Reactor liquid moles (D, E, F, G, H)|
| YY(9)    | ETR                   | Reactor enthalpy                    |
| YY(10-12)| UCVS(1-3)             | Separator vapor moles (A, B, C)     |
| YY(13-17)| UCLS(4-8)             | Separator liquid moles (D-H)        |
| YY(18)   | ETS                   | Separator enthalpy                  |
| YY(19-26)| UCLC(1-8)             | Stripper liquid moles (all)         |
| YY(27)   | ETC                   | Stripper enthalpy                   |
| YY(28-35)| UCVV(1-8)             | Compressor vapor moles (all)        |
| YY(36)   | ETV                   | Compressor enthalpy                 |
| YY(37)   | TWR                   | Reactor cooling water temp          |
| YY(38)   | TWS                   | Separator cooling water temp        |
| YY(39-50)| VPOS(1-12)            | Valve positions (manipulated vars)  |

### Complete Set of Differential Equations

From `teprob.f:762-806`:

#### Material Balances

```
Reactor vapor (i=1 to 8):
  dYY(i)/dt = FCM(i,7) - FCM(i,8) + CRXR(i)

Separator liquid (i=1 to 8):
  dYY(i+9)/dt = FCM(i,8) - FCM(i,9) - FCM(i,10) - FCM(i,11)

Stripper liquid (i=1 to 8):
  dYY(i+18)/dt = FCM(i,12) - FCM(i,13)

Compressor vapor (i=1 to 8):
  dYY(i+27)/dt = FCM(i,1) + FCM(i,2) + FCM(i,3) + FCM(i,5) + FCM(i,9) - FCM(i,6)
```

#### Energy Balances

```
Reactor:
  dYY(9)/dt = HST(7)×FTM(7) - HST(8)×FTM(8) + RH + QUR

Separator:
  dYY(18)/dt = HST(8)×FTM(8) - HST(9)×FTM(9) - HST(10)×FTM(10) - HST(11)×FTM(11) + QUS

Stripper:
  dYY(27)/dt = HST(4)×FTM(4) + HST(11)×FTM(11) - HST(5)×FTM(5) - HST(13)×FTM(13) + QUC

Compressor:
  dYY(36)/dt = HST(1)×FTM(1) + HST(2)×FTM(2) + HST(3)×FTM(3) + HST(5)×FTM(5) + HST(9)×FTM(9) - HST(6)×FTM(6)
```

#### Cooling Water Temperatures

```
Reactor cooling water:
  dYY(37)/dt = (FWR×500.53×(TCWR - TWR) - QUR×10⁶/1.8) / HWR

Separator cooling water:
  dYY(38)/dt = (FWS×500.53×(TCWS - TWS) - QUS×10⁶/1.8) / HWS
```

#### Valve Position Dynamics

From `teprob.f:799-806`:

```
For i = 1 to 12:
  dYY(i+38)/dt = (VCV(i) - VPOS(i)) / VTAU(i)
```

Where:
- `VCV(i)` = Desired valve position (from controller/XMV)
- `VPOS(i)` = Actual valve position (state)
- `VTAU(i)` = Valve time constant

Time constants (hours):
| Valve | VTAU (sec) | VTAU (hr)    |
|-------|------------|--------------|
| 1-2   | 8          | 0.00222      |
| 3     | 6          | 0.00167      |
| 4     | 9          | 0.00250      |
| 5     | 7          | 0.00194      |
| 6-8   | 5          | 0.00139      |
| 9     | 120        | 0.0333       |
| 10-12 | 5          | 0.00139      |

**Valve dynamics** represent first-order lag: actual position exponentially approaches desired position.

---

## Measurements and Control

### Manipulated Variables (Control Inputs)

12 manipulated variables control the process:

| XMV   | Description                        | Range      |
|-------|------------------------------------|------------|
| XMV(1)| D Feed Flow (stream 2)            | 0-400      |
| XMV(2)| E Feed Flow (stream 3)            | 0-400      |
| XMV(3)| A Feed Flow (stream 1)            | 0-100      |
| XMV(4)| A and C Feed Flow (stream 4)      | 0-1500     |
| XMV(5)| Compressor Recycle Valve          | 0-100%     |
| XMV(6)| Purge Valve (stream 9)            | 0-100%     |
| XMV(7)| Separator Pot Liquid Flow         | 0-1500     |
| XMV(8)| Stripper Liquid Product Flow      | 0-1000     |
| XMV(9)| Stripper Steam Valve              | 0-0.03     |
| XMV(10)| Reactor Cooling Water Flow       | 0-1000     |
| XMV(11)| Condenser Cooling Water Flow     | 0-1200     |
| XMV(12)| Agitator Speed                   | -50 to 50  |

### Measured Variables

41 measurements available (some with noise, some sampled):

#### Continuous Measurements (XMEAS 1-22)

From `teprob.f:679-701`:

```
XMEAS(1) = FTM(3) × 0.359/35.3145                [A Feed, kscmh]
XMEAS(2) = FTM(1) × XMWS(1) × 0.454              [D Feed, kg/hr]
XMEAS(3) = FTM(2) × XMWS(2) × 0.454              [E Feed, kg/hr]
XMEAS(4) = FTM(4) × 0.359/35.3145                [A&C Feed, kscmh]
XMEAS(5) = FTM(9) × 0.359/35.3145                [Recycle Flow, kscmh]
XMEAS(6) = FTM(6) × 0.359/35.3145                [Reactor Feed Rate, kscmh]
XMEAS(7) = (PTR - 760)/760 × 101.325             [Reactor Pressure, kPa gauge]
XMEAS(8) = (VLR - 84.6)/666.7 × 100              [Reactor Level, %]
XMEAS(9) = TCR                                   [Reactor Temperature, °C]
XMEAS(10) = FTM(10) × 0.359/35.3145              [Purge Rate, kscmh]
XMEAS(11) = TCS                                  [Product Sep Temp, °C]
XMEAS(12) = (VLS - 27.5)/290 × 100               [Product Sep Level, %]
XMEAS(13) = (PTS - 760)/760 × 101.325            [Prod Sep Pressure, kPa gauge]
XMEAS(14) = FTM(11)/DLS/35.3145                  [Prod Sep Underflow, m³/hr]
XMEAS(15) = (VLC - 78.25)/VTC × 100              [Stripper Level, %]
XMEAS(16) = (PTV - 760)/760 × 101.325            [Stripper Pressure, kPa gauge]
XMEAS(17) = FTM(13)/DLC/35.3145                  [Stripper Underflow, m³/hr]
XMEAS(18) = TCC                                  [Stripper Temperature, °C]
XMEAS(19) = QUC × 1.04×10³ × 0.454               [Stripper Steam Flow, kg/hr]
XMEAS(20) = CPDH × 0.29307×10³                   [Compressor Work, kW]
XMEAS(21) = TWR                                  [Reactor CW Outlet Temp, °C]
XMEAS(22) = TWS                                  [Separator CW Outlet Temp, °C]
```

#### Sampled Composition Measurements (XMEAS 23-41)

**Reactor Feed Analysis (Stream 6)** - Sampled every 0.1 hr, 0.1 hr dead time:

```
XMEAS(23-28) = XST(1-6, 7) × 100    [Components A-F, mole %]
```

**Purge Gas Analysis (Stream 9)** - Sampled every 0.1 hr, 0.1 hr dead time:

```
XMEAS(29-36) = XST(1-8, 10) × 100   [Components A-H, mole %]
```

**Product Analysis (Stream 11)** - Sampled every 0.25 hr, 0.25 hr dead time:

```
XMEAS(37-41) = XST(4-8, 13) × 100   [Components D, E, F, G, H, mole %]
```

### Measurement Noise

From `teprob.f:712-715` and `1256-1296`:

Random Gaussian noise is added to each measurement using TESUB6:

```
XMEAS(i) = XMEAS(i) + Gaussian(0, XNS(i))
```

Standard deviations (XNS):

| Measurement      | Std Dev    | Measurement         | Std Dev  |
|------------------|------------|---------------------|----------|
| XMEAS(1)         | 0.0012     | XMEAS(12)           | 1.0      |
| XMEAS(2)         | 18.0       | XMEAS(13)           | 0.30     |
| XMEAS(3)         | 22.0       | XMEAS(14)           | 0.125    |
| XMEAS(4)         | 0.05       | XMEAS(15)           | 1.0      |
| XMEAS(5)         | 0.20       | XMEAS(16)           | 0.30     |
| XMEAS(6)         | 0.21       | XMEAS(17)           | 0.115    |
| XMEAS(7)         | 0.30       | XMEAS(18)           | 0.01     |
| XMEAS(8)         | 0.50       | XMEAS(19)           | 1.15     |
| XMEAS(9)         | 0.01       | XMEAS(20)           | 0.20     |
| XMEAS(10)        | 0.0017     | XMEAS(21-22)        | 0.01     |
| XMEAS(11)        | 0.01       | XMEAS(23-36)        | 0.05-0.25|
|                  |            | XMEAS(37-41)        | 0.01-0.50|

---

## Process Disturbances

The simulation includes 20 programmed disturbances (IDV array) to test control systems.

### Disturbance Types

From the documentation and code:

| IDV   | Description                                      | Type              |
|-------|--------------------------------------------------|-------------------|
| IDV(1)| A/C Feed Ratio (Stream 4)                       | Step              |
| IDV(2)| B Composition (Stream 4)                        | Step              |
| IDV(3)| D Feed Temperature (Stream 2)                   | Step              |
| IDV(4)| Reactor Cooling Water Inlet Temperature         | Step              |
| IDV(5)| Condenser Cooling Water Inlet Temperature       | Step              |
| IDV(6)| A Feed Loss (Stream 1)                          | Step              |
| IDV(7)| C Header Pressure Loss (Stream 4)               | Step              |
| IDV(8)| A, B, C Feed Composition (Stream 4)             | Random Variation  |
| IDV(9)| D Feed Temperature (Stream 2)                   | Random Variation  |
| IDV(10)| C Feed Temperature (Stream 4)                  | Random Variation  |
| IDV(11)| Reactor Cooling Water Inlet Temperature        | Random Variation  |
| IDV(12)| Condenser Cooling Water Inlet Temperature      | Random Variation  |
| IDV(13)| Reaction Kinetics                              | Slow Drift        |
| IDV(14)| Reactor Cooling Water Valve                    | Sticking          |
| IDV(15)| Condenser Cooling Water Valve                  | Sticking          |
| IDV(16-20)| Unknown                                     | Unknown           |

### Disturbance Implementation

From `teprob.f:407-416`, step disturbances modify feed conditions:

```fortran
XST(1,4) = TESUB8(1,TIME) - IDV(1)×0.03 - IDV(2)×2.43719×10⁻³
XST(2,4) = TESUB8(2,TIME) + IDV(2)×0.005
XST(3,4) = 1.0 - XST(1,4) - XST(2,4)
TST(1) = TESUB8(3,TIME) + IDV(3)×5.0
TST(4) = TESUB8(4,TIME)
TCWR = TESUB8(5,TIME) + IDV(4)×5.0
TCWS = TESUB8(6,TIME) + IDV(5)×5.0
```

**IDV(1):** Shifts A/C ratio in stream 4 by -0.03 (reduces A)
**IDV(2):** Increases B by 0.005, reduces A slightly
**IDV(3):** Increases D feed temperature by 5°C
**IDV(4-5):** Increase cooling water inlet temperatures by 5°C

**IDV(6)** (line 567): Reduces A feed by 100%:
```fortran
FTM(3) = VPOS(3) × (1 - IDV(6)) × VRNG(3)/100
```

**IDV(7)** (line 568): Reduces stream 4 by 20%:
```fortran
FTM(4) = VPOS(4) × (1 - IDV(7)×0.2) × VRNG(4)/100
```

### Random Walk Disturbances (IDV 8-13)

From `teprob.f:340-396`, these use cubic Hermite interpolation for smooth random variations.

The TESUB5 subroutine generates smooth random walks using:

```
S(t) = A + B×t + C×t² + D×t³
```

Where coefficients are updated at random intervals to create continuous, smooth disturbances.

### Valve Sticking (IDV 14-15)

From `teprob.f:793-806`:

```fortran
If |VCV(i) - XMV(i)| > VST(i)×IVST(i):
    VCV(i) = XMV(i)
```

When IDV(14) or IDV(15) is active:
- `VST(i) = 2.0%`
- Valve won't respond to small changes (< 2%)
- Creates "sticking" behavior

---

## Summary

The Tennessee Eastman process simulation is a comprehensive dynamic model featuring:

1. **Chemical reactions**: Four gas-phase reactions with Arrhenius kinetics and pressure dependencies

2. **Unit operations**:
   - Exothermic reactor with cooling
   - Vapor-liquid separator
   - Steam-heated stripper
   - Recycle compressor

3. **Thermodynamics**:
   - Polynomial enthalpy models
   - Antoine vapor pressure equations
   - Ideal gas law for gas phase
   - Raoult's law for vapor-liquid equilibrium

4. **Dynamics**: 50 differential equations governing:
   - Material balances (40 component mole equations)
   - Energy balances (6 enthalpy equations)
   - Heat transfer (2 cooling water temperatures)
   - Valve dynamics (12 first-order lags)

5. **Instrumentation**:
   - 12 manipulated variables (valves, flows)
   - 41 measurements (22 continuous + 19 sampled)
   - Realistic measurement noise and delays

6. **Disturbances**: 20 programmed faults including steps, random variations, drifts, and valve sticking

This makes it an excellent benchmark for testing:
- Advanced process control strategies
- Fault detection and diagnosis methods
- Data-driven monitoring techniques (PCA, PLS, etc.)

---

## References

1. J.J. Downs and E.F. Vogel, "A plant-wide industrial process control problem", *Computers and Chemical Engineering*, Vol. 17, No. 3, pp. 245-255 (1993).

2. E.L. Russell, L.H. Chiang, and R.D. Braatz, *Data-driven Techniques for Fault Detection and Diagnosis in Chemical Processes*, Springer-Verlag, London, 2000.

3. L.H. Chiang, E.L. Russell, and R.D. Braatz, *Fault Detection and Diagnosis in Industrial Systems*, Springer-Verlag, London, 2001.

---

**Report compiled from:** `teprob.f` (Tennessee Eastman Process simulation code)
**Generated:** 2026-01-27
