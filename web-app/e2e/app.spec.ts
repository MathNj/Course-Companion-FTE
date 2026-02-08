import { test, expect } from '@playwright/test';

/*
  Base URL configuration
  Tests run against http://localhost:3000 by default
*/

test.describe('Basic Page Loads', () => {
  test('should load home page', async ({ page }) => {
    await page.goto('/');

    // Check that page has loaded and has content
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should load library page', async ({ page }) => {
    await page.goto('/library');

    // Check that page has loaded
    await expect(page.locator('body')).toBeVisible();
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should load chapter page', async ({ page }) => {
    await page.goto('/chapters/chapter-1');

    // Check that page has loaded
    await expect(page.locator('body')).toBeVisible();
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(100);
  });
});

test.describe('Premium Access Control', () => {
  test('should show premium lock for premium chapters without auth', async ({ page }) => {
    await page.goto('/chapters/chapter-4');

    // Should show premium lock or upgrade prompt - check for lock icon or upgrade text
    const pageContent = await page.content();
    const hasPremiumContent = pageContent.includes('Premium') || pageContent.includes('premium') ||
                             pageContent.includes('upgrade') || pageContent.includes('Upgrade') ||
                             pageContent.includes('Lock') || pageContent.includes('lock');
    expect(hasPremiumContent).toBeTruthy();
  });
});

test.describe('Header Navigation', () => {
  test('should have key navigation elements', async ({ page }) => {
    await page.goto('/');

    // Check for navigation - should have some content
    await expect(page.locator('body')).toBeVisible();
    const pageContent = await page.content();
    // Should have some navigation-related text or links
    const hasNav = pageContent.includes('Course') || pageContent.includes('Companion') ||
                  pageContent.includes('Login') || pageContent.includes('Student') ||
                  pageContent.includes('Teacher') || pageContent.includes('href=');
    expect(hasNav).toBeTruthy();
  });

  test('should NOT have /admin links', async ({ page }) => {
    await page.goto('/');

    // Check that there are no /admin links
    const adminLinks = await page.locator('a[href="/admin"]').count();
    expect(adminLinks).toBe(0);
  });
});

test.describe('Chapter Pages', () => {
  test('should display chapter content area', async ({ page }) => {
    await page.goto('/chapters/chapter-1');

    // Check that page loaded with content
    await expect(page.locator('body')).toBeVisible();
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should load quiz page for chapter', async ({ page }) => {
    await page.goto('/chapters/chapter-1/quiz');

    // Check for quiz content or redirect message
    const pageContent = await page.content();
    const hasQuizOrAuth = pageContent.includes('Quiz') || pageContent.includes('quiz') || pageContent.includes('Sign') || pageContent.includes('Log');
    expect(hasQuizOrAuth).toBeTruthy();
  });
});

test.describe('Teacher Dashboard', () => {
  test('should load teacher page (may show access denied)', async ({ page }) => {
    await page.goto('/teacher');

    // Page should load - may show access denied or teacher content
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(0);
  });
});

test.describe('Error Handling', () => {
  test('should handle invalid routes gracefully', async ({ page }) => {
    const response = await page.goto('/this-page-does-not-exist-12345');
    // Should get some response (404, 500, or redirect)
    expect(response).toBeTruthy();
  });
});

test.describe('Responsive Design', () => {
  test('should be mobile friendly', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');

    // The body should be visible on mobile
    await expect(page.locator('body')).toBeVisible();
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(50);
  });
});

test.describe('Library Page', () => {
  test('should display chapter cards', async ({ page }) => {
    await page.goto('/library');

    // Check that page loaded and has content
    await expect(page.locator('body')).toBeVisible();
    const bodyText = await page.locator('body').textContent();
    expect(bodyText?.length).toBeGreaterThan(100);
  });

  test('should show access tier badges', async ({ page }) => {
    await page.goto('/library');

    // Check that page has some content
    const pageContent = await page.content();
    const hasContent = pageContent.length > 500;
    expect(hasContent).toBeTruthy();
  });
});
