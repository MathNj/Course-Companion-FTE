/**
 * Service Worker for Course Companion FTE PWA
 * Provides offline support and caching strategies
 */

const CACHE_NAME = 'course-companion-v1';
const OFFLINE_URL = '/offline';

// Assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/offline',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// API routes to cache with network-first strategy
const API_CACHE_PATTERN = /\/api\//;

// Static assets cache pattern
const STATIC_CACHE_PATTERN = /\.(?:js|css|png|jpg|jpeg|svg|gif|webp|woff2?)$/;

// Install event - precache static assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');

  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Precaching assets');
      return cache.addAll(PRECACHE_ASSETS.map(url => new Request(url, { cache: 'reload' })))
        .catch((error) => {
          console.error('[SW] Failed to precache:', error);
          // Continue installation even if precaching fails
        });
    })
  );

  // Force the waiting service worker to become active
  self.skipWaiting();
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((cacheName) => cacheName !== CACHE_NAME)
          .map((cacheName) => {
            console.log('[SW] Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          })
      );
    })
  );

  // Take control of all pages immediately
  self.clients.claim();
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }

  // Skip chrome extensions and other protocols
  if (!url.protocol.startsWith('http')) {
    return;
  }

  // Strategy 1: API requests - Network First, fallback to Cache
  if (API_CACHE_PATTERN.test(url.pathname)) {
    event.respondWith(networkFirstStrategy(request));
    return;
  }

  // Strategy 2: Static assets - Cache First, fallback to Network
  if (STATIC_CACHE_PATTERN.test(url.pathname)) {
    event.respondWith(cacheFirstStrategy(request));
    return;
  }

  // Strategy 3: HTML pages - Network First, fallback to Cache, then Offline
  event.respondWith(networkFirstWithOfflineFallback(request));
});

/**
 * Network First Strategy
 * Try network first, fallback to cache if offline
 */
async function networkFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    // Try network first
    const networkResponse = await fetch(request);

    // Cache the response for future use
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log('[SW] Serving from cache (API):', request.url);
      return cachedResponse;
    }

    // Nothing in cache, return error response
    return new Response(JSON.stringify({ error: 'Offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

/**
 * Cache First Strategy
 * Try cache first, fallback to network if not found
 */
async function cacheFirstStrategy(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);

  if (cachedResponse) {
    return cachedResponse;
  }

  try {
    // Not in cache, fetch from network
    const networkResponse = await fetch(request);

    // Cache for future use
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Network failed and nothing in cache
    console.error('[SW] Failed to fetch:', request.url);
    return new Response('Offline', { status: 503 });
  }
}

/**
 * Network First with Offline Fallback
 * For HTML pages - try network, then cache, then offline page
 */
async function networkFirstWithOfflineFallback(request) {
  const cache = await caches.open(CACHE_NAME);

  try {
    // Try network first
    const networkResponse = await fetch(request);

    // Cache successful responses
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }

    return networkResponse;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await cache.match(request);

    if (cachedResponse) {
      console.log('[SW] Serving from cache (page):', request.url);
      return cachedResponse;
    }

    // Nothing in cache, serve offline page
    const offlineResponse = await cache.match(new Request(OFFLINE_URL));

    if (offlineResponse) {
      return offlineResponse;
    }

    // No offline page available, return basic offline response
    return new Response(
      '<h1>You are offline</h1><p>Please check your internet connection.</p>',
      {
        status: 503,
        headers: { 'Content-Type': 'text/html' }
      }
    );
  }
}

// Message event - handle messages from clients
self.addEventListener('message', (event) => {
  console.log('[SW] Received message:', event.data);

  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }

  if (event.data && event.data.type === 'CACHE_URLS') {
    const urls = event.data.urls || [];
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => cache.addAll(urls))
    );
  }
});

// Push notification support (optional, for future use)
self.addEventListener('push', (event) => {
  if (!event.data) {
    return;
  }

  const data = event.data.json();
  const options = {
    body: data.body || '',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [200, 100, 200],
    data: {
      url: data.url || '/'
    }
  };

  event.waitUntil(self.registration.showNotification(data.title || 'Course Companion', options));
});

// Handle notification clicks
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  event.waitUntil(
    self.clients.openWindow(event.notification.data.url || '/')
  );
});

// Sync event for background sync (optional, for future use)
self.addEventListener('sync', (event) => {
  console.log('[SW] Background sync:', event.tag);

  if (event.tag === 'sync-notes') {
    event.waitUntil(syncNotes());
  }
});

/**
 * Sync notes with server when back online
 */
async function syncNotes() {
  // Get all clients and send sync message
  const clients = await self.clients.matchAll();
  clients.forEach((client) => {
    client.postMessage({ type: 'SYNC_NOTES' });
  });
}
