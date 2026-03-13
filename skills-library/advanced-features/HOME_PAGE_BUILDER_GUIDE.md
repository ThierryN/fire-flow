# 🎨 Home Page Builder Guide

**Step-by-step guide to recreate your hardcoded home page using the Page Builder**

**Reference:** Use `HARDCODED_HOME_PAGE_BACKUP.md` for exact text content

---

## 📋 Component Mapping

Here's exactly which components to drag from the sidebar for each section:

---

## 1️⃣ Hero Section

**Component to Use:** `Hero`

**Configuration:**
```
Title: Grow in Faith
Subtitle: Through Biblical Teaching
Description: Join our community of believers in a journey of spiritual growth through authentic biblical teaching, transformative courses, and meaningful connections.

Primary Button:
  - Text: "Explore Courses"
  - Link: /courses
  - Style: Primary (dark background)

Secondary Button:
  - Text: "Learn More"
  - Link: /about
  - Style: Secondary (white background with border)
```

**Layout:** Full width, centered text

---

## 2️⃣ Spacer

**Component to Use:** `Spacer`

**Configuration:**
```
Height: Medium (or 64px)
```

This adds space between Hero and Stats sections.

---

## 3️⃣ Stats Section

**Problem:** There's no "Stats" component in your builder!

**Solution - Option 1:** Use `Text` component with custom HTML
**Solution - Option 2:** Skip this for now and ask developer to add a Stats component

**Temporary Workaround:**
1. Drag `Heading` component
2. Set text to: "500+ Active Members | 50+ Courses Available | 99% Satisfaction Rate | 24/7 Support"
3. Center align

**OR Skip this section** - It's nice to have but not critical

---

## 4️⃣ Features Section ("Why Choose Our Ministry")

**Component to Use:** `FeaturesGrid`

**Configuration:**
```
Section Heading: Why Choose Our Ministry
Section Description: Our ministry is committed to providing authentic biblical teaching that empowers believers to grow in their faith and understanding of Scripture.

Feature 1:
  - Title: Biblical Teaching
  - Description: In-depth Bible studies and courses that help you understand Scripture in its proper context and historical background.
  - Icon: 📖 (or leave blank)

Feature 2:
  - Title: Community Support
  - Description: Connect with like-minded believers for fellowship, discussion, and shared spiritual growth experiences.
  - Icon: 🤝 (or leave blank)

Feature 3:
  - Title: Spiritual Growth
  - Description: Resources designed to help you mature in your faith and develop a deeper relationship with God.
  - Icon: 🌱 (or leave blank)
```

**Layout:** 3 columns

---

## 5️⃣ Spacer

**Component to Use:** `Spacer`

**Configuration:**
```
Height: Medium
```

---

## 6️⃣ Featured Courses Section

**Problem:** No "Featured Courses" component exists!

**Solution:** This section is DYNAMIC (pulls from database) - you have 3 options:

### Option A: Skip It (Recommended for now)
- The hardcoded version shows this automatically
- Wait for developer to add this component to page builder

### Option B: Add Static Text
1. Drag `Heading` component
2. Text: "Featured Courses"
3. Center align
4. Drag `Text` component
5. Add message: "Visit our Courses page to explore our catalog"
6. Drag `CTA` component
7. Button text: "View All Courses"
8. Link: /courses

### Option C: Request Custom Component
- Ask developer to create a "FeaturedCourses" component for Puck

**My Recommendation:** Use Option B (static heading + CTA button)

---

## 7️⃣ Spacer

**Component to Use:** `Spacer`

**Configuration:**
```
Height: Large (or 96px)
```

---

## 8️⃣ Testimonials Section

**Component to Use:** `Heading` + `Text` + Three `Testimonial` components

**Step 1: Add Section Heading**
1. Drag `Heading` component
2. Text: "What Our Community Says"
3. Alignment: Center
4. Size: Large (H2)

**Step 2: Add Section Description**
1. Drag `Text` component
2. Text: "Hear from members who have experienced spiritual growth through our ministry."
3. Alignment: Center

**Step 3: Add Testimonial 1**
1. Drag `Testimonial` component
2. Configure:
```
Name: Sarah Johnson
Role: Community Member
Quote: "The courses offered by School of the Priests have deepened my understanding of Scripture in ways I never thought possible."
Avatar: SJ (initials)
```

**Step 4: Add Testimonial 2**
1. Drag `Testimonial` component
2. Configure:
```
Name: Michael Thomas
Role: Course Student
Quote: "I've been searching for solid biblical teaching that challenges me to grow spiritually. This ministry has provided that and more."
Avatar: MT
```

**Step 5: Add Testimonial 3**
1. Drag `Testimonial` component
2. Configure:
```
Name: Rebecca Wilson
Role: Ministry Leader
Quote: "As a ministry leader, I've found the resources provided here invaluable for my own spiritual development."
Avatar: RW
```

**Note:** The testimonials might need to be arranged horizontally - check if there's a layout/grid option

