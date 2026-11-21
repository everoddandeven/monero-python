// The entries of the tabs and of the navigation that leave the site, as the Changelog to the releases on GitHub, open in a new tab:
// Material has no option for it. document$ is the observable of Material that emits for each page it shows, also with
// navigation.instant, which replaces the page without loading it again.
document$.subscribe(function () {
  document.querySelectorAll("a.md-tabs__link, a.md-nav__link").forEach(function (link) {
    if (link.hostname && link.hostname !== window.location.hostname) {
      link.target = "_blank";
      link.rel = "noopener";
    }
  });
});
