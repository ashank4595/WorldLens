// Side panel appears only on the tab where user clicked World Lens
// Switch tabs → panel hides
// Return to original tab → panel comes back
// TODO: Store page data separately for each tab so reopening an older tab shows
// its own URL and results. For now, storage is shared globally, so opening
// the extension on a new tab overwrites the previous tab's data.

/*            *
 * SIDE PANEL *
 *            */

// Undo the previously-persisted "open panel on action click" behavior.
// While that's true, Chrome auto-opens the panel and SUPPRESSES onClicked,
// so we never get the activeTab grant. Forcing it false makes onClicked fire.
chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });

// Disable the panel by default for every tab.
// We will enable it only for the tab where the user clicks the extension.
chrome.sidePanel.setOptions({ enabled: false });

chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });

  // Keep the side panel disabled by default after install/reload.
  chrome.sidePanel.setOptions({ enabled: false });
});

//ON CLICKED FUNCTION
chrome.action.onClicked.addListener((tab) => {
  // Enable the panel only for this specific tab.
  // Other tabs will not have World Lens open.
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true,
  });

  /* SAVE PAGE URL *
   * AND TITLE     *
   * TO LOCAL      */
  const pageUrl = tab.url
    ? tab.url
    : "NO_URL — restricted page or no activeTab grant";

  // let pageUrl;
  // if (tab.url) {
  //   pageUrl = tab.url;
  // } else {
  //   pageUrl = "NO_URL — restricted page or no activeTab grant";
  // }

  const pageTitle = tab.title ? tab.title : "NO_TITLE";

  // Prints to service worker console for debugging.
  console.log("[BACKGROUND] tab.url =", tab.url);
  console.log("[BACKGROUND] full tab =", tab);

  // Saves URL and page title to local storage as pageUrl and pageTitle
  chrome.storage.local.set(
    {
      pageUrl,
      pageTitle,
    },
    () => {
      console.log("[BACKGROUND] saved pageUrl =", pageUrl);
      console.log("[BACKGROUND] saved pageTitle =", pageTitle);
    },
  );

  // Open side panel when tabId = tab.id.
  // IMPORTANT: open() must be called synchronously within the user gesture.
  // Do NOT await anything before this line, or the open will be rejected.
  chrome.sidePanel.open({ tabId: tab.id });
});
