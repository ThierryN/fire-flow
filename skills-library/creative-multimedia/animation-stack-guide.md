# Web Animation Stack — Decision Guide
**Description:** Comprehensive guide for choosing and implementing web animations. Covers Motion (Framer Motion), GSAP, Lottie, and CSS-native approaches with working patterns for each.

**When to use:** Any project requiring animations beyond simple CSS transitions — page transitions, scroll effects, interactive UI, marketing pages, micro-interactions, loading states, SVG animation.

---

## Decision Tree: Which Tool for Which Job?

```
Need animation? ─┬─ Simple hover/fade/color? ──────────── CSS Transitions
                  │
                  ├─ React component enter/exit/layout? ── Motion (Framer Motion)
                  │
                  ├─ Complex timeline / scroll-driven? ──── GSAP + ScrollTrigger
                  │
                  ├─ Designer-created (After Effects)? ──── Lottie
                  │
                  └─ SVG morphing / path animation? ──────── GSAP or SMIL
```

### Quick Reference

| Tool | Best For | Bundle Size | Learning Curve |
|------|----------|-------------|----------------|
| CSS Transitions | Hover, opacity, color, simple transforms | 0 KB | Low |
| Motion (Framer Motion) | React layout animations, gestures, presence | ~32 KB gzip | Medium |
| GSAP | Timelines, scroll, SVG morph, marketing | ~24 KB core | Medium-High |
| Lottie | After Effects exports, loading states | ~50 KB (lottie-web) | Low (player) |

---

## CSS Transitions & Animations (No Library Needed)

Use CSS first. If CSS handles it, stop here.

```css
/* Transition — triggers on state change (hover, class toggle) */
.card {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.15);
}

/* Keyframe animation — runs automatically or on class addition */
@keyframes fadeSlideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.appear {
  animation: fadeSlideIn 0.5s ease-out forwards;
}

/* Staggered children with custom property */
.stagger-list > * {
  animation: fadeSlideIn 0.4s ease-out forwards;
  opacity: 0;
}
.stagger-list > *:nth-child(1) { animation-delay: 0ms; }
.stagger-list > *:nth-child(2) { animation-delay: 80ms; }
.stagger-list > *:nth-child(3) { animation-delay: 160ms; }
.stagger-list > *:nth-child(4) { animation-delay: 240ms; }
```

---

## Motion (Framer Motion) Patterns

Install: `npm install motion` (v11+) or `npm install framer-motion` (v10 and earlier)

### Basic Animation with Variants

```tsx
import { motion } from "motion/react";

const cardVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
  exit: { opacity: 0, y: -20 },
};

function Card({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      exit="exit"
      transition={{ duration: 0.4, ease: "easeOut" }}
    >
      {children}
    </motion.div>
  );
}
```

### AnimatePresence for Mount/Unmount

```tsx
import { AnimatePresence, motion } from "motion/react";

function Notification({ message, isVisible }: { message: string; isVisible: boolean }) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          key="notification"
          initial={{ opacity: 0, y: -50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: -50, scale: 0.9 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          className="notification"
        >
          {message}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

### Layout Animations (Shared Element Transitions)

```tsx
import { motion, LayoutGroup } from "motion/react";

function TabPanel({ tabs, activeTab, onSelect }) {
  return (
    <LayoutGroup>
      <div className="tab-bar">
        {tabs.map((tab) => (
          <button key={tab.id} onClick={() => onSelect(tab.id)} className="tab">
            {tab.label}
            {activeTab === tab.id && (
              <motion.div
                layoutId="active-tab-indicator"
                className="tab-indicator"
                transition={{ type: "spring", stiffness: 400, damping: 30 }}
              />
            )}
          </button>
        ))}
      </div>
    </LayoutGroup>
  );
}
```

### Gesture Animations (Drag, Hover, Tap)

```tsx
function DraggableCard() {
  return (
    <motion.div
      drag
      dragConstraints={{ left: -100, right: 100, top: -50, bottom: 50 }}
      dragElastic={0.2}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      whileDrag={{ boxShadow: "0 20px 40px rgba(0,0,0,0.3)" }}
      className="draggable-card"
    >
      Drag me
    </motion.div>
  );
}
```

### Scroll-Linked Animations

```tsx
import { motion, useScroll, useTransform } from "motion/react";

function ParallaxHero() {
  const { scrollYProgress } = useScroll();

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 0.5], [1, 0.8]);

  return (
    <motion.div style={{ y, opacity, scale }} className="hero">
      <h1>Parallax Hero</h1>
    </motion.div>
  );
}
```

### Stagger Children Pattern

```tsx
const containerVariants = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.2,
    },
  },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0 },
};

