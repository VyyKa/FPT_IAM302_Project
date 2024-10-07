document.getElementById('dark-mode-toggle').addEventListener('click', function() {
    const isDarkMode = document.body.classList.toggle('dark-mode');
    
    // Change the icon based on the current mode
    const icon = isDarkMode ? 'sun-icon.svg' : 'moon-icon.svg';
    this.querySelector('img').src = `{{ url_for('static', filename='images/${icon}') }}`;
    
    // Save mode in localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
});

// Apply saved theme on page load
window.addEventListener('DOMContentLoaded', (event) => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        document.getElementById('dark-mode-toggle').querySelector('img').src = '/static/images/sun-icon.svg';
    }
});
