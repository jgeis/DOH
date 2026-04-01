
function sendHeightToParent() {
  const height = document.documentElement.scrollHeight;

  // post message with target origin as bh808 site
  window.parent.postMessage({
    messageType: "IFrameHeight",
    height: height
  }, "https://bh808.hawaii.gov/");
}


const urlParams = new URLSearchParams(window.location.search);

// set up resize observer to stream sizing to parent
const resizeObserver = new ResizeObserver(() => {
  sendHeightToParent();
});

// retreive the vis container created by dash
const visContainer = document.getElementById("content-size-wrapper");

// if found send height to parent and observe it for changes
if(visContainer) {
  sendHeightToParent();
  resizeObserver.observe(existingContainer);
}
// otherwise set up mutation observer and check for the container creation
else {
  const mutationObserver = new MutationObserver((mutations, observerInstance) => {
    // body was mutated, check if container exists now
    const visContainer = document.getElementById("content-size-wrapper");
    // if it does disconnect the mutation observer, send the height to parents, and observe container for changes
    if(visContainer) {
      observerInstance.disconnect();
      
      sendHeightToParent();
      resizeObserver.observe(visContainer);
    }
  });

  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
}

