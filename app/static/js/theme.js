/**
 * Theme Toggle Functionality
 * Handles dark/light mode switching
 */

(function() {
    'use strict';
    
    function initTheme() {
        const html = document.documentElement;
        const themeIcon = document.getElementById('themeIcon');
        
        // Get saved theme or default to light
        const savedTheme = localStorage.getItem('theme') || 'light';
        
        // Set theme attribute immediately
        html.setAttribute('data-theme', savedTheme);
        
        // Update icon
        if (themeIcon) {
            if (savedTheme === 'dark') {
                themeIcon.className = 'bi bi-moon-fill';
            } else {
                themeIcon.className = 'bi bi-sun-fill';
            }
        }
        
        console.log('Theme initialized:', savedTheme);
    }
    
    function setupThemeToggle() {
        const themeToggle = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const html = document.documentElement;
        
        if (!themeToggle) {
            console.warn('Theme toggle button not found');
            return;
        }
        
        if (!themeIcon) {
            console.warn('Theme icon not found');
            return;
        }
        
        // Add click event listener
        themeToggle.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            const currentTheme = html.getAttribute('data-theme') || 'light';
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            // Update theme attribute
            html.setAttribute('data-theme', newTheme);
            
            // Save to localStorage
            localStorage.setItem('theme', newTheme);
            
            // Update icon
            if (newTheme === 'dark') {
                themeIcon.className = 'bi bi-moon-fill';
            } else {
                themeIcon.className = 'bi bi-sun-fill';
            }
            
            console.log('Theme changed to:', newTheme);
        });
    }
    
    // Wait for DOM to be fully loaded
    function initialize() {
        initTheme();
        setupThemeToggle();
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        // DOM already loaded, but wait a bit to ensure all elements are ready
        setTimeout(initialize, 100);
    }
})();

