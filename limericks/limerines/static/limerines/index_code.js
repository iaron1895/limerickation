var i = 0;
var txt = 'Welcome.';
var speed = 200;

function typeWriter() {
    if (i < txt.length) {
        document.getElementById("welcome").innerHTML += txt.charAt(i);
        i++;
        setTimeout(typeWriter, speed);
    }
}

window.onload = function() {
    typeWriter();
    document.getElementById("buttons").classList.add("fadeIn");
};