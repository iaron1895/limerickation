const limerick_pair_id = JSON.parse(document.getElementById('limerick-pair').textContent);
const limerick_pair2_id = JSON.parse(document.getElementById('limerick-pair2').textContent);
const limerick_user_rank = JSON.parse(document.getElementById('limerick-user-rank').textContent);
const limerick_pair_user_rank = JSON.parse(document.getElementById('limerick-pair-user-rank').textContent);
const limerick_pair2_user_rank = JSON.parse(document.getElementById('limerick-pair2-user-rank').textContent);
const limerick_model_rank = JSON.parse(document.getElementById('limerick-model-rank').textContent);
const limerick_pair_model_rank = JSON.parse(document.getElementById('limerick-pair-model-rank').textContent);
const limerick_pair2_model_rank = JSON.parse(document.getElementById('limerick-pair2-model-rank').textContent)
const previous_lim_id = JSON.parse(document.getElementById('previous-lim-id').textContent);
const next_lim_id = JSON.parse(document.getElementById('next-lim-id').textContent);
const originating_id = JSON.parse(document.getElementById('originating-id').textContent);
const all_limericks = JSON.parse(document.getElementById('all_limericks').textContent);

function editableLimerick() {
    editable = (window.location.href.indexOf("edit") > -1 && window.location.href.indexOf("result") <= -1);
    if(editable) {
        document.getElementById("edit-button").style.visibility = 'visible';
        url_prev = (previous_lim_id != 0) ? "/limerines/limericks/"+previous_lim_id+"/edit" : "#"
        document.getElementById("previous-limerick").setAttribute("href",url_prev) 
        url_next = (next_lim_id != 0) ? "/limerines/limericks/"+next_lim_id+"/edit" : "#"
        document.getElementById("next-limerick").setAttribute("href",url_next) 
    }
}

function resultingLimerick() {
    resulting = window.location.href.indexOf("result") > -1;
    if(!resulting) {
        document.getElementById("navigation-buttons").style.visibility = 'visible';
    }
    else {
        document.getElementById("back-button").style.visibility = 'visible';
        url_back = (originating_id != 0) ? "/limerines/limericks/"+originating_id+"/edit" : "#";
        document.getElementById("originating-limerick").setAttribute("href",url_back);
    }
}

function limerickButtons(show) {
    if(show) {
        document.getElementById("save-button").style.display = '';
        document.getElementById("generate-button").style.display='';
    } 
    else {
        document.getElementById("save-button").style.display = "none";
        document.getElementById("generate-button").style.display="none";
    }
}

function limerickFinal(set) {
    limerick = document.querySelector(".limerick-block-edit");
    (set) ? limerick.style.borderColor = "#7D9D9C" :  limerick.style.borderColor = '#E4DCCF';
    if(set) {
        document.getElementById("o-verse1").value = document.getElementById("original-1").textContent;
        document.getElementById("o-verse3").value = document.getElementById("original-3").textContent;
        document.getElementById("o-verse4").value = document.getElementById("original-4").textContent;
        document.getElementById("o-verse5").value = document.getElementById("original-5").textContent;
        document.getElementById("new-verse1").value = document.getElementById("verse1-current-selection").textContent;
        document.getElementById("new-verse2").value = document.getElementById("verse2-current-selection").textContent;
        document.getElementById("new-verse3").value = (document.getElementById("verse3-option").style.visibility == 'hidden') ? 'hidden' : document.getElementById("verse3-current-selection").textContent;
        document.getElementById("new-verse4").value = (document.getElementById("verse4-option").style.visibility == 'hidden') ? 'hidden' : document.getElementById("verse4-current-selection").textContent;
        document.getElementById("new-verse5").value = (document.getElementById("verse5-option").style.visibility == 'hidden') ? 'hidden' : document.getElementById("verse5-current-selection").textContent;
    }
}

function enableDisableGenderFilter() {
    gender_filter = document.getElementById("gender-switch");
    (!limerick_pair_id) ? gender_filter.classList.toggle("filterDisabled") : gender_filter.addEventListener("click",genderFlipCard);
}

function enableDisablePlaceFilter() {
    place_filter = document.getElementById("place-switch");
    (!limerick_pair2_id) ? place_filter.classList.toggle("filterDisabled") : place_filter.addEventListener("click",placeFlipCard);
}

