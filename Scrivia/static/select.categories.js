/*!
****************************************************************************
 * SCRIVIA - DRAWING AND TRIVIA GAME
 * select.categories.js
 *
 * Webprogrammeren en Databases IK
 * Sava Arbutina, Noah Milidragović, Rogier Wesseling, Nick Duijm
 *
 * This script shows and hides categories depending on what you have selected from the drop-down menu.
****************************************************************************
*/

// Only shows the combined points leaderboard when the page is loaded
window.onload = function () {
    document.getElementById("animals").style.display = "none";
    document.getElementById("video_games").style.display = "none";
    document.getElementById("comics").style.display = "none";
    document.getElementById("celebrities").style.display = "none";
    document.getElementById("general_knowledge").style.display = "none";
}

// Chooses which category to show or hide depending on the selected category
function onCategorySelect() {
    var category = document.getElementById("categories").value;
    if (category == "animals") {
        document.getElementById("animals").style.display = "";
        document.getElementById("video_games").style.display = "none";
        document.getElementById("comics").style.display = "none";
        document.getElementById("celebrities").style.display = "none";
        document.getElementById("general_knowledge").style.display = "none";
        document.getElementById("combined").style.display = "none";
    }
    else if (category == "video_games") {
        document.getElementById("animals").style.display = "none";
        document.getElementById("video_games").style.display = "";
        document.getElementById("comics").style.display = "none";
        document.getElementById("celebrities").style.display = "none";
        document.getElementById("general_knowledge").style.display = "none";
        document.getElementById("combined").style.display = "none";
    }
    else if (category == "comics") {
        document.getElementById("animals").style.display = "none";
        document.getElementById("video_games").style.display = "none";
        document.getElementById("comics").style.display = "";
        document.getElementById("celebrities").style.display = "none";
        document.getElementById("general_knowledge").style.display = "none";
        document.getElementById("combined").style.display = "none";
    }
    else if (category == "celebrities") {
        document.getElementById("animals").style.display = "none";
        document.getElementById("video_games").style.display = "none";
        document.getElementById("comics").style.display = "none";
        document.getElementById("celebrities").style.display = "";
        document.getElementById("general_knowledge").style.display = "none";
        document.getElementById("combined").style.display = "none";
    }
    else if (category == "general_knowledge") {
        document.getElementById("animals").style.display = "none";
        document.getElementById("video_games").style.display = "none";
        document.getElementById("comics").style.display = "none";
        document.getElementById("celebrities").style.display = "none";
        document.getElementById("general_knowledge").style.display = "";
        document.getElementById("combined").style.display = "none";
    }
    else {
        document.getElementById("animals").style.display = "none";
        document.getElementById("video_games").style.display = "none";
        document.getElementById("comics").style.display = "none";
        document.getElementById("celebrities").style.display = "none";
        document.getElementById("general_knowledge").style.display = "none";
        document.getElementById("combined").style.display = "";
    }
}