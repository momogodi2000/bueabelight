// BueaDelights Admin Dashboard Service Worker
// Version 1.0.0

const CACHE_NAME = 'bueadelights-admin-v1.0.0';
const DATA_CACHE_NAME = 'bueadelights-data-v1.0.0';
const IMAGE_CACHE_NAME = 'bueadelights-images-v1.0.0';
const API_CACHE_NAME = 'bueadelights-api-v1.0.0';

// Files to cache immediately on install
const FILES_TO_CACHE = [
  '/admin/dashboard/',
  '/admin/offline/',
  '/static/css/admin.css',
  '/static/js/admin.js',
  '/static/images/icon-192x192.png',
  '/static/images/icon-512x512.png',
  '/static/images/logo.png',
  '/static/fonts/',
  '/manifest.json',
  'https://cdn.jsdelivr.net/npm/chart.js',
  'https://unpkg.com/aos@2.3.1/dist/aos.css',
  'https://unpkg.com/aos@2.3.1/dist/aos.js',
  'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap'
];

// API endpoints that should be cached
const API_ENDPOINTS = [
  '/admin/api/dashboard-stats/',
  '/admin/api/recent-orders/',
  '/admin/api/low-stock-products/',
  '/admin/api/analytics-data/',
  '/admin/api/orders/',
  '/admin/api/products/',
  '/admin/api/categories/',
  '/admin/api/messages/',
  '/admin/api/catering/'
];

// Background sync tags
const SYNC_TAGS = {
  ORDER_SYNC: 'order-sync',
  PRODUCT_SYNC: 'product-sync',
  ANALYTICS_SYNC: 'analytics-sync',
  MESSAGE_SYNC: 'message-sync'
};