function flipCard() {
    const card = document.getElementById("card");
    card.classList.toggle("flipCard");
}

function genderFlipCard() {
    gender_filter = document.getElementById("gender-switch");
    gender_filter.classList.toggle("active");
    place_filter = document.getElementById("place-switch");
    if(limerick_pair2_id) place_filter.classList.toggle("filterDisabled");
    pron_filter = document.getElementById("pron-switch");
    pron_filter.classList.toggle("filterDisabled")
    if(gender_filter.classList.contains("active")) {
        pron_filter.removeEventListener("click",pronFlipCard);
        if(limerick_pair2_id) place_filter.removeEventListener("click",placeFlipCard);
        disableVoting();
        document.getElementById("user-rank-display").innerHTML = limerick_pair_user_rank+"/"+all_limericks.length
        document.getElementById("model-rank-display").innerHTML = limerick_pair_model_rank+"/"+all_limericks.length
    }
    else {
        pron_filter.addEventListener("click",pronFlipCard);
        if(limerick_pair2_id) place_filter.addEventListener("click",placeFlipCard);
        enableVoting();
        document.getElementById("user-rank-display").innerHTML = limerick_user_rank+"/"+all_limericks.length
        document.getElementById("model-rank-display").innerHTML = limerick_model_rank+"/"+all_limericks.length
    }
    flipCard();
}

function placeFlipCard() {
    place_filter = document.getElementById("place-switch");
    place_filter.classList.toggle("active");
    current_back = document.getElementById("card-back").innerHTML;
    gender_filter = document.getElementById("gender-switch");
    if(limerick_pair_id) gender_filter.classList.toggle("filterDisabled");
    pron_filter = document.getElementById("pron-switch");
    pron_filter.classList.toggle("filterDisabled")
    to_change = document.getElementById("temp-card-back-pair2").innerHTML;
    if(place_filter.classList.contains("active")) {
        if(limerick_pair_id) gender_filter.removeEventListener("click",genderFlipCard);
        pron_filter.removeEventListener("click",pronFlipCard);
        disableVoting();
        flipCard();
        document.getElementById("user-rank-display").innerHTML = limerick_pair2_user_rank+"/"+all_limericks.length
        document.getElementById("model-rank-display").innerHTML = limerick_pair2_model_rank+"/"+all_limericks.length
        document.getElementById("temp-card-back-pair2").innerHTML = current_back;
        document.getElementById("card-back").innerHTML = to_change;   
    }
    else {
        if(limerick_pair_id) gender_filter.addEventListener("click",genderFlipCard);
        pron_filter.addEventListener("click",pronFlipCard);
        enableVoting();
        flipCard();
        document.getElementById("user-rank-display").innerHTML = limerick_user_rank+"/"+all_limericks.length
        document.getElementById("model-rank-display").innerHTML = limerick_model_rank+"/"+all_limericks.length
        setTimeout(function(){ 
            document.getElementById("card-back").innerHTML = to_change;
            document.getElementById("temp-card-back-pair2").innerHTML = current_back;
        }, 600);
    }
}

function pronFlipCard() {
    pron_filter = document.getElementById("pron-switch");
    pron_filter.classList.toggle("active");
    current_back = document.getElementById("card-back").innerHTML;
    to_change = document.getElementById("temp-card-back").innerHTML;
    gender_filter = document.getElementById("gender-switch");
    if(limerick_pair_id) gender_filter.classList.toggle("filterDisabled");
    place_filter = document.getElementById("place-switch");
    if(limerick_pair2_id) place_filter.classList.toggle("filterDisabled");
    if(pron_filter.classList.contains("active")) {
        if(limerick_pair_id) gender_filter.removeEventListener("click",genderFlipCard);
        if(limerick_pair2_id) place_filter.removeEventListener("click",placeFlipCard);
        document.getElementById("temp-card-back").innerHTML = current_back;
        document.getElementById("card-back").innerHTML = to_change;  
        flipCard();         
    }
    else {
        if(limerick_pair_id) gender_filter.addEventListener("click",genderFlipCard);
        if(limerick_pair2_id) place_filter.addEventListener("click",placeFlipCard);
        flipCard();
        setTimeout(function(){ 
            document.getElementById("card-back").innerHTML = to_change;
            document.getElementById("temp-card-back").innerHTML = current_back;
        }, 600);
    }
}

