function toggle(){
	var x = document.getElementById("ipass");
	if (x.type === "password") {
		x.type = "text";
	} else {
		x.type = "password";
	}
}