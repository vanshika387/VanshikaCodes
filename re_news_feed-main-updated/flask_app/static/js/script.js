// document.addEventListener('DOMContentLoaded', () => {
//     console.log('JavaScript loaded');
    
//     // Event delegation for checkbox changes
//     document.querySelector('.news-table').addEventListener('change', function(event) {
//         if (event.target.classList.contains('useful-checkbox')) {
//             const checkbox = event.target;
//             const linkId = checkbox.dataset.linkId;
//             const isUseful = checkbox.checked;
            
//             // Update the label immediately for better UX
//             const label = checkbox.nextElementSibling;
//             label.textContent = isUseful ? 'YES' : 'NO';
            
//             // Send update to server
//             updateUsefulStatus(linkId, isUseful);
//         }
//     });

//     // Initialize checkboxes based on their data attributes
//     function initializeCheckboxes() {
//         const checkboxes = document.querySelectorAll('.useful-checkbox');
//         checkboxes.forEach(checkbox => {
//             const label = checkbox.nextElementSibling;
//             label.textContent = checkbox.checked ? 'YES' : 'NO';
//         });
//     }

//     function updateUsefulStatus(linkId, isUseful) {
//         fetch('/update_useful', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//             },
//             body: JSON.stringify({
//                 link_id: linkId,
//                 useful: isUseful
//             })
//         })
//         .then(response => response.json())
//         .then(data => {
//             if (!data.success) {
//                 console.error('Failed to update useful status:', data.error);
//                 // Revert the checkbox if update failed
//                 const checkbox = document.querySelector(`[data-link-id="${linkId}"]`);
//                 if (checkbox) {
//                     checkbox.checked = !isUseful;
//                     const label = checkbox.nextElementSibling;
//                     label.textContent = checkbox.checked ? 'YES' : 'NO';
//                 }
//             }
//         })
//         .catch(error => {
//             console.error('Error:', error);
//             // Revert the checkbox if request failed
//             const checkbox = document.querySelector(`[data-link-id="${linkId}"]`);
//             if (checkbox) {
//                 checkbox.checked = !isUseful;
//                 const label = checkbox.nextElementSibling;
//                 label.textContent = checkbox.checked ? 'YES' : 'NO';
//             }
//         });
//     }

//     // Initialize checkboxes when page loads
//     initializeCheckboxes();
// });

document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript loaded');
    
    // Event delegation for checkbox changes
    document.querySelector('.news-table').addEventListener('change', function(event) {
        if (event.target.classList.contains('useful-checkbox')) {
            const checkbox = event.target;
            const linkId = checkbox.dataset.linkId;
            const isUseful = checkbox.checked;
            
            // Get the headline from the table row
            const headline = checkbox.closest('tr').querySelector('td:nth-child(3)').textContent;
            
            // Show confirmation dialog
            const userConfirmed = confirm(`Do you want to mark this article as useful?\n\n"${headline}"`);
            
            if (userConfirmed) {
                // Update the label immediately for better UX
                const label = checkbox.nextElementSibling;
                label.textContent = isUseful ? 'YES' : 'NO';
                
                // Send update to server
                updateUsefulStatus(linkId, isUseful);
            } else {
                // Revert the checkbox if user cancels
                checkbox.checked = !isUseful;
                return false;
            }
        }
    });

    function updateUsefulStatus(linkId, isUseful) {
        fetch('/update_useful', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                link_id: linkId,
                useful: isUseful
            })
        })
        .then(response => response.json())
        .then(data => {
            if (!data.success) {
                console.error('Failed to update useful status:', data.error);
                // Revert the checkbox if update failed
                const checkbox = document.querySelector(`[data-link-id="${linkId}"]`);
                if (checkbox) {
                    checkbox.checked = !isUseful;
                    const label = checkbox.nextElementSibling;
                    label.textContent = checkbox.checked ? 'YES' : 'NO';
                }
            }
        })
        .catch(error => {
            console.error('Error:', error);
            // Revert the checkbox if request failed
            const checkbox = document.querySelector(`[data-link-id="${linkId}"]`);
            if (checkbox) {
                checkbox.checked = !isUseful;
                const label = checkbox.nextElementSibling;
                label.textContent = checkbox.checked ? 'YES' : 'NO';
            }
        });
    }

    // Initialize checkboxes based on their data attributes
    function initializeCheckboxes() {
        const checkboxes = document.querySelectorAll('.useful-checkbox');
        checkboxes.forEach(checkbox => {
            const label = checkbox.nextElementSibling;
            label.textContent = checkbox.checked ? 'YES' : 'NO';
        });
    }

    // Initialize checkboxes when page loads
    initializeCheckboxes();
});

document.addEventListener('DOMContentLoaded', () => {
    console.log('JavaScript loaded');
    
    const viewUsefulBtn = document.getElementById('view-useful-btn');
    const downloadCsvBtn = document.getElementById('download-csv-btn');
    const showAllBtn = document.getElementById('show-all-btn');
    const newsTable = document.querySelector('.news-table');
    
    // Toggle between showing all articles and only useful ones
    viewUsefulBtn.addEventListener('click', () => {
        const rows = newsTable.querySelectorAll('tbody tr');
        let hasUsefulArticles = false;
        
        rows.forEach(row => {
            const checkbox = row.querySelector('.useful-checkbox');
            if (checkbox && checkbox.checked) {
                row.style.display = '';
                hasUsefulArticles = true;
            } else {
                row.style.display = 'none';
            }
        });
        
        if (hasUsefulArticles) {
            viewUsefulBtn.style.display = 'none';
            showAllBtn.style.display = '';
        }
    });
    
    // Show all articles
    showAllBtn.addEventListener('click', () => {
        const rows = newsTable.querySelectorAll('tbody tr');
        rows.forEach(row => row.style.display = '');
        
        showAllBtn.style.display = 'none';
        viewUsefulBtn.style.display = '';
    });
    
    // Download CSV functionality
    downloadCsvBtn.addEventListener('click', () => {
        const usefulArticles = [];
        const rows = newsTable.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const checkbox = row.querySelector('.useful-checkbox');
            if (checkbox && checkbox.checked) {
                const cells = row.querySelectorAll('td');
                usefulArticles.push({
                    source: cells[0].textContent.trim(),
                    location: cells[1].textContent.trim(),
                    headline: cells[2].textContent.trim(),
                    date: cells[3].textContent.trim(),
                    link: cells[4].querySelector('a').href
                });
            }
        });
        
        if (usefulArticles.length === 0) {
            alert('No useful articles selected!');
            return;
        }
        
        // Convert to CSV
        const headers = ['Source', 'Location', 'Headline', 'Date', 'Link'];
        const csvRows = [
            headers.join(','),
            ...usefulArticles.map(article => 
                `"${article.source}","${article.location}","${article.headline}","${article.date}","${article.link}"`
            )
        ];
        
        const csvContent = csvRows.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        
        link.setAttribute('href', url);
        link.setAttribute('download', 'useful_articles.csv');
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    });
    
    // Your existing checkbox and other event handlers...
    // ... (keep all your existing code for checkbox handling)
});