function vote(upvote) {
    document.getElementById("action_vote").value = upvote;
    document.forms['submit-vote'].submit();
}

function buttonClick() {
    left = document.querySelector(".left");
    container = document.querySelector(".container"); 
    container.classList.toggle("hover-left");
    if(container.classList.contains("hover-left")) {
        document.getElementById("score-button").style.display = 'none';
        document.getElementById("options").style.display = 'none';
        document.getElementById("options-hidden").style.display = 'none';
        document.getElementById("limerick-block").style.width="100%";
        activateClicks();
        setTimeout(function(){ 
            limerickButtons(true);
        }, 300);
        document.getElementById("original-limerick").style.borderColor = '#E4DCCF';
    }
    else {
        document.getElementById("score-button").style.display = '';
        document.getElementById("options").style.display = '';
        document.getElementById("options-hidden").style.display = '';
        document.getElementById("limerick-block").style.width="auto";
        limerickButtons(false);
        document.getElementById("original-limerick").style.borderColor = '#576F72';
    }
}

function activateVerse1() {
    options = document.getElementById("verse1-option");
    options.classList.toggle("active");
    (options.classList.contains("active")) ?  limerickButtons(false) : limerickButtons(true);
}

function activateVerse2() {
    options = document.getElementById("verse2-option");
    options.classList.toggle("active");
    (options.classList.contains("active")) ?  limerickButtons(false) : limerickButtons(true);
}

function activateVerse3() {
    options = document.getElementById("verse3-option");
    options.classList.toggle("active");
    (options.classList.contains("active")) ?  limerickButtons(false) : limerickButtons(true);
}

function activateVerse4() {
    options = document.getElementById("verse4-option");
    options.classList.toggle("active");
    (options.classList.contains("active")) ?  limerickButtons(false) : limerickButtons(true);
}

function activateVerse5() {
    options = document.getElementById("verse5-option");
    options.classList.toggle("active");
    (options.classList.contains("active")) ?  limerickButtons(false) : limerickButtons(true);
}

function verseProperty(verse, original, activationFunction) {
    var default_option = document.getElementById(verse);
    if (original) {
        default_option.onclick = activationFunction;
        default_option.classList.add("default_option");
        default_option.classList.remove("disabled");
    }
    else {
        default_option.onclick = '';
        default_option.classList.add("disabled");
        default_option.classList.remove("default_option");
    }
}

function hideVerse(verse, hide) {
    e =  document.getElementById(verse);
    (hide) ? e.style.visibility = 'hidden' : e.style.visibility = 'visible';
}
const onClickVerse1 = function() {
    document.getElementById("notification").innerHTML = '';
    document.getElementById("verse1-current-selection").innerHTML = this.innerHTML;
    activateVerse1();
    original = (document.getElementById("verse1-current-selection").textContent == document.getElementById("original-1").textContent);
    new_limerick = canSave();
    can_dropdown = true;
    if(!original && new_limerick) can_dropdown = false;
    verseProperty("verse2-current-parent",can_dropdown,activateVerse2);
    verseProperty("verse3-current-parent",can_dropdown,activateVerse3);
    verseProperty("verse4-current-parent",can_dropdown,activateVerse4);
    verseProperty("verse5-current-parent",can_dropdown,activateVerse5);
    document.getElementById("save-button").querySelector('button').disabled = can_dropdown;
    limerickFinal(!can_dropdown);
    if(!new_limerick) {
        notify();
    }
}

const onClickVerse2 = function() {
    document.getElementById("notification").innerHTML = '';
    document.getElementById("verse2-current-selection").innerHTML = this.innerHTML;
    activateVerse2();
    original = (document.getElementById("verse2-current-selection").textContent == document.getElementById("original-2").textContent);
    verseProperty("verse1-current-parent",original,activateVerse1);
    hideVerse("verse3-option", !original);
    hideVerse("verse4-option", !original);
    hideVerse("verse5-option", !original);
    document.getElementById("generate-button").querySelector('button').disabled = original;
    limerickFinal(!original);
}

