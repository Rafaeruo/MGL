// ajax for updating the score and status on user input
var url = window.location.href;

var aud_btns = document.querySelectorAll(".AUD-button");

aud_btns.forEach(item => {
    switch (item.id) {
        case "add":
            item.addEventListener("click", addF);
            break;
        case "update":
            item.addEventListener("click", updateF);
            break;
        case "delete":
            item.addEventListener("click", removeF);
            break;
    }
});

function addF() {
    let xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
            // XMLHttpRequest.DONE == 4
            if (xmlhttp.status == 200) {
                document.querySelector(
                    "#game-page-info-options"
                ).innerHTML = this.response;
                document
                    .querySelector("#update")
                    .addEventListener("click", updateF);
                document
                    .querySelector("#delete")
                    .addEventListener("click", removeF);
            } else if (xmlhttp.status == 400) {
                alert("There was an error 400");
            } else {
                alert("something else other than 200 was returned");
            }
        }
    };
    let status = document.querySelector("#game-page-info-status").value;
    let score = document.querySelector("#game-page-info-score").value;
    let data = JSON.stringify({ action: "0", status: status, score: score });
    xmlhttp.open("POST", url);
    xmlhttp.send(data);
}

function updateF() {
    let xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
            // XMLHttpRequest.DONE == 4
            if (xmlhttp.status == 200) {
                document.querySelector(
                    "#game-page-info-options"
                ).innerHTML = this.response;
                document
                    .querySelector("#update")
                    .addEventListener("click", updateF);
                document
                    .querySelector("#delete")
                    .addEventListener("click", removeF);
            } else if (xmlhttp.status == 400) {
                alert("There was an error 400");
            } else {
                alert("something else other than 200 was returned");
            }
        }
    };
    let status = document.querySelector("#game-page-info-status").value;
    let score = document.querySelector("#game-page-info-score").value;
    let data = JSON.stringify({ action: "1", status: status, score: score });
    xmlhttp.open("POST", url);
    xmlhttp.send(data);
}

function removeF() {
    let xmlhttp = new XMLHttpRequest();

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
            // XMLHttpRequest.DONE == 4
            if (xmlhttp.status == 200) {
                document.querySelector(
                    "#game-page-info-options"
                ).innerHTML = this.response;
                document.querySelector("#add").addEventListener("click", addF);
            } else if (xmlhttp.status == 400) {
                alert("There was an error 400");
            } else {
                alert("something else other than 200 was returned");
            }
        }
    };
    let status = document.querySelector("#game-page-info-status");
    let score = document.querySelector("#game-page-info-score");
    let data = JSON.stringify({ action: "2" });
    xmlhttp.open("POST", url);
    xmlhttp.send(data);
}

var summary = document.querySelector("#game-page-info-summary");

if (summary.innerHTML.length > 300) {
    summary.innerHTML =
        summary.innerHTML.substr(0, 300) +
        "<span id='dododot'>...</span><span id='more' hidden>" +
        summary.innerHTML.substr(301, summary.innerHTML.length - 1) +
        "</span>&nbsp&nbsp<a id='more-btn'>View more</a>";
    var dododot = document.querySelector("#dododot");
    var more = document.querySelector("#more");
    var more_btn = document.querySelector("#more-btn");

    more_btn.addEventListener("click", () => {
        if (more.hidden) {
            more.hidden = false;
            dododot.hidden = true;
            more_btn.innerHTML = "View less";
        } else {
            more.hidden = true;
            dododot.hidden = false;
            more_btn.innerHTML = "View more";
        }
    });
}
