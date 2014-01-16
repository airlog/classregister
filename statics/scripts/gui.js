
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

function presanceFormSubmit() {    
    var form = document.getElementById("fnieobecnosc");
    var hiddenDate = document.getElementById("dateInput");
    var input = document.getElementById("absentInput");
    var pattern = /\w+(\d+)/;
    
    /* wyczyść poprzedni stan */
    input.value = "";
    hiddenDate.value = "";
    
    var dateInput = document.getElementById("dateinput");   
    hiddenDate.value = dateInput.value;
    
    console.debug(dateInput);
    console.debug(form);
        
    /* CSV, jeden wiersz, w każdej kolumnie ID nieobecnego ucznia */
    var checkboxes = document.getElementsByClassName("presancestate");
    
    var absent = 0;
    for (var i = 0; i < checkboxes.length; i++) {
        var cb = checkboxes.item(i);
        if (!cb.checked) continue;
        
        var id = cb.name.match(pattern)[1];
        input.value += id + ",";
        absent++;
    }
     
    if (absent > 0 && dateInput.value) form.submit();
}

function degreeFormSubmit() {    
    var form = document.getElementById("focena");
    var hiddenDate = document.getElementById("dateInputDegree");
    var opis = document.getElementById("opisoceny");
    var input = document.getElementById("degreeInput");
    var pattern = /\w+(\d+)/;
    
    /* wyczyść poprzedni stan */
    input.value = "";
    hiddenDate.value = "";
    
    var dateInput = document.getElementById("dateinput");   
    hiddenDate.value = dateInput.value;
    
    /* CSV, wiele wierszy, dwie kolumny: uczenId,ocena */
    var selects = document.getElementsByClassName("degreestate");
    
    var degrees = 0;
    for (var i = 0; i < selects.length; i++) {
        var sl = selects.item(i);
        if (sl.value == "") continue;
        
        var id = sl.name.match(pattern)[1];
        input.value += id + "," + sl.value + "\n";
        degrees++;
    }
    
    if (degrees > 0 && opis.value.length > 3 && dateInput.value) form.submit();
}

