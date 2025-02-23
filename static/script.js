function getVideoId(url) {
    const urlObj = new URL(url);
    if (urlObj.hostname === 'youtu.be') {
        return urlObj.pathname.slice(1);
    }
    if (urlObj.hostname.includes('youtube.com')) {
        return urlObj.searchParams.get('v');
    }
    return null;
}
// Add this at the top of your script file
marked.setOptions({
    gfm: true,
    breaks: true,
    sanitize: true
});

async function summarize() {
    const videoUrl = document.getElementById('video-url').value;
    const loading = document.getElementById('loading');
    const result = document.getElementById('result');

    if (!videoUrl) {
        alert('Please enter a YouTube URL');
        return;
    }

    try {
        const videoId = getVideoId(videoUrl);
        if (!videoId) {
            alert('Invalid YouTube URL');
            return;
        }

        loading.classList.remove('hidden');
        result.textContent = '';

        const response = await fetch('/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ video_url: videoId })
        });

        const data = await response.json();

        // In the summarize function, where you handle the response:
        if (data.error) {
            result.textContent = data.error;
        } else {
            const htmlContent = marked.parse(data.summary);
            result.innerHTML = htmlContent;
            // Add classes to lists for proper styling
            result.querySelectorAll('ul').forEach(ul => ul.classList.add('summary-list'));
        }
    } catch (error) {
        result.textContent = 'An error occurred while processing your request.';
    } finally {
        loading.classList.add('hidden');
    }
}