

window.anchorLink = {
    init: function (anchorId) {
        var elem = document.getElementById(anchorId);
        if (elem) {
            elem.setAttribute("onclick", "return false;");
        }
    },
    scrollIntoView: function (elementId) {
        var elem = document.getElementById(elementId);
        if (elem) {
            elem.scrollIntoView();
            window.location.hash = elementId;
        }
    }
};
