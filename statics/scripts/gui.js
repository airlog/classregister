display_type = new Array();
function changeVisibility(id) {
	element = document.getElementById(id);
	if (element.style.display == "none") {
		element.style.display=display_type[id];
	}
	else {
		display_type[id] = element.style.display;
		element.style.display="none";
	}
}

function hide(className) {
	elements = document.getElementsByClassName(className);
	for (i = 0; i < elements.length; i++) changeVisibility(elements[i].id);
}
