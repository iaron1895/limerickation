var currentWord = '';
var timer;

const adjective_profession_dict = JSON.parse(document.getElementById('adjprof-data').textContent);
const all_limericks = JSON.parse(document.getElementById('all_limericks').textContent);

const onClickAdjective = function() {
    document.getElementById("adjective_current_selection").innerHTML = this.innerHTML;
    document.getElementById("adjective_option").classList.toggle("active");
    document.removeEventListener('keydown', keyboardPressAdjective); 
    updateAvailableProfessions();
    hideCurrentProfession();
}

const onClickProfession = function() {
    document.getElementById("profession_current_selection").innerHTML = this.innerHTML;
    document.getElementById("profession_option").classList.toggle("active");
    document.removeEventListener('keydown', keyboardPressProfession); 
}

function updateAvailableProfessions() {
    const all_professions = document.getElementById('profession_list').children;
    var current_adjective = document.getElementById("adjective_current_selection").textContent;
    for (let i = 0; i < all_professions.length; i++) { 
        (!adjective_profession_dict[current_adjective].includes(all_professions[i].textContent)) ? all_professions[i].style.display = 'none' : all_professions[i].style.display = '';
    }
}

function hideCurrentProfession() {
    var current_adjective = document.getElementById("adjective_current_selection").textContent;
    var current_profession = document.getElementById("profession_current_selection").textContent;
    if (!adjective_profession_dict[current_adjective].includes(current_profession)) {
        document.getElementById("profession_current_selection").innerHTML = adjective_profession_dict[current_adjective][0];
    }
}

function selectRandom() {
    var adjective_list = document.getElementById("adjective_list");
    var random_adjective = adjective_list.children[Math.floor(Math.random()*adjective_list.children.length)];
    var potential_professions = adjective_profession_dict[random_adjective.textContent];
    var random_profession = potential_professions[Math.floor(Math.random()*potential_professions.length)];
    document.getElementById("adjective_current_selection").innerHTML = random_adjective.textContent;
    document.getElementById("profession_current_selection").innerHTML = random_profession;
    updateAvailableProfessions();
}

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

function sendGenerationForm(kind) {
    document.getElementById("adjective_selection").value = document.getElementById("adjective_current_selection").textContent;
    document.getElementById("profession_selection").value = document.getElementById("profession_current_selection").textContent;
    document.getElementById("generation_kind").value = kind
    document.forms['limerick-generation'].submit();
    document.getElementById("container").style.display = 'none';
    document.getElementById("loading-screen").style.visibility = 'visible';
    replaceLimerick();
}

function initialiseDropdownList(default_option_parent, option, list, on_click_function, filter) {
    var default_option = document.getElementById(default_option_parent);
    default_option.onclick = function () { activateDropdown(option, filter); };
    var options = document.getElementById(list);
    for (let i = 0; i < options.children.length; i++) {
        options.children[i].onclick = on_click_function;
    }
}

function keyboardPressAdjective(e) {
    if (timer) {
        clearTimeout(timer);
    }
    var name = e.key;
    var  dropdown_option = document.getElementById("adjective_option");
    if(name == 'Enter' && dropdown_option.classList.contains("active")) {
        dropdown_option.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressAdjective);
        updateAvailableProfessions();
        hideCurrentProfession();
    }
    currentWord += e.key;
    startsWith = Array.from(document.getElementById("adjective_list").children).filter((adj) => adj.innerHTML.startsWith(currentWord));
    if(startsWith.length > 0) {
        startsWith[0].scrollIntoView();
        document.getElementById("adjective_current_selection").innerHTML = startsWith[0].innerHTML;
    }
    timer = setTimeout(function () {
        currentWord = '';
    }, 500);
}

function keyboardPressProfession(e) {
    if (timer) {
        clearTimeout(timer);
    }
    var name = e.key;
    var  dropdown_option = document.getElementById("profession_option");
    if(name == 'Enter' && dropdown_option.classList.contains("active")) {
        dropdown_option.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressProfession);
    }
    currentWord += e.key;
    var hiddenElements = Array.from(document.querySelectorAll("#profession_list > [style]"))
    startsWith = Array.from(document.getElementById("profession_list").children).filter((adj) => adj.innerHTML.startsWith(currentWord) && hiddenElements.indexOf(adj) == -1);
    if(startsWith.length > 0) {
        startsWith[0].scrollIntoView();
        document.getElementById("profession_current_selection").innerHTML = startsWith[0].innerHTML;
    }
    timer = setTimeout(function () {
        currentWord = '';
    }, 500);
}

function activateDropdown(dropdown_option, filter) {
    document.getElementById(dropdown_option).classList.toggle("active");
    if(document.getElementById(dropdown_option).classList.contains("active")) {
        if(filter == "adjective") document.addEventListener('keydown', keyboardPressAdjective); 
        if(filter == "profession") document.addEventListener('keydown', keyboardPressProfession); 
    }
    else {
        document.removeEventListener('keydown', keyboardPressAdjective); 
        document.removeEventListener('keydown', keyboardPressProfession); 
    }
}

window.addEventListener('click', function(e){  
    adjective = document.getElementById('adjective_option');
    profession = document.getElementById('profession_option');
    if (!adjective.contains(e.target) && adjective.classList.contains("active")){
        adjective.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressAdjective); 
    } 
    if (!profession.contains(e.target) && profession.classList.contains("active")){
        profession.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressProfession); 
    } 
});

window.onload = function() {
    updateAvailableProfessions();
    initialiseDropdownList("adjective_current_selection_parent","adjective_option","adjective_list", onClickAdjective,"adjective");
    initialiseDropdownList("profession_current_selection_parent","profession_option","profession_list", onClickProfession,"profession");
    document.getElementById('random_selection').addEventListener('click', selectRandom);
};