/*                 *
 * EXTRACT WEBPAGE *
 * TEXT + HEADLINE *
 *                 */

(() => {
  const headlineElement = document.querySelector("h1");

  const pageHeadline =
    headlineElement?.innerText || document.title || "NO_HEADLINE";

  const articleElement =
    document.querySelector("article") ||
    document.querySelector("main") ||
    document.querySelector('[role="main"]') ||
    document.body;

  const pageText = articleElement.innerText || "";

  console.log("[CONTENT] pageHeadline =", pageHeadline);
  console.log("[CONTENT] pageText length =", pageText.length);

  chrome.runtime.sendMessage({
    type: "PAGE_CONTENT_EXTRACTED",
    pageHeadline,
    pageText,
  });
})();