---

## 9️⃣ Spacer

**Component to Use:** `Spacer`

**Configuration:**
```
Height: Large
```

---

## 🔟 Call-to-Action Section

**Component to Use:** `CTA`

**Configuration:**
```
Heading: Ready to Start Your Journey?
Description: Join thousands of believers who are growing in their faith through our biblical teaching and community.

Primary Button:
  - Text: "Join Our Community"
  - Link: /register
  - Style: Light (white background)

Secondary Button:
  - Text: "Contact Us"
  - Link: /contact
  - Style: Outline (white border)

Background: Dark (or enable dark mode for this component)
```

---

## 1️⃣1️⃣ Final Spacer

**Component to Use:** `Spacer`

**Configuration:**
```
Height: Medium
```

This adds padding before the footer.

---

## 📊 Complete Component Order

Here's the exact order to drag components:

1. ✅ **Hero** - Main hero section
2. ✅ **Spacer** - Small
3. ⚠️ **[Stats - Skip for now]** - No component available
4. ✅ **Spacer** - Small
5. ✅ **FeaturesGrid** - Why Choose section
6. ✅ **Spacer** - Medium
7. ⚠️ **Heading** - "Featured Courses" (static workaround)
8. ⚠️ **Text** - Description
9. ⚠️ **CTA** - "View All Courses" button
10. ✅ **Spacer** - Large
11. ✅ **Heading** - "What Our Community Says"
12. ✅ **Text** - Testimonials description
13. ✅ **Testimonial** - Sarah Johnson
14. ✅ **Testimonial** - Michael Thomas
15. ✅ **Testimonial** - Rebecca Wilson
16. ✅ **Spacer** - Large
17. ✅ **CTA** - Ready to Start Your Journey
18. ✅ **Spacer** - Medium

---

## 🎯 Quick Start Checklist

Use this when building your page:

- [ ] **Step 1:** Open Admin → Pages → Edit: Home
- [ ] **Step 2:** Drag `Hero` component → Configure with main headline
- [ ] **Step 3:** Add `Spacer` (small)
- [ ] **Step 4:** Drag `FeaturesGrid` → Add 3 features
- [ ] **Step 5:** Add `Spacer` (medium)
- [ ] **Step 6:** Add section for "Featured Courses" (Heading + Text + CTA)
- [ ] **Step 7:** Add `Spacer` (large)
- [ ] **Step 8:** Add `Heading` for testimonials section
- [ ] **Step 9:** Add `Text` for testimonials description
- [ ] **Step 10:** Drag 3 `Testimonial` components
- [ ] **Step 11:** Add `Spacer` (large)
- [ ] **Step 12:** Drag `CTA` for final call-to-action
- [ ] **Step 13:** Add final `Spacer` (medium)
- [ ] **Step 14:** Click "Save Draft" to save progress
- [ ] **Step 15:** Preview the page
- [ ] **Step 16:** Click "Publish" when satisfied

---

## ⚠️ Known Limitations

**Components NOT available that you need:**
1. **Stats Grid** - The "500+ Members, 50+ Courses" section
2. **Featured Courses** - Dynamic course display from database

**Options:**
- **Skip these sections** - They're nice but not critical
- **Use workarounds** - Static text + buttons
- **Request from developer** - Ask to add these components to Puck

---

## 💡 Tips

1. **Save Often** - Click "Save Draft" frequently as you work
2. **Use Spacers** - They create breathing room between sections
3. **Preview First** - Don't publish until you've previewed
4. **Mobile Check** - The components should be responsive automatically
5. **Compare** - Keep your hardcoded page open in another tab to compare

---

## 🆘 If You Get Stuck

**Problem:** Can't find a component
**Solution:** Check the list above for workarounds

**Problem:** Component doesn't look right
**Solution:** Each component should have configuration options on the right sidebar

**Problem:** Layout is wrong
**Solution:** Components stack vertically by default - use FeaturesGrid for horizontal layouts

**Problem:** Lost your work
**Solution:** Click "Save Draft" - it auto-saves but manual save is safer

---

## 📸 Visual Reference

Your page structure should look like this in the editor:

```
[Canvas Area]
├─ Hero (with title, description, buttons)
├─ Spacer
├─ FeaturesGrid (3 features)
├─ Spacer
├─ Heading (Featured Courses - optional)
├─ Text (Description)
├─ CTA (View All Courses button)
├─ Spacer
├─ Heading (What Our Community Says)
├─ Text (Description)
├─ Testimonial (Sarah Johnson)
├─ Testimonial (Michael Thomas)
├─ Testimonial (Rebecca Wilson)
├─ Spacer
├─ CTA (Ready to Start Your Journey)
└─ Spacer
```

---

**Ready to Build?** Open Admin → Pages → Edit: Home and start dragging components!

**Questions?** Refer to `HARDCODED_HOME_PAGE_BACKUP.md` for exact text content.
