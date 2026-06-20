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

chrome.action.onClicked.addListener((tab) => {
  // Enable the panel only for this specific tab.
  // Other tabs will not have World Lens open.
  chrome.sidePanel.setOptions({
    tabId: tab.id,
    path: "sidepanel.html",
    enabled: true,
  });

  /*          *
   * SAVE URL *
   *          */

  // activeTab is granted on click, so tab.url is populated. Store it for the panel.
  const result = tab.url
    ? tab.url
    : "NO_URL — restricted page or no activeTab grant";

  console.log("[BACKGROUND] tab.url =", tab.url);
  console.log("[BACKGROUND] full tab =", tab);

  chrome.storage.local.set({ pageUrl: result }, () => {
    console.log("[BACKGROUND] saved pageUrl =", result);
  });

  // IMPORTANT: open() must be called synchronously within the user gesture.
  // Do NOT await anything before this line, or the open will be rejected.
  chrome.sidePanel.open({ tabId: tab.id });
});
