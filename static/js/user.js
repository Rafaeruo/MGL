window.onload = () => {
    var username_input = document.querySelector("#user-search-input");
    document
        .querySelector("#user-search-button")
        .addEventListener("click", () => {
            if (username_input.value != "") {
                window.location.href = `${username_input.value}`;
            }
        });

    let xmlhttp = new XMLHttpRequest();
    let url = window.location.href;

    let list5 = "";
    let list4 = "";
    let list3 = "";
    let list2 = "";
    let list1 = "";
    let list0 = "";

    xmlhttp.onreadystatechange = function () {
        if (xmlhttp.readyState == XMLHttpRequest.DONE) {
            // XMLHttpRequest.DONE == 4
            if (xmlhttp.status == 200) {
                let r = JSON.parse(this.response);
                let api_info = r[0];
                let db_info = r[1];

                if (api_info == null || db_info == null) {
                    document.querySelector("#user-page-list-div").innerHTML =
                        "<h2>Game list:</h2><p>This user's list is empty.</p>";
                    document.querySelector("#user-page-stats-inner").innerHTML =
                        "<p>No stats.</p>";
                    return;
                }

                console.log(api_info);
                console.log(db_info);

                let mean_score = 0;
                let score_ignore = 0;
                let completed = 0;
                let played = 0;
                let playing = 0;
                let plantoplay = 0;
                let notplayed = 0;

                for (i = 0; i < api_info.length; i++) {
                    current_score = db_info[i][1];
                    if (current_score !== "") {
                        mean_score += parseInt(current_score);
                        current_score = `<p id="user-page-list-game-score">Scored: ${current_score}</p>`;
                    } else {
                        current_score = `<p id="user-page-list-game-score">Not scored</p>`;
                        score_ignore += 1;
                    }

                    let current_image;
                    if (api_info[i].hasOwnProperty("cover")) {
                        current_image = `<a href="/game/${
                            api_info[i]["slug"]
                        }"><img id="user-page-list-game-image" src="${api_info[
                            i
                        ]["cover"]["url"].replace("thumb", "logo_med")}"></a>`;
                    } else {
                        current_image =
                            '<p id="user-page-list-game-image">No image</p>';
                    }

                    let current_name = `<a href="/game/${api_info[i]["slug"]}">${api_info[i]["name"]}</a>`;
                    let game = `<div class="user-page-list-game">${current_score}${current_image}${current_name}</div>`;
                    switch (db_info[i][2]) {
                        case 4:
                            list4 += game;
                            completed += 1;
                            break;
                        case 3:
                            list3 += game;
                            played += 1;
                            break;
                        case 2:
                            list2 += game;
                            playing += 1;
                            break;
                        case 1:
                            list1 += game;
                            plantoplay += 1;
                            break;
                        case 0:
                            list0 += game;
                            notplayed += 1;
                            break;
                    }
                    list5 += game;
                }
                //console.log(list5);
                document.querySelector("#user-page-list-5").innerHTML = list5;
                document.querySelector("#user-page-list-4").innerHTML = list4;
                document.querySelector("#user-page-list-3").innerHTML = list3;
                document.querySelector("#user-page-list-2").innerHTML = list2;
                document.querySelector("#user-page-list-1").innerHTML = list1;
                document.querySelector("#user-page-list-0").innerHTML = list0;

                //stats
                if (mean_score != 0) {
                    mean_score = (
                        mean_score /
                        (api_info.length - score_ignore)
                    ).toFixed(1);
                }
                document.querySelector(
                    "#meanscore"
                ).innerHTML = `Mean score: ${mean_score}`;
                document.querySelector(
                    "#count-5"
                ).innerHTML = `Game entries: ${api_info.length}`;
                document.querySelector(
                    "#count-4"
                ).innerHTML = `Completed: ${completed}`;
                document.querySelector(
                    "#count-3"
                ).innerHTML = `Played: ${played}`;
                document.querySelector(
                    "#count-2"
                ).innerHTML = `Playing: ${playing}`;
                document.querySelector(
                    "#count-1"
                ).innerHTML = `Plan to play: ${plantoplay}`;
                document.querySelector(
                    "#count-0"
                ).innerHTML = `Not played: ${notplayed}`;
            } else {
                alert("Couldn't retrieve user game list data");
            }
        }
    };
    xmlhttp.open("POST", url);
    xmlhttp.send();
};
