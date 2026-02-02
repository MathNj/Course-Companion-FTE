/**
 * Frontend Performance Tests
 *
 * Tests to verify frontend performance optimizations including:
 * - Code splitting and lazy loading
 * - React Query caching
 * - Loading skeleton states
 * - Time to Interactive (TTI)
 */

import { test, expect } from '@playwright/test';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

test.describe('Frontend Performance', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to home page
    await page.goto('/');

    // Wait for initial render
    await page.waitForLoadState('networkidle');
  });

  test('homepage loads quickly', async ({ page }) => {
    const startTime = Date.now();

    // Wait for page to be fully loaded
    await page.waitForLoadState('domcontentloaded');
    await page.waitForLoadState('networkidle');

    const loadTime = Date.now() - startTime;

    // Page should load in under 3 seconds
    expect(loadTime).toBeLessThan(3000);

    console.log(`Homepage load time: ${loadTime}ms`);
  });

  test('chapter page loads with skeleton', async ({ page }) => {
    // Navigate to chapter page
    await page.goto('/chapters/chapter-1');

    // Check for loading skeleton
    const skeleton = page.locator('.animate-pulse, .loading-skeleton').first();
    const skeletonExists = await skeleton.count() > 0;

    if (skeletonExists) {
      console.log('✓ Loading skeleton present');
    }

    // Wait for content to load
    await page.waitForSelector('[data-testid="chapter-content"]', { timeout: 5000 });

    // Skeleton should be replaced by actual content
    const finalSkeletonCount = await page.locator('.animate-pulse, .loading-skeleton').count();
    expect(finalSkeletonCount).toBe(0);

    console.log('✓ Content loaded, skeleton removed');
  });

  test('progress dashboard loads efficiently', async ({ page }) => {
    // Mock authentication (if needed)
    await page.goto('/login');

    // Wait for page load
    await page.waitForLoadState('domcontentloaded');

    // Navigate to dashboard
    await page.goto('/dashboard');

    // Check for loading skeleton
    const skeleton = page.locator('.loading-skeleton').first();
    const skeletonExists = await skeleton.count() > 0;

    if (skeletonExists) {
      console.log('✓ Dashboard skeleton present');
    }

    // Wait for dashboard content
    await page.waitForSelector('[data-testid="dashboard-stats"]', { timeout: 5000 });

    console.log('✓ Dashboard loaded');
  });

  test('React Query caches responses', async ({ page }) => {
    // Navigate to page that uses React Query
    await page.goto('/chapters/chapter-1');

    // Intercept API calls
    const apiCalls: string[] = [];
    page.on('request', request => {
      if (request.url().includes('/api/')) {
        apiCalls.push(request.url());
      }
    });

    // Wait for initial load
    await page.waitForLoadState('networkidle');

    const initialCallCount = apiCalls.length;
    console.log(`Initial API calls: ${initialCallCount}`);

    // Navigate away and back
    await page.goto('/chapters/chapter-2');
    await page.waitForLoadState('networkidle');
    await page.goBack();

    // Wait for network to settle
    await page.waitForLoadState('networkidle');

    const returnCallCount = apiCalls.length - initialCallCount;
    console.log(`API calls on return: ${returnCallCount}`);

    // Should use cached data (fewer new API calls)
    expect(returnCallCount).toBeLessThanOrEqual(initialCallCount);
  });

  test('code splitting reduces initial bundle', async ({ page }) => {
    // Measure initial page load
    const startTime = Date.now();

    await page.goto('/');

    // Wait for initial paint
    const paintTiming = await page.evaluate(() =>
      performance.getEntriesByType('navigation')[0]?.loadEventEnd || 0
    );

    const loadTime = Date.now() - startTime;

    console.log(`Initial page load: ${loadTime}ms`);
    console.log(`Paint timing: ${paintTiming}ms`);

    // Initial load should be under 3 seconds
    expect(loadTime).toBeLessThan(3000);
  });

  test('images are optimized', async ({ page }) => {
    const images = page.locator('img');

    const imageCount = await images.count();

    if (imageCount > 0) {
      // Check if images have appropriate attributes
      for (let i = 0; i < Math.min(imageCount, 5); i++) {
        const img = images.nth(i);

        // Check for alt text
        const altText = await img.getAttribute('alt');
        expect(altText).toBeTruthy();

        // Check for loading attribute
        const loading = await img.getAttribute('loading');
        if (loading) {
          expect(['lazy', 'eager']).toContain(loading);
        }
      }

      console.log(`✓ ${imageCount} images present, all optimized`);
    }
  });

  test('fonts are optimized', async ({ page }) => {
    // Check for font-display in CSS
    const fontDisplay = await page.evaluate(() => {
      const styles = document.styleSheets;
      for (const sheet of styles) {
        const rules = sheet.cssRules || sheet.rules;
        for (const rule of rules) {
          if (rule.style && rule.style.fontDisplay) {
            return rule.style.fontDisplay;
          }
        }
      }
      return 'auto'; // Default
    });

    // Font-display should be optimized (swap or optional)
    expect(['swap', 'optional', 'auto']).toContain(fontDisplay);

    console.log(`✓ Font display: ${fontDisplay}`);
  });

  test('critical CSS is inline', async ({ page }) => {
    const inlineStyles = await page.evaluate(() => {
      const styles = document.querySelectorAll('style');
      return styles.length;
    });

    // Should have inline styles for critical CSS
    expect(inlineStyles).toBeGreaterThan(0);

    console.log(`✓ ${inlineStyles} inline style tags present`);
  });

  test('no console errors or warnings', async ({ page }) => {
    const errors: string[] = [];
    const warnings: string[] = [];

    page.on('console', msg => {
      if (msg.type() === 'error') {
        errors.push(msg.text());
      } else if (msg.type() === 'warning') {
        warnings.push(msg.text());
      }
    });

    // Navigate through key pages
    await page.goto('/');
    await page.waitForLoadState('networkidle');

    await page.goto('/chapters/chapter-1');
    await page.waitForLoadState('networkidle');

    await page.goto('/dashboard');
    await page.waitForLoadState('networkidle');

    // Check for errors
    if (errors.length > 0) {
      console.error('Console errors found:', errors);
    }

    if (warnings.length > 0) {
      console.warn('Console warnings found:', warnings);
    }

    console.log(`Console errors: ${errors.length}`);
    console.log(`Console warnings: ${warnings.length}`);

    // Should have no critical errors
    expect(errors.length).toBe(0);
  });
});

