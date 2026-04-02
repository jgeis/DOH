
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

// retreive the react entry point container
const reactContainer = document.getElementById("react-entry-point");

// if found observe it for changes
if(reactContainer) {
  resizeObserver.observe(reactContainer);
}
// otherwise note that the container was not found
else {
  console.error("React entrypoint not found. Sizing messages will not be sent.");
}