function StaggerList({ items }: { items: string[] }) {
  return (
    <motion.ul variants={containerVariants} initial="hidden" animate="visible">
      {items.map((item) => (
        <motion.li key={item} variants={itemVariants}>
          {item}
        </motion.li>
      ))}
    </motion.ul>
  );
}
```

---

## GSAP Patterns

Install: `npm install gsap` (free core) or `npm install gsap@npm:@gsap/shockingly` (Club plugins)

### Basic Tweens

```ts
import gsap from "gsap";

// Animate TO a state
gsap.to(".box", { x: 200, rotation: 360, duration: 1, ease: "power2.out" });

// Animate FROM a state (element starts at these values, animates to CSS defaults)
gsap.from(".box", { opacity: 0, y: 50, duration: 0.8 });

// Animate FROM → TO explicitly
gsap.fromTo(".box",
  { opacity: 0, scale: 0.5 },
  { opacity: 1, scale: 1, duration: 0.6, ease: "back.out(1.7)" }
);
```

### Timeline for Sequenced Animations

```ts
import gsap from "gsap";

const tl = gsap.timeline({ defaults: { duration: 0.6, ease: "power2.out" } });

tl.from(".hero-title", { opacity: 0, y: 40 })
  .from(".hero-subtitle", { opacity: 0, y: 30 }, "-=0.3")   // overlap by 0.3s
  .from(".hero-cta", { opacity: 0, scale: 0.8 }, "-=0.2")
  .from(".hero-image", { opacity: 0, x: 100 }, "<");          // start at same time as previous

// Control
tl.play();
tl.pause();
tl.reverse();
tl.seek(1.5); // jump to 1.5 seconds
```

### ScrollTrigger Setup

```ts
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";

gsap.registerPlugin(ScrollTrigger);

// Fade in on scroll
gsap.from(".section", {
  scrollTrigger: {
    trigger: ".section",
    start: "top 80%",      // when top of .section hits 80% of viewport
    end: "bottom 20%",
    toggleActions: "play none none reverse", // onEnter onLeave onEnterBack onLeaveBack
    // markers: true,       // debug — remove in production
  },
  opacity: 0,
  y: 60,
  duration: 1,
});

// Pin + scrub (element sticks while scrolling drives animation)
gsap.to(".horizontal-panels", {
  xPercent: -100 * (panelCount - 1),
  ease: "none",
  scrollTrigger: {
    trigger: ".horizontal-container",
    pin: true,
    scrub: 1,             // 1 second smoothing
    snap: 1 / (panelCount - 1),
    end: () => "+=" + document.querySelector(".horizontal-container").offsetWidth,
  },
});
```

### React Integration with useGSAP Hook

```tsx
import gsap from "gsap";
import { useGSAP } from "@gsap/react";
import { useRef } from "react";

gsap.registerPlugin(useGSAP);

function AnimatedSection() {
  const containerRef = useRef<HTMLDivElement>(null);

  useGSAP(() => {
    // All GSAP animations inside here are automatically cleaned up
    gsap.from(".card", {
      y: 40,
      opacity: 0,
      stagger: 0.1,
      duration: 0.6,
      ease: "power2.out",
    });
  }, { scope: containerRef }); // scope limits querySelector to this container

  return (
    <div ref={containerRef}>
      <div className="card">Card 1</div>
      <div className="card">Card 2</div>
      <div className="card">Card 3</div>
    </div>
  );
}
```

### SplitText for Text Animations

```ts
import gsap from "gsap";
import { SplitText } from "gsap/SplitText"; // Club plugin

gsap.registerPlugin(SplitText);

const split = new SplitText(".headline", { type: "chars,words" });

gsap.from(split.chars, {
  opacity: 0,
  y: 20,
  rotateX: -90,
  stagger: 0.03,
  duration: 0.5,
  ease: "back.out(1.7)",
});
```

---

## Lottie Patterns

Install: `npm install lottie-react` (React) or `npm install lottie-web` (vanilla)

### React Component Usage

```tsx
import Lottie from "lottie-react";
import loadingAnimation from "./animations/loading.json";

function LoadingSpinner() {
  return (
    <Lottie
      animationData={loadingAnimation}
      loop={true}
      style={{ width: 120, height: 120 }}
    />
  );
}
```

### Controlled Playback

```tsx
import Lottie, { type LottieRefCurrentProps } from "lottie-react";
import { useRef } from "react";
import successAnimation from "./animations/success.json";

function SuccessCheck() {
  const lottieRef = useRef<LottieRefCurrentProps>(null);

  const handleComplete = () => {
    // Play only once, then hold on last frame
    lottieRef.current?.goToAndStop(
      lottieRef.current.getDuration(true)! - 1,
      true
    );
  };

  return (
    <Lottie
      lottieRef={lottieRef}
      animationData={successAnimation}
      loop={false}
      onComplete={handleComplete}
      style={{ width: 80, height: 80 }}
    />
  );
}
```

### Lazy-Loaded Lottie (Code Splitting)

```tsx
import { lazy, Suspense, useEffect, useState } from "react";
import Lottie from "lottie-react";

