/**
 * FitMY Frontend Application
 *
 * Entry point for the FitMY client-side application.
 * Handles API communication, routing, and UI interactions.
 */

// -----------------------------------------------------------------
// Configuration
// -----------------------------------------------------------------

const API_BASE_URL = 'http://localhost:8001';

// -----------------------------------------------------------------
// API Helper
// -----------------------------------------------------------------

const api = {
    /**
     * Make an authenticated API request.
     * @param {string} endpoint - API endpoint (e.g., '/auth/login')
     * @param {object} options - Fetch options (method, body, etc.)
     * @returns {Promise<object>} - Response data
     */
    async request(endpoint, options = {}) {
        const token = localStorage.getItem('fitmy_access_token');

        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(token && { 'Authorization': `Bearer ${token}` }),
                ...options.headers,
            },
            ...options,
        };

        if (config.body && typeof config.body === 'object') {
            config.body = JSON.stringify(config.body);
        }

        try {
            const response = await fetch(`${API_BASE_URL}${endpoint}`, config);

            if (response.status === 401) {
                // Try to refresh token
                const refreshed = await api.refreshToken();
                if (refreshed) {
                    // Retry original request
                    return api.request(endpoint, options);
                }
                // Redirect to login
                window.location.href = 'login.html';
                return null;
            }

            const data = await response.json();

            if (!response.ok) {
                const errDetail = data.detail ? (typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)) : (data.error || 'An error occurred');
                throw new Error(errDetail);
            }

            return data;
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error.message);
            throw error;
        }
    },

    // Convenience methods
    get(endpoint) { return this.request(endpoint, { method: 'GET' }); },
    post(endpoint, body) { return this.request(endpoint, { method: 'POST', body }); },
    put(endpoint, body) { return this.request(endpoint, { method: 'PUT', body }); },
    delete(endpoint) { return this.request(endpoint, { method: 'DELETE' }); },

    /**
     * Attempt to refresh the access token using the refresh token.
     * @returns {Promise<boolean>} - True if refresh was successful
     */
    async refreshToken() {
        const refreshToken = localStorage.getItem('fitmy_refresh_token');
        if (!refreshToken) return false;

        try {
            const response = await fetch(`${API_BASE_URL}/api/auth/refresh`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh_token: refreshToken }),
            });

            if (!response.ok) return false;

            const data = await response.json();
            localStorage.setItem('fitmy_access_token', data.access_token);
            return true;
        } catch {
            return false;
        }
    },
};


// -----------------------------------------------------------------
// Auth State
// -----------------------------------------------------------------

const auth = {
    isLoggedIn() {
        return !!localStorage.getItem('fitmy_access_token');
    },

    login(tokenData) {
        localStorage.setItem('fitmy_access_token', tokenData.access_token);
        localStorage.setItem('fitmy_refresh_token', tokenData.refresh_token);
    },

    logout() {
        localStorage.removeItem('fitmy_access_token');
        localStorage.removeItem('fitmy_refresh_token');
        window.location.href = '/';
    },
};


// -----------------------------------------------------------------
// UI Helpers
// -----------------------------------------------------------------

/**
 * Smooth scroll to a section when clicking nav links.
 */
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.querySelector(anchor.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
}

/**
 * Add scroll-based navbar background effect.
 */
function initNavbarScroll() {
    const navbar = document.getElementById('main-nav');
    if (!navbar) return;

    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.background = 'rgba(10, 10, 15, 0.95)';
        } else {
            navbar.style.background = 'rgba(10, 10, 15, 0.85)';
        }
    });
}

/**
 * Animate elements when they come into view.
 */
function initScrollAnimations() {
    const observer = new IntersectionObserver(
        (entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        },
        { threshold: 0.1 }
    );

    document.querySelectorAll('.feature-card, .pricing-card').forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}


// -----------------------------------------------------------------
// Initialize
// -----------------------------------------------------------------

function handleOAuthRedirect() {
    const urlParams = new URLSearchParams(window.location.search);
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');

    if (accessToken && refreshToken) {
        auth.login({ access_token: accessToken, refresh_token: refreshToken });
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname);
    }
}

function updateUIForAuthState() {
    if (auth.isLoggedIn()) {
        const loginBtn = document.getElementById('login-btn');
        if (loginBtn) {
            loginBtn.textContent = 'Logout';
            loginBtn.href = '#';
            loginBtn.onclick = (e) => { e.preventDefault(); auth.logout(); };
        }
        
        const signupBtn = document.getElementById('signup-btn');
        if (signupBtn) {
            signupBtn.textContent = 'Dashboard';
            signupBtn.href = '#'; // Eventually point to dashboard page/section
        }

        const heroCta = document.getElementById('hero-cta');
        if (heroCta) {
            heroCta.textContent = 'Go to Dashboard →';
            heroCta.href = '#';
        }

        // Fix pricing buttons to not redirect back to register if logged in
        document.querySelectorAll('.pricing-card a.btn-outline, .pricing-card a.btn-primary').forEach(btn => {
            btn.textContent = 'Subscribe Now';
            btn.href = '#pricing';
        });
    }
}

document.addEventListener('DOMContentLoaded', () => {
    handleOAuthRedirect();
    initSmoothScroll();
    initNavbarScroll();
    initScrollAnimations();
    updateUIForAuthState();

    console.log('🚀 FitMY app initialized');
});
