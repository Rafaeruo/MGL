//center the horizontal scroll bars
var scrolls = document.querySelectorAll(".index-group-list");
for (i = 0; i < scrolls.length; i++) {
    scrolls[i].scrollLeft =
        (scrolls[i].scrollWidth - scrolls[i].offsetWidth) / 2;
}