const onClickVerse3 = function() {
    document.getElementById("notification").innerHTML = '';
    document.getElementById("verse3-current-selection").innerHTML = this.innerHTML;
    activateVerse3();
    original = (document.getElementById("verse3-current-selection").textContent == document.getElementById("original-3").textContent);
    verseProperty("verse1-current-parent",original,activateVerse1);
    verseProperty("verse2-current-parent",original,activateVerse2);
    hideVerse("verse4-option", !original);
    hideVerse("verse5-option", !original);
    document.getElementById("generate-button").querySelector('button').disabled = original;
    limerickFinal(!original);
}

const onClickVerse4 = function() {
    document.getElementById("notification").innerHTML = '';
    document.getElementById("verse4-current-selection").innerHTML = this.innerHTML;
    activateVerse4();
    original = (document.getElementById("verse4-current-selection").textContent == document.getElementById("original-4").textContent);
    verseProperty("verse1-current-parent",original,activateVerse1);
    verseProperty("verse2-current-parent",original,activateVerse2);
    verseProperty("verse3-current-parent",original,activateVerse3);
    hideVerse("verse5-option", !original);
    document.getElementById("generate-button").querySelector('button').disabled = original;
    limerickFinal(!original);
}

const onClickVerse5 = function() {
    document.getElementById("notification").innerHTML = '';
    document.getElementById("verse5-current-selection").innerHTML = this.innerHTML;
    activateVerse5();
    original = (document.getElementById("verse5-current-selection").textContent == document.getElementById("original-5").textContent);
    new_limerick = canSave();
    can_dropdown = true;
    if(!original && new_limerick) can_dropdown = false;
    verseProperty("verse2-current-parent",can_dropdown,activateVerse2);
    verseProperty("verse3-current-parent",can_dropdown,activateVerse3);
    verseProperty("verse4-current-parent",can_dropdown,activateVerse4);
    verseProperty("verse1-current-parent",can_dropdown,activateVerse1);
    document.getElementById("save-button").querySelector('button').disabled = can_dropdown;
    limerickFinal(!can_dropdown);
    if(!new_limerick) {
        notify();
    }
}

function verseActivateDropdown(verseParent, verseList, activationFunction, onClickFunction) {
    var default_option = document.getElementById(verseParent);
    var verse_options = document.getElementById(verseList);
    if(verse_options.childElementCount == 0) {
        default_option.onclick = '';
        default_option.classList.add("disabled");
        default_option.classList.remove("default_option");
    }
    else {
        default_option.onclick = activationFunction;
    }
    for (let i = 0; i < verse_options.children.length; i++) {
        verse_options.children[i].onclick = onClickFunction;
    }
}
function activateClicks() {
    verseActivateDropdown("verse1-current-parent", "verse1-list", activateVerse1, onClickVerse1);
    verseActivateDropdown("verse2-current-parent", "verse2-list", activateVerse2, onClickVerse2);
    verseActivateDropdown("verse3-current-parent", "verse3-list", activateVerse3, onClickVerse3);
    verseActivateDropdown("verse4-current-parent", "verse4-list", activateVerse4, onClickVerse4);
    verseActivateDropdown("verse5-current-parent", "verse5-list", activateVerse5, onClickVerse5);
}

function disableVoting() {
    voting_buttons = document.querySelectorAll('button[type="vote_button"]');
    for(let i = 0; i < voting_buttons.length; i++) {
        voting_buttons[i].disabled = true
    }
    voting = document.getElementById("voting-buttons");
    voting.classList.add("filterDisabled")
}

function enableVoting() {
    voting_buttons = document.querySelectorAll('button[type="vote_button"]');
    for(let i = 0; i < voting_buttons.length; i++) {
        voting_buttons[i].disabled = false;
    }
    voting = document.getElementById("voting-buttons");
    voting.classList.remove("filterDisabled")
}


