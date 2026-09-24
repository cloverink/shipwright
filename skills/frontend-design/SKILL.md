---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces. Rejects generic AI aesthetics (purple gradients, Inter font, glassmorphism). Design direction first, then implementation.
model: opus
---

# /frontend-design

Build frontend that doesn't look like every other AI-generated UI.

## Philosophy

Most AI-generated UI converges on the same aesthetic: purple gradients, Inter font, glassmorphism cards, excessive rounded corners. This skill deliberately breaks from that pattern.

**Design direction comes first.** Before writing any code, establish:
- What mood/tone should the UI convey?
- What makes this interface distinctive?
- What's the one bold choice that sets it apart?

## Process

1. **Understand**: what is this page/component for? Who uses it? In what context?
2. **Direction**: propose 2-3 aesthetic directions (not wireframes, *moods*)
3. **Commit**: pick one direction and commit to it boldly
4. **Build**: implement with high craft quality
5. **Refine**: iterate on details (spacing, transitions, micro-interactions)

## Anti-patterns (avoid these)

- Purple/blue gradients as default accent
- Inter or system font without intention
- Glassmorphism/frosted glass on everything
- Excessive border-radius (not everything needs to be a pill)
- Drop shadows on every element
- Dark mode as the default without reason
- Generic hero sections with stock illustration style

## What good looks like

- **Intentional typography**: weight, spacing, and size serve hierarchy, not decoration
- **Restrained color**: 1-2 accent colors max, used with purpose
- **Meaningful motion**: 150-200ms micro-interactions, 500ms transitions
- **Whitespace as design element**: not filler, but rhythm
- **One bold choice**: a distinctive layout, an unusual color, a typographic statement

## Adapting to your project

<!-- CONFIGURE: Replace with your project's design system -->
```
Stack: [your framework] + [your UI library] + [your CSS approach]
Design tokens: [your color system, typography, spacing scale]
Component library: [your shared components]
```

The skill works with any stack. The principles are universal: the implementation details are yours.

## Usage

```
/frontend-design            # Start design process for a new page/component
```

Best used for greenfield UI. For wiring data, fixing bugs, or extending existing components, use a standard frontend-dev approach instead.