// Install event - cache core files
self.addEventListener('install', (event) => {
  console.log('[ServiceWorker] Install');
  
  event.waitUntil(
    Promise.all([
      // Cache core application files
      caches.open(CACHE_NAME).then((cache) => {
        console.log('[ServiceWorker] Pre-caching offline page and core files');
        return cache.addAll(FILES_TO_CACHE);
      }),
      
      // Skip waiting to activate immediately
      self.skipWaiting()
    ])
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[ServiceWorker] Activate');
  
  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return !cacheName.startsWith('bueadelights-') || 
                     ![CACHE_NAME, DATA_CACHE_NAME, IMAGE_CACHE_NAME, API_CACHE_NAME].includes(cacheName);
            })
            .map((cacheName) => {
              console.log('[ServiceWorker] Removing old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      }),
      
      // Take control of all clients
      self.clients.claim()
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Handle different types of requests with appropriate strategies
  if (url.pathname.startsWith('/admin/api/')) {
    // API requests - Network First with fallback
    event.respondWith(handleApiRequest(request));
  } else if (isImageRequest(request)) {
    // Images - Cache First
    event.respondWith(handleImageRequest(request));
  } else if (isStaticResource(request)) {
    // Static resources - Stale While Revalidate
    event.respondWith(handleStaticResource(request));
  } else if (url.pathname.startsWith('/admin/')) {
    // Admin pages - Network First with offline fallback
    event.respondWith(handleAdminPage(request));
  }
});

// API Request Handler - Network First Strategy
async function handleApiRequest(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(API_CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[ServiceWorker] Network request failed, serving from cache:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline data structure for API endpoints
    return new Response(JSON.stringify(getOfflineApiResponse(request.url)), {
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

// Image Request Handler - Cache First Strategy
async function handleImageRequest(request) {
  const cache = await caches.open(IMAGE_CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  if (cachedResponse) {
    return cachedResponse;
  }
  
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  } catch (error) {
    // Return placeholder image for failed image requests
    return new Response(getPlaceholderImage(), {
      headers: { 'Content-Type': 'image/svg+xml' }
    });
  }
}

// Static Resource Handler - Stale While Revalidate
async function handleStaticResource(request) {
  const cache = await caches.open(CACHE_NAME);
  const cachedResponse = await cache.match(request);
  
  const fetchPromise = fetch(request).then((networkResponse) => {
    if (networkResponse.ok) {
      cache.put(request, networkResponse.clone());
    }
    return networkResponse;
  }).catch(() => cachedResponse);
  
  return cachedResponse || fetchPromise;
}

// Admin Page Handler - Network First with Offline Fallback
async function handleAdminPage(request) {
  try {
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.log('[ServiceWorker] Admin page request failed, checking cache:', error);
    
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline page
    return caches.match('/admin/offline/');
  }
}

// Background Sync - Handle offline actions
self.addEventListener('sync', (event) => {
  console.log('[ServiceWorker] Background sync:', event.tag);
  
  switch (event.tag) {
    case SYNC_TAGS.ORDER_SYNC:
      event.waitUntil(syncOrders());
      break;
    case SYNC_TAGS.PRODUCT_SYNC:
      event.waitUntil(syncProducts());
      break;
    case SYNC_TAGS.ANALYTICS_SYNC:
      event.waitUntil(syncAnalytics());
      break;
    case SYNC_TAGS.MESSAGE_SYNC:
      event.waitUntil(syncMessages());
      break;
    default:
      console.log('[ServiceWorker] Unknown sync tag:', event.tag);
  }
});

// Push Notification Handler
self.addEventListener('push', (event) => {
  console.log('[ServiceWorker] Push received:', event);
  
  const options = {
    body: 'New order received! Check your dashboard.',
    icon: '/static/images/icon-192x192.png',
    badge: '/static/images/badge-72x72.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'view-orders',
        title: 'View Orders',
        icon: '/static/images/action-view.png'
      },
      {
        action: 'dismiss',
        title: 'Dismiss',
        icon: '/static/images/action-dismiss.png'
      }
    ],
    requireInteraction: true,
    tag: 'bueadelights-notification'
  };
  
  if (event.data) {
    const data = event.data.json();
    options.body = data.message || options.body;
    options.data = { ...options.data, ...data };
  }
  
  event.waitUntil(
    self.registration.showNotification('BueaDelights Admin', options)
  );
});

// Notification Click Handler
self.addEventListener('notificationclick', (event) => {
  console.log('[ServiceWorker] Notification click received:', event);
  
  event.notification.close();
  
  if (event.action === 'view-orders') {
    event.waitUntil(
      clients.openWindow('/admin/orders/')
    );
  } else if (event.action === 'dismiss') {
    // Just close the notification
    return;
  } else {
    // Default action - open dashboard
    event.waitUntil(
      clients.openWindow('/admin/dashboard/')
    );
  }
});

// Message Handler for communication with main thread
self.addEventListener('message', (event) => {
  console.log('[ServiceWorker] Message received:', event.data);
  
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      cacheUrls(event.data.urls)
    );
  }
});

// Utility Functions

function isImageRequest(request) {
  return request.destination === 'image' || 
         /\.(jpg|jpeg|png|gif|webp|svg|ico)$/i.test(new URL(request.url).pathname);
}

function isStaticResource(request) {
  return request.destination === 'style' || 
         request.destination === 'script' || 
         request.destination === 'font' ||
         /\.(css|js|woff|woff2|ttf|eot)$/i.test(new URL(request.url).pathname);
}

function getOfflineApiResponse(url) {
  const pathname = new URL(url).pathname;
  
  const offlineResponses = {
    '/admin/api/dashboard-stats/': {
      total_orders: 0,
      pending_orders: 0,
      total_products: 0,
      total_revenue: 0,
      status: 'offline'
    },
    '/admin/api/recent-orders/': {
      results: [],
      message: 'Offline - showing cached data',
      status: 'offline'
    },
    '/admin/api/low-stock-products/': {
      results: [],
      message: 'Offline - showing cached data',
      status: 'offline'
    }
  };
  
  return offlineResponses[pathname] || {
    message: 'Data unavailable offline',
    status: 'offline'
  };
}

function getPlaceholderImage() {
  return `<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" fill="#228B22" opacity="0.1"/>
    <text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="#228B22" font-family="sans-serif" font-size="16">
      🍽️ BueaDelights
    </text>
  </svg>`;
}

async function cacheUrls(urls) {
  const cache = await caches.open(CACHE_NAME);
  return cache.addAll(urls);
}

// Background Sync Functions

async function syncOrders() {
  try {
    console.log('[ServiceWorker] Syncing orders...');
    
    // Get pending orders from IndexedDB or localStorage
    const pendingOrders = await getPendingData('orders');
    
    for (const order of pendingOrders) {
      try {
        const response = await fetch('/admin/api/orders/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await getCSRFToken()
          },
          body: JSON.stringify(order)
        });
        
        if (response.ok) {
          await removePendingData('orders', order.id);
          await showNotification('Order synced successfully!');
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync order:', error);
      }
    }
    
    console.log('[ServiceWorker] Orders sync completed');
  } catch (error) {
    console.error('[ServiceWorker] Orders sync failed:', error);
  }
}

async function syncProducts() {
  try {
    console.log('[ServiceWorker] Syncing products...');
    
    const pendingProducts = await getPendingData('products');
    
    for (const product of pendingProducts) {
      try {
        const response = await fetch('/admin/api/products/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await getCSRFToken()
          },
          body: JSON.stringify(product)
        });
        
        if (response.ok) {
          await removePendingData('products', product.id);
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync product:', error);
      }
    }
    
    console.log('[ServiceWorker] Products sync completed');
  } catch (error) {
    console.error('[ServiceWorker] Products sync failed:', error);
  }
}

