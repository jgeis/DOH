
function sendHeightToParent() {
  const height = document.documentElement.getBoundingClientRect().height;

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
const visContainer = document.getElementById("_dash-app-content");

// if found observe it for changes
if(visContainer) {
  resizeObserver.observe(existingContainer);
}
// otherwise set up mutation observer and check for the container creation
else {
  const mutationObserver = new MutationObserver((mutations, observerInstance) => {
    // body was mutated, check if container exists now
    const visContainer = document.getElementById("_dash-app-content");
    // if it does disconnect the mutation observer and observe container for changes
    if(visContainer) {
      observerInstance.disconnect();
      resizeObserver.observe(visContainer);
    }
  });

  mutationObserver.observe(document.body, {
    childList: true,
    subtree: true
  });
}

