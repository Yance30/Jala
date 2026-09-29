---
name: Precision Graph & Forensic Intelligence
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#3e4947'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#6e7977'
  outline-variant: '#bdc9c6'
  surface-tint: '#006a63'
  primary: '#005c55'
  on-primary: '#ffffff'
  primary-container: '#0f766e'
  on-primary-container: '#a3faef'
  inverse-primary: '#80d5cb'
  secondary: '#4c6453'
  on-secondary: '#ffffff'
  secondary-container: '#cbe6d1'
  on-secondary-container: '#506857'
  tertiary: '#893a00'
  on-tertiary: '#ffffff'
  tertiary-container: '#af4c00'
  on-tertiary-container: '#ffe6da'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#9cf2e8'
  primary-fixed-dim: '#80d5cb'
  on-primary-fixed: '#00201d'
  on-primary-fixed-variant: '#00504a'
  secondary-fixed: '#cee9d4'
  secondary-fixed-dim: '#b2cdb8'
  on-secondary-fixed: '#082013'
  on-secondary-fixed-variant: '#344c3c'
  tertiary-fixed: '#ffdbca'
  tertiary-fixed-dim: '#ffb690'
  on-tertiary-fixed: '#341100'
  on-tertiary-fixed-variant: '#783200'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display-xl:
    fontFamily: Inter
    fontSize: 40px
    fontWeight: '600'
    lineHeight: 48px
    letterSpacing: -0.03em
  display-xl-mobile:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.025em
  headline-lg:
    fontFamily: Inter
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.015em
  headline-sm:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
    letterSpacing: -0.005em
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
    letterSpacing: 0em
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
    letterSpacing: 0.005em
  label-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.01em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.04em
  numeric-data:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: -0.01em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1.25rem
  gutter-desktop: 1.5rem
  margin: 1rem
  margin-desktop: 2rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1.25rem
  space-xl: 2rem
---

## Brand & Style

The design system embodies forensic clarity, institutional trust, and analytical speed. Designed specifically for internal fraud auditors and data scientists scrutinizing high-volume healthcare claims across complex actor networks, it rejects bureaucratic visual clutter in favor of a hyper-focused, modern fintech atmosphere influenced by Linear’s density and Notion’s systematic restraint.

### Design Movement
**Minimalist Institutional Modernism.** The aesthetic merges structural precision with modern SaaS utility:
- **Purity over Ornamentation:** Surfaces are stark, bright, and deliberate. High-contrast dark green typography replaces harsh pure black to evoke institutional authority with an organic, discerning undertone.
- **Data-First Hierarchy:** Visual weight is governed strictly by urgency and evidentiary significance. Neutral information recedes; anomalies, network ties, and fraud scores claim instant focus.
- **Calm Authority:** Eliminates anxiety typically found in surveillance or audit tooling, replacing it with an objective, surgical workspace.

## Colors

The system uses a tightly controlled chromatic structure to avoid visual fatigue over prolonged investigative sessions:

- **Primary Accent (`#0F766E` - Deep Teal):** The operational core. Used for active navigation states, primary action buttons, key metrics, interactive nodes in entity resolution graphs, and validated states.
- **Secondary / Deep Core (`#132A1C` - Dark Forest Pine):** Replaces pure black (`#000000`) for headers, primary typography, brand anchors, and structural contrast. It introduces clinical depth without screen glare.
- **Tertiary Accent (`#F97316` - Forensic Amber/Orange):** Reserved strictly for multi-actor fraud vectors, high-risk flags, outlier anomalies, and collision alerts. Never used decoratively.
- **Neutral & Canvas (`#FFFFFF` & `#F8FAFC`):** The primary canvas is absolute crisp white (`#FFFFFF`), supported by warm-gray/slate container surfaces (`#F8FAFC` to `#F1F5F9`) and micro-borders (`#E2E8F0`).

### Semantic Color Rules
- **Structural Text:** 
  - Primary: `#132A1C` (Dark Forest Pine)
  - Secondary: `#475569` (Slate Gray)
  - Muted/De-emphasized: `#94A3B8` (Soft Chrome)
- **Fraud Severity:**
  - Standard/Normal: `#0F766E` (Deep Teal pill badge)
  - Suspicious/Collusion: `#F97316` (Forensic Orange pill badge)
  - Critical/Flagged: `#DC2626` (Red - reserved solely for confirmed fraud triggers)

## Typography

The type system prioritizes micro-legibility and horizontal efficiency. Built entirely on **Inter**, it leverages tabular numbers (`tnum`) across all claims tables, patient-provider ratios, and currency amounts (IDR).

- **Headings:** Set in tight, negative letter spacing (`-0.015em` to `-0.03em`) and medium/semibold weights to anchor dashboard views without overpowering tabular data.
- **Numbers & Metrics:** Must enforce `font-feature-settings: "tnum", "cv02", "cv03", "cv04"` to ensure perfect vertical alignment across ledger matrices and multi-actor transaction graphs.
- **Metadata and Badges:** Rendered in small, slightly tracked upper-case or title-case semibold (`label-sm`), providing instant legibility at microscopic scales.

## Layout & Spacing

The layout model relies on a dense, utilitarian grid system with dynamic desktop sidebars and responsive main panels:

