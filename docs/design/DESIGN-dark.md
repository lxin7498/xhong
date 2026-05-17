---
name: Technical Precision
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
  on-surface-variant: '#3c4a42'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#6c7a71'
  outline-variant: '#bbcabf'
  surface-tint: '#006c49'
  primary: '#006c49'
  on-primary: '#ffffff'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#4edea3'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#a43a3a'
  on-tertiary: '#ffffff'
  tertiary-container: '#fc7c78'
  on-tertiary-container: '#711419'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#ffdad7'
  tertiary-fixed-dim: '#ffb3af'
  on-tertiary-fixed: '#410005'
  on-tertiary-fixed-variant: '#842225'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  display:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h1:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h2:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
  h3:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '500'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  meta-mono:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
    letterSpacing: 0.02em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  unit: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  xxl: 64px
  gutter: 24px
  margin: 32px
---

## Brand & Style

This design system is engineered for high-performance environments where clarity and technical sophistication are paramount. The aesthetic targets an elite "Tech Professional" demographic, blending the rigorous clarity of academic journals with the cutting-edge feel of modern laboratory software.

The style is defined as **Minimalist Layered Depth**. It avoids heavy ornamentation in favor of structural integrity, using light-on-light layering and surgical color application to guide the eye. The emotional response is one of calm authority, precision, and high-value investment. Every pixel serves a functional purpose, evoking a sense of expensive, purpose-built hardware.

## Colors

The palette is strictly curated to maintain an atmosphere of pristine focus. 
- **Base Surface:** Pure White (#FFFFFF) is the bedrock of the UI, used for the primary canvas to maximize perceived brightness and cleanliness.
- **Layering Tones:** Ultra-light grays (#F8FAFC and #F1F5F9) provide structural depth, separating sidebar navigation, tool panels, and nested containers without introducing heavy visual weight.
- **Action & Status:** Emerald Green (#10B981) is the sole vibrant accent. It is reserved for high-intent primary actions, critical success states, and active connectivity indicators.
- **Ink:** Deep slate tones are used for typography to ensure maximum legibility while appearing softer and more "premium" than pure black.

## Typography

The typographic hierarchy utilizes a dual-font strategy to balance character with utility.
- **Space Grotesk** is used for all headlines and UI labels to provide a geometric, technical "engine" feel. Its unique apertures add an academic, futuristic flair.
- **Inter** is utilized for body copy and long-form data reading due to its exceptional legibility and neutral performance.
- **System Metadata:** Use the Monospaced variant of Space Grotesk (or a supporting mono font) strictly for IDs, timestamps, coordinates, and code snippets.
- **Formatting:** Keep line lengths for body text between 60-75 characters to maintain a high-end editorial feel.

## Layout & Spacing

This design system employs a **Fixed-Fluid Hybrid Grid**. Core content areas adhere to a 12-column grid for structural consistency, while utility panels and sidebars use fixed-width dimensions to maximize the workspace for technical data.

- **Rhythm:** A 4px baseline grid ensures mathematical precision in vertical rhythm.
- **Density:** High information density is encouraged, but must be balanced by generous outer margins (32px+) to maintain the "premium" feel.
- **Gutters:** Standard 24px gutters provide clear air between data modules, preventing the UI from feeling cramped.

## Elevation & Depth

Depth is conveyed through a "Light-on-Light" layering philosophy. Instead of heavy shadows, hierarchy is established through subtle tonal shifts and stacking.

- **The Base:** Background is #FFFFFF.
- **Tier 1 (Surface):** Secondary containers (like sidebars or cards) use #F8FAFC with a 1px border of #E2E8F0.
- **Tier 2 (Floating):** Modals, dropdowns, and context menus use #FFFFFF but include a `backdrop-blur(12px)` and a very soft, diffused shadow: `0 4px 20px -2px rgba(0, 0, 0, 0.05)`.
- **Borders:** Every container must have a 1px solid border. Use #F1F5F9 for subtle separation and #E2E8F0 for more distinct boundaries.

## Shapes

The shape language focuses on "Soft Precision." Elements are neither aggressively sharp nor overly playful.
- **Standard Radius:** 8px (rounded-md) for most buttons, inputs, and small containers.
- **Container Radius:** 12px (rounded-lg) for larger cards, modals, and primary dashboard modules.
- **Symmetry:** Ensure all nested elements have a concentric radius (e.g., if a container has a 12px radius and 8px padding, the inner element should have a 4px radius).

## Components

- **Buttons:** 
    - *Primary:* Emerald Green background with White text. Use sparingly.
    - *Secondary:* White background with 1px #E2E8F0 border and Slate text.
    - *Tertiary:* Ghost style with no border, becoming #F8FAFC on hover.
- **Input Fields:** Use #F8FAFC background with a 1px bottom border for an academic, "fill-in-the-blank" feel, or a full subtle border for high-density forms. Use the Mono font for numerical inputs.
- **Chips/Badges:** Small, 4px radius. Use ultra-light fills (e.g., Emerald Green at 10% opacity) with high-contrast text for status indicators.
- **Lists:** Use 1px #F1F5F9 horizontal dividers. Ensure high vertical padding (12px-16px) to maintain the premium, spacious feel.
- **Floating Elements:** Use a semi-transparent White (#FFFFFFCC) with a backdrop blur for navigation bars or floating action panels to emphasize the layered depth.
- **Data Tables:** Pure white headers with a sticky #F8FAFC background. Use Mono fonts for all numeric data columns to ensure alignment and readability.