async function syncAnalytics() {
  try {
    console.log('[ServiceWorker] Syncing analytics...');
    
    const pendingAnalytics = await getPendingData('analytics');
    
    for (const data of pendingAnalytics) {
      try {
        const response = await fetch('/admin/api/analytics/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await getCSRFToken()
          },
          body: JSON.stringify(data)
        });
        
        if (response.ok) {
          await removePendingData('analytics', data.id);
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync analytics:', error);
      }
    }
    
    console.log('[ServiceWorker] Analytics sync completed');
  } catch (error) {
    console.error('[ServiceWorker] Analytics sync failed:', error);
  }
}

async function syncMessages() {
  try {
    console.log('[ServiceWorker] Syncing messages...');
    
    const pendingMessages = await getPendingData('messages');
    
    for (const message of pendingMessages) {
      try {
        const response = await fetch('/admin/api/messages/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': await getCSRFToken()
          },
          body: JSON.stringify(message)
        });
        
        if (response.ok) {
          await removePendingData('messages', message.id);
        }
      } catch (error) {
        console.error('[ServiceWorker] Failed to sync message:', error);
      }
    }
    
    console.log('[ServiceWorker] Messages sync completed');
  } catch (error) {
    console.error('[ServiceWorker] Messages sync failed:', error);
  }
}

// Helper functions for data management
async function getPendingData(type) {
  // This would typically use IndexedDB
  // For now, returning empty array as placeholder
  return [];
}

async function removePendingData(type, id) {
  // Remove from IndexedDB after successful sync
  console.log(`[ServiceWorker] Removing pending ${type} data for ID:`, id);
}

async function getCSRFToken() {
  try {
    const response = await fetch('/admin/api/csrf-token/');
    const data = await response.json();
    return data.csrfToken;
  } catch (error) {
    console.error('[ServiceWorker] Failed to get CSRF token:', error);
    return '';
  }
}

async function showNotification(message) {
  try {
    await self.registration.showNotification('BueaDelights Admin', {
      body: message,
      icon: '/static/images/icon-192x192.png',
      badge: '/static/images/badge-72x72.png'
    });
  } catch (error) {
    console.error('[ServiceWorker] Failed to show notification:', error);
  }
}

// Performance monitoring
self.addEventListener('fetch', (event) => {
  const start = performance.now();
  
  event.respondWith(
    handleRequest(event.request).then((response) => {
      const end = performance.now();
      console.log(`[ServiceWorker] Request to ${event.request.url} took ${end - start}ms`);
      return response;
    })
  );
});

function handleRequest(request) {
  // This would contain the main fetch handling logic
  // Delegating to the appropriate handler based on request type
  const url = new URL(request.url);
  
  if (url.pathname.startsWith('/admin/api/')) {
    return handleApiRequest(request);
  } else if (isImageRequest(request)) {
    return handleImageRequest(request);
  } else if (isStaticResource(request)) {
    return handleStaticResource(request);
  } else if (url.pathname.startsWith('/admin/')) {
    return handleAdminPage(request);
  } else {
    return fetch(request);
  }
}

console.log('[ServiceWorker] BueaDelights Admin Service Worker loaded successfully');