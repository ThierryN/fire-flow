---
name: {{SKILL_NAME}}
category: {{CATEGORY}}
type: ui-component
version: 1.0.0
contributed: {{DATE}}
contributor: {{PROJECT}}
last_updated: {{DATE}}
tags: [{{TAGS}}]
difficulty: {{DIFFICULTY}}
usage_count: 0
success_rate: 100
---

# {{TITLE}}

## Problem

[What UI/UX challenge does this component pattern solve?]

**User Impact:**
[How the user experience suffers without this pattern]

## Visual Reference

```
+----------------------------------+
|  [ASCII wireframe of component]  |
|                                  |
|  [Show key interactive states]   |
+----------------------------------+
```

## Solution Pattern

### Component Structure

```{{LANGUAGE}}
{{COMPONENT_CODE}}
```

### Styling

```{{LANGUAGE}}
{{STYLING_CODE}}
```

### State Management

```{{LANGUAGE}}
{{STATE_CODE}}
```

## Accessibility

- [ ] Keyboard navigation: [Tab, Enter, Escape behavior]
- [ ] Screen reader: [ARIA roles and labels]
- [ ] Focus management: [Focus trap, return focus]
- [ ] Color contrast: [WCAG AA minimum]
- [ ] Reduced motion: [prefers-reduced-motion handling]

```{{LANGUAGE}}
// Accessibility implementation
{{A11Y_CODE}}
```

## Responsive Behavior

| Breakpoint | Behavior |
|-----------|----------|
| Mobile (<640px) | [Description] |
| Tablet (640-1024px) | [Description] |
| Desktop (>1024px) | [Description] |

## Props / API

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `string` | `'default'` | [Description] |
| `size` | `string` | `'md'` | [Description] |
| `onAction` | `function` | - | [Description] |

## Usage Example

```{{LANGUAGE}}
// Basic usage
{{BASIC_USAGE}}

// Advanced usage with all props
{{ADVANCED_USAGE}}
```

## Common Mistakes

1. **[Mistake 1]** - [Correct approach]
2. **[Mistake 2]** - [Correct approach]

## When to Use

- [Scenario 1]
- [Scenario 2]

## When NOT to Use

- [Use alternative-component instead when...]

## Related Skills

- [related-skill] - [description]

## References

- Contributed from: {{PROJECT}}