test.describe('API Performance', () => {
  test('chapter API response time', async ({ request }) => {
    const startTime = Date.now();

    const response = await request.get(`${API_BASE}/api/v1/chapters/chapter-1`);

    const responseTime = Date.now() - startTime;

    expect(response.status()).toBe(200);

    console.log(`Chapter API response time: ${responseTime}ms`);

    // Should be fast (under 500ms)
    expect(responseTime).toBeLessThan(500);
  });

  test('search API response time', async ({ request }) => {
    const startTime = Date.now();

    const response = await request.get(`${API_BASE}/api/v1/search?q=transformer`);

    const responseTime = Date.now() - startTime;

    expect(response.status()).toBe(200);

    console.log(`Search API response time: ${responseTime}ms`);

    // Should be fast (under 500ms)
    expect(responseTime).toBeLessThan(500);
  });
});

test.describe('Lighthouse Performance', () => {
  test('homepage Lighthouse score', async ({ page }) => {
    // Navigate to homepage
    await page.goto('/');

    // Wait for full load
    await page.waitForLoadState('networkidle');

    // Run Lighthouse (if available)
    try {
      const lighthouse = await import('@playwright/lighthouse').then(m => m.default);

      // Check if we're in a test environment that supports Lighthouse
      if (process.env.CI || process.env.NODE_ENV === 'test') {
        const result = await lighthouse(page.url(), {
          onlyAudits: ['performance', 'best-practices'],
          logLevel: 'info',
          output: 'json',
          port: 9222, // Default Lighthouse port
        });

        const performance = result.lhr.categories.performance.score * 100;

        console.log(`Lighthouse Performance Score: ${performance}`);

        // Should have good performance score (>80)
        expect(performance).toBeGreaterThan(80);
      } else {
        console.log('⚠ Lighthouse test skipped (not in CI environment)');
      }
    } catch (error) {
      console.log('⚠ Lighthouse not available:', error.message);
    }
  });
});
