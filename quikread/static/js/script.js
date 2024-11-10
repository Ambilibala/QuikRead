// static/js/scripts.js
// Get the button
var mybutton = document.getElementById("topBtn");
// When the user scrolls down 20px from the top of the document, show the button
window.onscroll = function() {scrollFunction()};
function scrollFunction() {
    if (document.body.scrollTop > 20 || document.documentElement.scrollTop > 20) {
        mybutton.style.display = "block";
    } else {
        mybutton.style.display = "none";
    }
}
// When the user clicks on the button, scroll to the top of the document
mybutton.onclick = function() {
    document.body.scrollTop = 0;
    document.documentElement.scrollTop = 0;
}
// Navbar burger menu
document.addEventListener('DOMContentLoaded', () => {
    const burger = document.querySelector('#navbarBurger');
    const menu = document.querySelector('#navbarMenu');
    
    burger?.addEventListener('click', () => {
        burger.classList.toggle('is-active');
        menu.classList.toggle('is-active');
    });

    // Close notification messages
    document.querySelectorAll('.notification .delete').forEach(button => {
        button.addEventListener('click', () => {
            button.parentElement.remove();
        });
    });

    // Scroll to top button
    const topButton = document.querySelector('#topBtn');
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            topButton.style.display = 'block';
        } else {
            topButton.style.display = 'none';
        }
    });

    topButton.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
});