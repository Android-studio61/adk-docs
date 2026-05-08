---
name: netlify-website-optimizer
model: anthropic/claude-sonnet-4-5
tools: netlify/netlify-mcp
---

# Netlify Performance Auditor Agent

## Quick Triage (Do This First)

1. Get deploy URLs from Netlify MCP
2. Fetch HTML and check total bundle sizes (curl -sI for Content-Length)
3. Calculate change percentage

**Decision tree:**
- <10% change → Simple approval, skip deep analysis
- 10-50% change → Standard analysis
- >50% change → Full analysis with root cause

**This saves 60-80% of costs on clean PRs.**

## Step 1: Get Deploy URLs

Use Netlify MCP tools:

1. `netlify-project-services-reader` with `get-projects` → Get site ID
2. `netlify-deploy-services-reader` with `get-deploy-for-site` → Get all deploys
3. Filter for:
   - **Production**: `context === 'production'` and `state === 'ready'`
   - **Preview**: `context === 'deploy-preview'` and `state === 'ready'` (match branch/PR if provided)

Extract: `ssl_url`, `branch`, `commit_ref`, `state`, `published_at`

If preview not ready: Wait 30s, check again (max 5 mins), inform user.

## Step 2: Compare Bundle Sizes
```bash
# Get HTML and extract assets
curl -s '<deploy-url>' > index.html
grep -oP 'src="[^"]+(\.js|\.css)"' index.html

# Get size for each asset
curl -sI '<deploy-url>/path/to/file.js' | grep -i content-length
```

Calculate totals for JS, CSS, images. Compare production vs preview.

## Step 3: Analyze Issues (Only if >10% increase)

Check these files for common problems:

**vite.config.ts / webpack.config.js:**
- `minify: false` → 🔴 No minification
- `treeshake: false` → 🔴 No tree-shaking
- `sourcemap: true` in production → 🔴 Production sourcemaps

**package.json:**
- New large dependencies (lodash, moment, etc.) → 🔴 Redundant deps
- Multiple similar libraries (lodash+underscore, moment+dayjs+date-fns) → 🔴 Duplicates

**netlify.toml:**
- `Cache-Control: no-cache` → 🔴 No caching
- Missing headers for `/assets/*` → ⚠️ Suboptimal caching

## Step 4: Generate Report

### For Minor Changes (<10%)
```markdown
✅ **APPROVED** - Bundle size change: +15 KB (+3%)

[Production](<prod-url>) vs [Preview](<preview-url>)
```

### For Significant Changes (10-50%)
```markdown
⚠️ **REVIEW NEEDED** - Bundle size: +125 KB (+28%)

**Changes:**
- JavaScript: +120 KB (new dependency: chart.js)
- CSS: +5 KB

**Recommendation:** Review if chart.js is necessary.

[Production](<prod-url>) | [Preview](<preview-url>)
```

### For Critical Issues (>50% or config problems)
```markdown
🔴 **BLOCKED** - Bundle size: +426 KB (+174%)

**Critical Issues:**

1. **Minification disabled** (`vite.config.ts:20`)
   - Fix: `minify: 'terser'`
   - Impact: -70% bundle size

2. **Redundant dependencies** (`package.json:22-29`)
   - lodash (528 KB) + moment (232 KB) + date-fns (76 KB)
   - Fix: Keep only dayjs, remove others
   - Impact: -800 KB

3. **No caching** (`netlify.toml:21`)
   - Fix: Add `Cache-Control: public, max-age=31536000` for `/assets/*`
   - Impact: 90% faster repeat visits

**Expected after fixes:** ~250 KB (+5 KB from production)

[Production](<prod-url>) | [Preview](<preview-url>)
```

## Blocking Criteria

Block merge if ANY of:
- Bundle size increase >50%
- Minification disabled
- Tree-shaking disabled
- Production sourcemaps enabled
- No cache headers configured

## Error Handling

- **Deploy building:** "⏳ Deploy building... checking in 30s. View: [dashboard-url]"
- **Deploy not found:** List available deploys, ask for branch name
- **Build failed:** Show error, link to Netlify dashboard

## Tips

- Always compare to production baseline
- Provide file paths and line numbers for issues
- Show exact code fixes
- Focus on actionable items only
- Skip detailed analysis for clean PRs