function LazyLottie({ src, ...props }: { src: string } & Record<string, unknown>) {
  const [animationData, setAnimationData] = useState(null);

  useEffect(() => {
    fetch(src)
      .then((res) => res.json())
      .then(setAnimationData);
  }, [src]);

  if (!animationData) return <div className="lottie-placeholder" />;

  return <Lottie animationData={animationData} {...props} />;
}

// Usage — JSON loaded on demand, not bundled
<LazyLottie src="/animations/onboarding.json" loop style={{ width: 200 }} />
```

### LottieFiles Marketplace Integration

```tsx
// Use DotLottie for .lottie format (smaller than JSON)
// npm install @lottiefiles/dotlottie-react

import { DotLottieReact } from "@lottiefiles/dotlottie-react";

function MarketplaceAnimation() {
  return (
    <DotLottieReact
      src="https://lottie.host/abc123/animation.lottie"
      loop
      autoplay
      style={{ width: 200, height: 200 }}
    />
  );
}
```

---

## Performance Guidelines

### The Golden Rule

Only animate properties that are GPU-composited. Everything else triggers layout or paint recalculations:

| Safe (Composited) | Unsafe (Triggers Layout/Paint) |
|---|---|
| `transform` (translate, scale, rotate) | `width`, `height`, `top`, `left` |
| `opacity` | `margin`, `padding` |
| `filter` (with caution) | `border-radius` (paint) |
| `clip-path` (paint, but fast) | `box-shadow` (paint) |

### Practical Rules

```css
/* Use will-change ONLY on elements about to animate, remove after */
.about-to-animate {
  will-change: transform, opacity;
}

/* Prefer transform over positional properties */
/* BAD */
.move { left: 100px; }
/* GOOD */
.move { transform: translateX(100px); }
```

### Reduce Layout Thrashing

```ts
// BAD — read/write interleaved forces synchronous layout
elements.forEach((el) => {
  const height = el.offsetHeight; // READ (forces layout)
  el.style.height = height * 2 + "px"; // WRITE (invalidates layout)
});

// GOOD — batch reads, then batch writes
const heights = elements.map((el) => el.offsetHeight); // all READs
elements.forEach((el, i) => {
  el.style.height = heights[i] * 2 + "px"; // all WRITEs
});
```

### Custom Animations with requestAnimationFrame

```ts
function animateValue(
  from: number,
  to: number,
  duration: number,
  onUpdate: (value: number) => void,
  onComplete?: () => void
) {
  const start = performance.now();

  function tick(now: number) {
    const elapsed = now - start;
    const progress = Math.min(elapsed / duration, 1);

    // Ease-out cubic
    const eased = 1 - Math.pow(1 - progress, 3);
    onUpdate(from + (to - from) * eased);

    if (progress < 1) {
      requestAnimationFrame(tick);
    } else {
      onComplete?.();
    }
  }

  requestAnimationFrame(tick);
}

// Usage: animate a counter from 0 to 1000 over 2 seconds
animateValue(0, 1000, 2000, (val) => {
  counterEl.textContent = Math.round(val).toLocaleString();
});
```

### Motion: Reduce Re-renders

```tsx
// Use motion values instead of React state for high-frequency updates
import { useMotionValue, useTransform, motion } from "motion/react";

function Slider() {
  const x = useMotionValue(0);
  const background = useTransform(x, [-100, 0, 100], ["#ff0000", "#ffffff", "#00ff00"]);

  // x and background update WITHOUT triggering React re-renders
  return (
    <motion.div drag="x" style={{ x, background }} dragConstraints={{ left: -100, right: 100 }}>
      Drag
    </motion.div>
  );
}
```

---

## Common Patterns Cheat Sheet

| Pattern | Tool | Key API |
|---------|------|---------|
| Page transition (React Router) | Motion | `AnimatePresence` + `motion.div` on route |
| Scroll-reveal sections | GSAP | `ScrollTrigger` with `toggleActions` |
| Shared element transition | Motion | `layoutId` on source and target |
| Infinite marquee | CSS | `@keyframes` with `translateX` |
| Loading spinner | Lottie or CSS | `lottie-react` or `@keyframes rotate` |
| Number counter | GSAP or rAF | `gsap.to()` on object prop / `requestAnimationFrame` |
| Parallax background | Motion or GSAP | `useScroll` + `useTransform` / `ScrollTrigger scrub` |
| Typing effect | GSAP | `SplitText` + stagger on chars |
| Accordion expand/collapse | Motion | `animate={{ height: "auto" }}` with `AnimatePresence` |

---

