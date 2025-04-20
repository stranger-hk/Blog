// Main JavaScript file for the blog application

document.addEventListener("DOMContentLoaded", () => {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map((tooltipTriggerEl) => new bootstrap.Tooltip(tooltipTriggerEl))
  
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
      anchor.addEventListener("click", function (e) {
        e.preventDefault()
  
        const target = document.querySelector(this.getAttribute("href"))
        if (target) {
          target.scrollIntoView({
            behavior: "smooth",
          })
        }
      })
    })
  
    // Add active class to current nav item
    const currentLocation = window.location.pathname
    const navLinks = document.querySelectorAll(".navbar-nav .nav-link")
  
    navLinks.forEach((link) => {
      const href = link.getAttribute("href")
      if (href === currentLocation || (href !== "/" && currentLocation.startsWith(href))) {
        link.classList.add("active")
      }
    })
  
    // Handle image loading errors
    document.querySelectorAll("img").forEach((img) => {
      img.addEventListener("error", function () {
        this.src = "https://via.placeholder.com/300x200?text=Image+Not+Found"
      })
    })
  })
  