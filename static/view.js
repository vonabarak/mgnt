var getTableData = function(url) {
    // console.log('Invoking getTableData');
    var TableData = new XMLHttpRequest();
    TableData.onreadystatechange = function() {
        if(TableData.readyState === 4) {
            var tableInfo = JSON.parse(TableData.responseText);
            var newTabBody = document.createElement('tbody');
            for (row in tableInfo.data) {
                var docRow = document.createElement('tr');
                var t = tableInfo.data[row];
                var elems = [row, t.sname, t.fname, t.pname, t.city, t.phone, t.email, t.comment];
                for (var i=0; i<elems.length; i++) {
                    var docElement = document.createElement('td');
                    docRow.appendChild(docElement);
                    docElement.textContent = elems[i];
                }
                var delButtonTd = document.createElement('td');
                var delButton = document.createElement('button');
                delButton.textContent = 'Del';
                delButton.onclick = function() {
                    var delRequest = new XMLHttpRequest();
                    delRequest.open("GET", "/api/comments/?action=del&id="+this.id);
                    delRequest.send();
                };
                delButton.setAttribute("id", row);
                delButtonTd.appendChild(delButton);
                docRow.appendChild(delButtonTd);
                newTabBody.appendChild(docRow);
            }
            oldTabBody = document.getElementById("viewtabbody");
            if (oldTabBody != null) {
                oldTabBody.parentNode.removeChild(oldTabBody);
            }
            newTabBody.setAttribute("id", "viewtabbody");
            table1 = document.getElementById("viewtable");
            table1.appendChild(newTabBody);
        }
    };

    TableData.open("GET", url, true);
    TableData.send();
};

function onload() {
    var url = "/api/comments/";
    getTableData(url);
    window.setInterval(function(){
            getTableData(url)
    }, 1000);
}
