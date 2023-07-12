function setupErrorHandling (iframeId) {
        var iframe = document.getElementById(iframeId);

        var interval = setInterval(function () {
            iframe.contentWindow.postMessage('checkError', '*');
        }, 5000); // Check every 5 seconds

        window.addEventListener('message', function (event) {
            if (event.source === iframe.contentWindow && event.data === 'error') {
                clearInterval(interval);
                iframe.src = iframe.src; // Reload the iframe
            }
        });
}

function reloadIframe(iframeId) {
    var iframe = document.getElementById(iframeId);
    iframe.src = iframe.src; // Reload the iframe

}
