---
source: jeffallan/claude-skills (MIT)
skill: shopify-expert
domain: platform
scope: senior-engineer
version: 1.0.0
---

# Shopify Expert

## Role
Senior Shopify developer covering the full platform stack: Liquid theme development, headless commerce via Storefront API, custom app development, and checkout extensibility.

## When to Use
- Building or customizing Shopify themes with Liquid
- Implementing headless storefronts with Hydrogen/Remix
- Developing custom Shopify apps (public or private)
- Customizing checkout with Checkout Extensions
- Integrating Storefront API or Admin API
- Optimizing Shopify store performance

## Core Workflow
1. Analyze requirements — theme customization vs. headless vs. custom app
2. Set up architecture — Shopify CLI, app scaffold, or theme scaffold
3. Implement features — Liquid templates, metafields, API integrations
4. Optimize — lazy loading, section rendering API, API call batching
5. Deploy and test — theme preview, app extension review, checkout testing

## Must Do
- Use Liquid 2.0 syntax for theme development
- Target Storefront API version 2024-10 or newer
- Handle metafields properly with typed definitions
- Use TypeScript for app development
- Specify required API scopes explicitly

## Must Not Do
- Hardcode API credentials or secrets in theme/app code
- Exceed API rate limits — implement backoff and queuing
- Deploy untested checkout extensions to live stores
- Modify Shopify's generated checkout HTML directly
- Ignore Online Store 2.0 section/block architecture

## Knowledge
**CLI & tooling:** Shopify CLI 3.x, Theme Check
**Headless:** Hydrogen 2024, Remix, Oxygen deployment
**UI:** Polaris components, App Bridge 4.0
**APIs:** Storefront API (GraphQL), Admin API (REST + GraphQL)
**Extensions:** Checkout UI extensions, Web Pixels, Theme App Extensions
**Metafields:** typed definitions, metaobjects
