document.addEventListener('DOMContentLoaded', function() {
    const darkModeToggle = document.getElementById('dark-mode-toggle');

    if (darkModeToggle) {  // Ensure the toggle button exists
        darkModeToggle.addEventListener('click', function() {
            const isDarkMode = document.body.classList.toggle('dark-mode');
            
            // Update the icon based on the current mode
            const icon = isDarkMode ? 'sun-icon.svg' : 'moon-icon.svg';
            this.querySelector('img').src = `/static/images/${icon}`;
            
            // Save the mode in localStorage
            localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
        });

        // Apply the saved theme when the page loads
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            darkModeToggle.querySelector('img').src = '/static/images/sun-icon.svg';
        }
    }
});