---
name: Emerald Code
colors:
  surface: '#0b1326'
  surface-dim: '#0b1326'
  surface-bright: '#31394d'
  surface-container-lowest: '#060e20'
  surface-container-low: '#131b2e'
  surface-container: '#171f33'
  surface-container-high: '#222a3d'
  surface-container-highest: '#2d3449'
  on-surface: '#dae2fd'
  on-surface-variant: '#bbcabf'
  inverse-surface: '#dae2fd'
  inverse-on-surface: '#283044'
  outline: '#86948a'
  outline-variant: '#3c4a42'
  surface-tint: '#4edea3'
  primary: '#4edea3'
  on-primary: '#003824'
  primary-container: '#10b981'
  on-primary-container: '#00422b'
  inverse-primary: '#006c49'
  secondary: '#45dfa4'
  on-secondary: '#003825'
  secondary-container: '#00bd85'
  on-secondary-container: '#00452e'
  tertiary: '#68dba9'
  on-tertiary: '#003825'
  tertiary-container: '#3eb686'
  on-tertiary-container: '#00422c'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#6ffbbe'
  primary-fixed-dim: '#4edea3'
  on-primary-fixed: '#002113'
  on-primary-fixed-variant: '#005236'
  secondary-fixed: '#68fcbf'
  secondary-fixed-dim: '#45dfa4'
  on-secondary-fixed: '#002114'
  on-secondary-fixed-variant: '#005137'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#0b1326'
  on-background: '#dae2fd'
  surface-variant: '#2d3449'
typography:
  h1:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  h2:
    fontFamily: Space Grotesk
    fontSize: 36px
    fontWeight: '600'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  h3:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.3'
    letterSpacing: -0.01em
  body-lg:
    fontFamily: Space Grotesk
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  body-md:
    fontFamily: Space Grotesk
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
    letterSpacing: '0'
  code:
    fontFamily: Space Grotesk
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1.5'
    letterSpacing: '0'
  label-sm:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin: 32px
---

## Brand & Style
The brand personality for this design system is intellectually rigorous, futuristic, and highly efficient. It is designed for developers and computer science students who value precision and clarity. The emotional response should be one of "controlled immersion"—a focused state where the UI recedes to highlight complex information, while vibrant accents provide clear feedback and motivation.

The design style is a hybrid of **Minimalism** and **Glassmorphism**. It utilizes a "Terminal-Plus" aesthetic: the dark, high-contrast foundations of a code editor combined with sophisticated translucent layers and subtle glow effects that signify modern, high-end software.

## Colors
The palette is rooted in a deep, nocturnal base to minimize eye strain during long coding sessions. The primary Emerald Green (#10B981) acts as the "source of truth," used for primary actions, progress indicators, and success states. 

- **Primary Emerald:** High-vibrancy green for high-priority interactive elements.
- **Surface Neutrals:** A range of deep slates used to differentiate between the background, sidebar, and content containers.
- **Accents:** Use a 10% opacity Emerald tint for subtle backgrounds on active items to maintain a cohesive "tech glow."

## Typography
This design system exclusively uses **Space Grotesk**. Its geometric construction and technical quirks—like the distinct glyph shapes—align perfectly with a computer science context.

Headlines should be tightly tracked to emphasize the font's bold, futuristic character. Body text is set with generous line height to ensure readability of technical documentation. For code snippets within this design system, use the medium weight of Space Grotesk to maintain the brand aesthetic while ensuring character distinction.

## Layout & Spacing
The layout follows a **12-column fluid grid** for dashboard views and a **fixed-center column (800px)** for reading-heavy documentation or lessons. 

A strict 8px base-unit system governs all spatial relationships. Use 24px gutters for standard component spacing and 48px-80px for vertical section breathing room. Layouts should prioritize information density in IDE-like views, but use wider margins in "Learning Modes" to reduce cognitive load.

## Elevation & Depth
Depth is conveyed through **Tonal Layers** and **Backdrop Blurs**. 

1.  **Background (Level 0):** #020617 (Deepest).
2.  **Surface (Level 1):** #0F172A (Navigation sidebars, inactive cards).
3.  **Raised (Level 2):** #1E293B (Active modals, popovers).

Instead of traditional shadows, use 1px solid borders in a slightly lighter slate (#334155) for structure. For "Active" or "Focused" states, apply an outer glow using the Primary Emerald with a 20px blur at 15% opacity to simulate a light-emitting screen effect.

## Shapes
This design system utilizes a **Soft (Level 1)** roundedness approach. A 4px (0.25rem) radius is the standard for most components, providing a professional, engineered feel without being overly aggressive. 

Larger containers like cards or lesson modules may use a 12px (0.75rem) radius to feel more approachable. Interactive elements like buttons and input fields must remain consistent at the base 4px radius to reinforce the technical, modular nature of the platform.

## Components
- **Buttons:** Primary buttons are solid Emerald Green with black text. Secondary buttons use a ghost style with an Emerald border and text. All buttons feature a 200ms transition on hover, where the primary button gains a soft green outer glow.
- **Input Fields:** Use a dark slate fill with a subtle 1px border. On focus, the border transitions to Emerald Green, and the label (using `label-sm`) shifts color to match.
- **Code Blocks:** Styled to look like a terminal window with a header bar containing "traffic light" window controls. The background is a slightly darker shade than the surrounding surface to create an inset look.
- **Chips/Tags:** Used for programming languages (e.g., Python, C++). Use a low-opacity Emerald background with Emerald text to signify categories.
- **Progress Bars:** Thin 4px tracks with a glowing Emerald fill. For completion states, the entire track should pulse slightly.
- **Cards:** Use Level 1 surfaces with no shadows; use a 1px border to define the edge. When hovered, the border color should brighten from a muted slate to the primary emerald.