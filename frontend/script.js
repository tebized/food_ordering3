// Wait for the window to load before running the script
window.onload = function () {
  // Get references to the splash screen and the main content elements
  const splashScreen = document.getElementById("splash-screen");
  const mainContent = document.getElementById("main-content");

  // Set a timer for 3 seconds (3000 milliseconds)
  setTimeout(() => {
    // After 3 seconds, start fading out the splash screen
    splashScreen.style.opacity = "0";

    // Wait for the fade-out transition to finish before showing main content
    setTimeout(() => {
      // Hide the splash screen
      splashScreen.style.display = "none";

      // Show the main content with "Get started" button
      mainContent.classList.remove("hidden");
      mainContent.style.display = "block";
    }, 500); // This should match the CSS transition duration
  }, 3000); // Show splash screen for 3 seconds
};