window.addEventListener('click', function(e){  
    verse1 = document.getElementById('verse1-option');
    verse2 = document.getElementById('verse2-option');
    verse3 = document.getElementById('verse3-option');
    verse4 = document.getElementById('verse4-option'); 
    verse5 = document.getElementById('verse5-option');
    if (!verse1.contains(e.target) && verse1.classList.contains("active")) activateVerse1();
    if (!verse2.contains(e.target) && verse2.classList.contains("active")) activateVerse2();
    if (!verse3.contains(e.target) && verse3.classList.contains("active")) activateVerse3();
    if (!verse4.contains(e.target) && verse4.classList.contains("active")) activateVerse4();
    if (!verse5.contains(e.target) && verse5.classList.contains("active")) activateVerse5();
});

/*$(document).on('submit','#new-limerick-form',function(e){
    e.preventDefault();
    $.ajax({
        type:'POST',
        data:
        {
            verse1:$("#new-verse1").val(),
            verse2:$("#new-verse2").val(),
            verse3:$("#new-verse3").val(),
            verse4:$("#new-verse4").val(),
            verse5:$("#new-verse5").val(),
            overse1:$("#o-verse1").val(),
            overse3:$("#o-verse3").val(),
            overse4:$("#o-verse4").val(),
            overse5:$("#o-verse5").val(),
            female:$('input[name=female]').val(),
            place:$('input[name=place]').val(),
            adjective:$('input[name=adjective]').val(),
            profession:$('input[name=profession]').val(),
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val()
        },
        success:function(response){
            $("body").html(response);
        }
    })
});*/

function replaceLimerick() {
    var current_limerick = document.getElementById("current-random-limerick");
    current_limerick.classList.remove('fadeOut')
    current_limerick.classList.remove('fadeIn')
    current_limerick.classList.add('fadeOut');
    var random_limerick = all_limericks[Math.floor(Math.random()*all_limericks.length)];
    document.getElementById("random-verse1").innerHTML = random_limerick[0]
    document.getElementById("random-verse2").innerHTML = random_limerick[1]
    document.getElementById("random-verse3").innerHTML = random_limerick[2]
    document.getElementById("random-verse4").innerHTML = random_limerick[3]
    document.getElementById("random-verse5").innerHTML = random_limerick[4]
    current_limerick.focus(); // use focus trick without setTimeOut
    current_limerick.classList.add('fadeIn');
    setTimeout(replaceLimerick, 7000);
}

function loadingScreen() {
    document.forms['new-limerick-form'].submit();
    document.getElementById("main-container").style.display = 'none';
    document.getElementById("loading-screen").style.visibility = 'visible';
    replaceLimerick();
}

function notify() {
    v1same =  (document.getElementById("verse1-current-selection").textContent == document.getElementById("original-1").textContent);
    v2same =  (document.getElementById("verse2-current-selection").textContent == document.getElementById("original-2").textContent);
    v3same =  (document.getElementById("verse3-current-selection").textContent == document.getElementById("original-3").textContent);
    v4same =  (document.getElementById("verse4-current-selection").textContent == document.getElementById("original-4").textContent);
    v5same =  (document.getElementById("verse5-current-selection").textContent == document.getElementById("original-5").textContent);
    if(!v1same || !v2same || !v3same || !v4same || !v5same) document.getElementById("notification").innerHTML = "This limerick already exists.";
}
function canSave() {
    newLimerick = true;
    nv1 = document.getElementById("verse1-current-selection").innerHTML;
    nv2 = document.getElementById("verse2-current-selection").innerHTML;
    nv3 = document.getElementById("verse3-current-selection").innerHTML;
    nv4 = document.getElementById("verse4-current-selection").innerHTML;
    nv5 = document.getElementById("verse5-current-selection").innerHTML;
    for(let i = 0; i < all_limericks.length; i++) {
        if(nv1 == all_limericks[i][0] && nv2 == all_limericks[i][1] && nv3 == all_limericks[i][2] && 
            nv4 == all_limericks[i][3] && nv5 == all_limericks[i][4]) {
                newLimerick = false;
                break;
            }
    }
    return newLimerick;
}

function openRanking() {
    document.getElementById("rankings").style.width = "200px";
}

function closeRanking() {
    document.getElementById("rankings").style.width = "0";
}

window.onload = function() {
    //openRanking();
    resultingLimerick();
    editableLimerick();
    limerickButtons(false);
    enableDisableGenderFilter();
    enableDisablePlaceFilter();
    const pron_filter = document.getElementById("pron-switch");
    pron_filter.addEventListener("click",pronFlipCard);
}

