/* jQuery & Velocity.js for Animations */
function slideUpIn() {
  $("#login").velocity("transition.slideUpIn", 1250)
};

function slideLeftIn() {
  $(".row").delay(500).velocity("transition.slideLeftIn", {stagger: 500})    
}

function shake() {
  $(".password-row").velocity("callout.shake");
}

slideUpIn();
slideLeftIn();
$("button").on("click", function () {
  shake();
});

/*Login form - Username styling */
const usrname = document.getElementById("id_username");
usrname.classList.add("username");
usrname.placeholder="Username";
$('#id_username').attr('aria-label', 'Username');

/*Login form - Password styling */
const passwd = document.getElementById("id_password");
passwd.classList.add("password");
passwd.placeholder="Password";
$('#id_password').attr('aria-label', 'Password');