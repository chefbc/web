(function() {
    async function initAnnouncements() {
        const bar = document.getElementById('announcement-bar');
        if (!bar) return;

        // Check if user has dismissed announcements
        if (localStorage.getItem('announcements-dismissed')) {
            return;
        }

        try {
            // Find the correct base path for the JSON file
            const scriptTag = document.querySelector('script[src*="announcements.js"]');
            const basePath = scriptTag.src.replace('assets/javascripts/announcements.js', '');
            
            const response = await fetch(`${basePath}assets/announcements.json`);
            if (!response.ok) return;

            const announcements = await response.json();
            const now = new Date();
            const todayStr = now.toISOString().split('T')[0];

            const activeAnnouncements = announcements.filter(ann => {
                const start = ann.start_date || '0000-00-00';
                const end = ann.end_date || '9999-99-99';
                return todayStr >= start && todayStr <= end;
            });

            if (activeAnnouncements.length > 0) {
                const contentArea = bar.querySelector('.announcement-content');
                contentArea.innerHTML = '';

                activeAnnouncements.forEach(ann => {
                    const annDiv = document.createElement('div');
                    annDiv.className = 'announcement-item';
                    
                    if (ann.color) {
                        annDiv.style.backgroundColor = ann.color;
                    }

                    if (ann.html) {
                        annDiv.innerHTML = ann.html;
                    } else if (ann.text) {
                        annDiv.textContent = ann.text;
                    }

                    contentArea.appendChild(annDiv);
                });

                bar.style.display = 'block';

                // Add dismissal listener
                const dismissBtn = bar.querySelector('.announcement-dismiss');
                if (dismissBtn) {
                    dismissBtn.addEventListener('click', () => {
                        bar.style.display = 'none';
                        localStorage.setItem('announcements-dismissed', 'true');
                    });
                }
            } else {
                bar.style.display = 'none';
            }
        } catch (error) {
            console.error('Error loading announcements:', error);
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAnnouncements);
    } else {
        initAnnouncements();
    }
})();
