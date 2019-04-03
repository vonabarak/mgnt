function onAddButtonClick() {
    // console.log('hello');
    var snameField = document.getElementById("sname");
    var fnameField = document.getElementById("fname");
    var pnameField = document.getElementById("pname");
    var regionField = document.getElementById("region");
    var cityField = document.getElementById("city");
    var phoneField = document.getElementById("phone");
    var emailField = document.getElementById("email");
    var commentField = document.getElementById("comment");
    var allFields = [snameField, fnameField, pnameField, regionField, cityField, phoneField, emailField, commentField];

    var commentRequest = new XMLHttpRequest();
    commentRequest.onreadystatechange = function () {
        if (commentRequest.readyState === 4){
            var responseData = JSON.parse(commentRequest.responseText);

            // remove red borders from all fields
            for (var i=0; i<allFields.length; i++){
                allFields[i].style = "";
            }
            if (responseData.error === false) {
                console.log('Comment successfully added');
                var log = document.createElement('p');
                log.innerText = "Комментарий добавлен";
                var logs = document.getElementById("log");
                logs.appendChild(log);
            } else {
                // set red border for malformed field
                var malformedField = document.getElementById(responseData.error.replace(/['"]+/g, ''));
                malformedField.style = "border:2px solid #ff0000";
            }
        }
    }
    var sname = snameField.value;
    var fname = fnameField.value;
    var pname = pnameField.value;
    var region = regionField.options[regionField.selectedIndex].value;
    var city = cityField.options[cityField.selectedIndex].value;
    var phone = phoneField.value;
    var email = emailField.value;
    var comment = commentField.value;

    commentRequest.open("GET",
        "/api/comments/?action=add&"+
        "sname="+sname+
        "&fname="+fname+
        "&pname="+pname+
        "&region="+region+
        "&city="+city+
        "&phone="+phone+
        "&email="+email+
        "&comment="+comment
    );
    commentRequest.send();
}

function onRegionChange() {
    // setting options for city field
    var regionField = document.getElementById("region");
    var cityField = document.getElementById("city");
    var selected = regionField.options[regionField.selectedIndex].value;
    var cityRequest = new XMLHttpRequest();
    cityRequest.onreadystatechange = function () {
        if (cityRequest.readyState === 4) {
            responseData = JSON.parse(cityRequest.responseText);
            // console.log(responseData.data);
            for (option in responseData.data) {
                var newCityOption = new Option(responseData.data[option], option, false, false);
                cityField.appendChild(newCityOption);
            }
        }
    }
    // remove all old options from city field
    while (cityField.firstChild) {
        cityField.removeChild(cityField.firstChild);
    }
    cityRequest.open("GET", "/api/cities/?region="+selected);
    cityRequest.send();
}

function onload() {
    // set options for region field
    var regionField = document.getElementById("region");
    var regionRequest = new XMLHttpRequest();
    regionRequest.onreadystatechange = function() {
        if (regionRequest.readyState === 4) {
            responseData = JSON.parse(regionRequest.responseText);
            for (option in responseData.data) {
                var newOption = new Option(responseData.data[option], option, false, false);
                regionField.appendChild(newOption)
            }
            // set options for city field for first time (will be triggered on region change)
            onRegionChange();
        }
    };
    regionRequest.open("GET", "/api/regions/");
    regionRequest.send();
}