- **Desktop (>= 1280px):** 12-column dynamic fluid grid. Left-hand collapsible investigation navigation rail (64px collapsed, 240px expanded), central workspace spanning 8 to 10 columns, with an optional 3-to-4 column contextual triage drawer. Outer margins are locked at `2rem`, gutters at `1.5rem`.
- **Tablet (768px - 1279px):** 8-column layout. Gutters scale down to `1.25rem`, outer margins to `1.5rem`. Side-by-side claim comparison automatically cascades into vertically stacked panels.
- **Mobile (< 768px):** 4-column layout with fixed `1rem` outer canvas padding. Tables convert to swipeable, card-based audit summaries with collapsed forensic metrics.
- **Rhythm:** Spacing follows an intentional 4px/8px baseline. Inner component elements maintain compact padding (`space-xs` and `space-sm`) to support high information density, while macro sections breathe with `space-xl` separation.

## Elevation & Depth

This design system uses a **low-contrast outline and micro-ambient shadow approach** to maintain a crisp, distraction-free environment:

- **Surface Tiers:**
  - `Base`: Absolute Pure White (`#FFFFFF`).
  - `Container Tier 1 (Cards, Tables)`: Off-white canvas (`#FFFFFF`) with a 1px crisp outline in `#E2E8F0`.
  - `Container Tier 2 (Panels, Inspect Drawers)`: Light muted tint (`#F8FAFC`) framed by `#CBD5E1`.
- **Shadow System:**
  - **Flat State (Cards, static panels):** `0 0 0 1px #E2E8F0` (No shadow blur, pure structural border).
  - **Interactive Hover (Selectable claims, graph nodes):** `0 2px 4px -1px rgba(19, 42, 28, 0.04), 0 0 0 1px #CBD5E1`.
  - **Overlays (Modals, popovers, actor context cards):** `0 10px 25px -5px rgba(19, 42, 28, 0.08), 0 0 0 1px #E2E8F0`.
- **Restraint:** Drop shadows are strictly tinted with the dark secondary tone (`#132A1C`) at very low opacities (4%–8%), preventing muddy, grey artifacts and preserving clinical crispness.

## Shapes

The geometric identity is clean, controlled, and intentionally quiet:
- **Base Level (`roundedness: 1`):** Core interactive components (inputs, list items, table rows, button elements) feature a refined `0.25rem` (4px) corner radius.
- **Structural Containers (`rounded-lg`):** Analytical panels, fraud relationship maps, and data cards utilize `0.5rem` (8px) corners to balance softness and modular rigidity.
- **Status & Badges (Pill Shape):** Actor identifiers, status flags, and classification tags break the rectangular structure with complete rounded pill profiles (`9999px`), drawing immediate peripheral attention to categorical data.

## Components

### 1. Buttons
- **Primary:** Background `#0F766E`, text `#FFFFFF`, border `transparent`, subtle hover `#0D6861`. Focus ring is 2px `#0F766E` offset by 2px white.
- **Secondary:** Background `#FFFFFF`, text `#132A1C`, 1px border `#E2E8F0`, hover background `#F8FAFC`.
- **Tertiary / Forensic Trigger:** Background `#F97316`, text `#FFFFFF`, applied strictly to irreversible or urgent audit escalations (e.g., "Freeze Provider Claim ID").

### 2. Pill Badges & Actor Chips
- **Category Badge:** Height 22px, `roundedness: full (9999px)`, padding `2px 10px`, font `label-sm`.
  - Normal/Verified: Background `rgba(15, 118, 110, 0.08)`, text `#0F766E`, border `1px solid rgba(15, 118, 110, 0.2)`.
  - Anomalous Multi-actor Linkage: Background `rgba(249, 115, 22, 0.1)`, text `#C2410C`, border `1px solid rgba(249, 115, 22, 0.3)`.

### 3. Data Tables & Lists
- **Structure:** Clean border-bottom `#F1F5F9`, no alternating zebra stripes. Hover states produce a warm-gray wash (`#F8FAFC`).
- **Cells:** Vertical padding `8px 12px`, tabular font figures for Indonesian Rupiah amounts and claim frequencies, right-aligned for numeric comparisons.

### 4. Input Fields & Search Bars
- **Fields:** Pure white background, 1px border `#E2E8F0`, height 36px, `roundedness: 1`. Focused state shifts border to `#0F766E` with a zero-offset box shadow `0 0 0 1px #0F766E`.
- **Search:** Includes a monospaced shortcut indicator (e.g., `⌘K`) in muted slate (`#94A3B8`).

### 5. Cards & Intelligence Panels
- **Layout:** Crisp `#FFFFFF` background, 1px perimeter border `#E2E8F0`, padding `1.25rem`. 
- **Header Structure:** Small bold title in `#132A1C`, paired with a right-aligned pill badge or real-time confidence metric.

### 6. Network Node Callouts (Product-Specific)
- Used inside graph visualization canvases to represent hospitals (Faskes), doctors, and patient clusters.
- **Styling:** Micro-card with an 8px circular indicator (Teal for verified entity, Orange for multi-party collusion risk), accompanied by actor registration codes in monospaced tabular typography.