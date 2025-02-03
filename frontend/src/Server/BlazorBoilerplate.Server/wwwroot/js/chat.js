window.scrollChatToBottom = (element) => {
    if (element && element instanceof HTMLElement) {
        console.log("Scrolling to bottom...");
        console.log("Element received:", element);

        setTimeout(() => {
            element.scrollTop = element.scrollHeight;
            console.log("Scroll action completed.");
        }, 100); // Adding a short delay for better reliability
    } else {
        console.error("Invalid element reference passed to scrollChatToBottom");
    }
};
