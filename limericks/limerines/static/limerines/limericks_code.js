let gender_filter = null
let adjective_filter = null
let profession_filter = null
let type_filter = null
var currentWord = '';
var timer;

const adjective_profession_dict = JSON.parse(document.getElementById('adjprof-data').textContent);
const sort_type = JSON.parse(document.getElementById('sort-type').textContent);

function buttonEnabledDisabled() {
    current_gender_filter = document.getElementById("gender_current_selection").textContent;
    current_adjective_filter = document.getElementById("adjective_current_selection").textContent;
    current_profession_filter = document.getElementById("profession_current_selection").textContent;
    current_type_filter = document.getElementById("type_current_selection").textContent;
    if(current_gender_filter != gender_filter || current_adjective_filter != adjective_filter || current_profession_filter != profession_filter || current_type_filter != type_filter) {
        document.getElementById("apply-filter").disabled = false;
    } else {
        document.getElementById("apply-filter").disabled = true;
    }
}

function clearAllFilters() {
    gender_filter = 'All';
    adjective_filter = 'All';
    profession_filter = 'All';
    type_filter = 'All';
    document.getElementById("apply-filter").disabled = true;
    document.getElementById("gender_selection").value = gender_filter;
    document.getElementById("adjective_selection").value = adjective_filter;
    document.getElementById("profession_selection").value = profession_filter;
    document.getElementById("type_selection").value = type_filter;
    document.getElementById("sort_by_filter").value = sort_type;
    document.forms['filter-form'].submit();
}

function removeFiltersVisibleHidden() {
    current_gender_filter = document.getElementById("gender_current_selection").textContent;
    current_adjective_filter = document.getElementById("adjective_current_selection").textContent;
    current_profession_filter = document.getElementById("profession_current_selection").textContent;
    current_type_filter = document.getElementById("type_current_selection").textContent;
    if(current_gender_filter != 'All' || current_adjective_filter != 'All' || current_profession_filter != 'All' || current_type_filter != 'All') {
        document.getElementById("remove-filters").style.display = '';
    } else {
        document.getElementById("remove-filters").style.display = 'none';
    }
}

function openFilter() {
    document.getElementById("table-filter").style.width = "200px";
    votingOption(true);
    updateAvailableProfessions();
    updateAvailableAdjectives();
    hideCurrentProfession();
    hideCurrentAdjective();
}

function applyFilters() {
    gender_filter = document.getElementById("gender_current_selection").textContent;
    adjective_filter = document.getElementById("adjective_current_selection").textContent;
    profession_filter = document.getElementById("profession_current_selection").textContent;
    type_filter = document.getElementById("type_current_selection").textContent;
    document.getElementById("apply-filter").disabled = true;
    document.getElementById("gender_selection").value = gender_filter;
    document.getElementById("adjective_selection").value = adjective_filter;
    document.getElementById("profession_selection").value = profession_filter;
    document.getElementById("type_selection").value = type_filter;
    document.getElementById("sort_by_filter").value = sort_type;
    document.forms['filter-form'].submit();
}

function votingOption(disable) {
    voting_buttons = document.querySelectorAll('button[type="vote_button"]');
    for(let i = 0; i < voting_buttons.length; i++) {
        voting_buttons[i].disabled = disable
    }
}

function updateCurrentValuesVote(upvote, id) {
    gender_filter = document.getElementById("gender_current_selection").textContent;
    adjective_filter = document.getElementById("adjective_current_selection").textContent;
    profession_filter = document.getElementById("profession_current_selection").textContent;
    type_filter = document.getElementById("type_current_selection").textContent;
    document.getElementById("gender_selection_vote").value = gender_filter;
    document.getElementById("adjective_selection_vote").value = adjective_filter;
    document.getElementById("profession_selection_vote").value = profession_filter;
    document.getElementById("type_selection_vote").value = type_filter;
    document.getElementById("action_vote").value = upvote;
    document.getElementById("limerick_id").value = id;
    document.getElementById("sort_by_vote").value = sort_type;
    document.forms['submit-vote'].submit();
}

function sortTable() {
    gender_filter = document.getElementById("gender_current_selection").textContent;
    adjective_filter = document.getElementById("adjective_current_selection").textContent;
    profession_filter = document.getElementById("profession_current_selection").textContent;
    type_filter = document.getElementById("type_current_selection").textContent;
    document.getElementById("gender_selection_sort").value = gender_filter;
    document.getElementById("adjective_selection_sort").value = adjective_filter;
    document.getElementById("profession_selection_sort").value = profession_filter;
    document.getElementById("type_selection_sort").value = type_filter;
    document.getElementById("sort_by_sort").value = (sort_type == 'user') ? 'model' : 'user';
    document.forms['sort-table'].submit();
}

function closeFilter() {
    document.getElementById("table-filter").style.width = "0";
    document.getElementById("gender_current_selection").textContent = gender_filter;
    document.getElementById("adjective_current_selection").textContent = adjective_filter;
    document.getElementById("profession_current_selection").textContent = profession_filter;
    document.getElementById("type_current_selection").textContent = type_filter;
    document.getElementById("apply-filter").disabled = true;
    removeFiltersVisibleHidden();
    votingOption(false);
}

function activateFilter(option, filter = '') {
    document.getElementById(option).classList.toggle("active")
    if(document.getElementById(option).classList.contains("active")) {
        if(filter == "adjective") document.addEventListener('keydown', keyboardPressAdjective); 
        if(filter == "profession") document.addEventListener('keydown', keyboardPressProfession); 
    }
    else {
        document.removeEventListener('keydown', keyboardPressAdjective); 
        document.removeEventListener('keydown', keyboardPressProfession); 
    }
}

function onClickFilter(current_selection, option, obj, filter = '') {
    document.getElementById(current_selection).innerHTML = obj.innerHTML;
    document.getElementById(option).classList.toggle("active");
    buttonEnabledDisabled();
    removeFiltersVisibleHidden();
    if(filter == 'adjective') {
        document.removeEventListener('keydown', keyboardPressAdjective); 
        updateAvailableProfessions();
        if(document.getElementById(current_selection).textContent != 'All') {
            hideCurrentProfession();
        }
    }
    if(filter == 'profession') {
        document.removeEventListener('keydown', keyboardPressProfession); 
        updateAvailableAdjectives();
        if(document.getElementById(current_selection).textContent != 'All') {
            hideCurrentAdjective();
        }
    }
}

function updateAvailableProfessions() {
    const all_professions = document.getElementById('profession_list').children;
    var current_adjective = document.getElementById("adjective_current_selection").textContent;
    if(current_adjective == 'All') {
        for (let i = 0; i < all_professions.length; i++) { 
            all_professions[i].style.display = '';
        }
        return;
    }
    for (let i = 0; i < all_professions.length; i++) { 
        if(all_professions[i].textContent == 'All') {
            continue;
        }
        (!adjective_profession_dict[current_adjective].includes(all_professions[i].textContent)) ? all_professions[i].style.display = 'none' : all_professions[i].style.display = '';
    }
}

function hideCurrentProfession() {
    var current_adjective = document.getElementById("adjective_current_selection").textContent;
    var current_profession = document.getElementById("profession_current_selection").textContent;
    if(current_profession == 'All') {
        return;
    }
    if (!adjective_profession_dict[current_adjective].includes(current_profession)) {
        document.getElementById("profession_current_selection").innerHTML = adjective_profession_dict[current_adjective][0];
    }
}

function updateAvailableAdjectives() {
    all_adjectives = document.getElementById('adjective_list').children;
    all_professions = document.getElementById('profession_list').children;
    var current_profession = document.getElementById("profession_current_selection").textContent;
    if(current_profession == 'All') {
        for (let i = 0; i < all_adjectives.length; i++) { 
            all_adjectives[i].style.display = '';
        }
        return;
    }
    for (let i = 0; i < all_adjectives.length; i++) { 
        if(all_adjectives[i].textContent == 'All') {
            continue;
        }
        (!adjective_profession_dict[all_adjectives[i].textContent].includes(current_profession)) ? all_adjectives[i].style.display = 'none' : all_adjectives[i].style.display = '';
    }
}

function hideCurrentAdjective() {
    var current_adjective = document.getElementById("adjective_current_selection").textContent;
    var current_profession = document.getElementById("profession_current_selection").textContent;
    if(current_adjective == 'All') {
        return;
    }
    if (!adjective_profession_dict[current_adjective].includes(current_profession)) {
        for(var key in adjective_profession_dict) {
            if(adjective_profession_dict[key].includes(current_profession)) {
                document.getElementById("adjective_current_selection").innerHTML = key;
                break;
            }
        }
    }
}

function initialiseDropdownList(default_option_parent, option, list, current_selection, filter = '') {
    var default_option = document.getElementById(default_option_parent);
    default_option.onclick = function () { activateFilter(option, filter); };
    options = document.getElementById(list);
    for (let i = 0; i < options.children.length; i++) {
        options.children[i].onclick = function () { onClickFilter(current_selection, option, this, filter); };
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
        buttonEnabledDisabled();
        document.removeEventListener('keydown', keyboardPressAdjective);
        updateAvailableProfessions();
        if(document.getElementById(current_selection).textContent != 'All') {
            hideCurrentProfession();
        }
    }
    currentWord += e.key;
    var hiddenElements = Array.from(document.querySelectorAll("#adjective_list > [style]"))
    startsWith = Array.from(document.getElementById("adjective_list").children).filter((adj) => adj.innerHTML.startsWith(currentWord) && hiddenElements.indexOf(adj) == -1);
    if(startsWith.length > 0) {
        startsWith[0].scrollIntoView({block:"nearest",inline:"start"});
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
        buttonEnabledDisabled();
        document.removeEventListener('keydown', keyboardPressProfession);
        updateAvailableAdjectives();
        if(document.getElementById(current_selection).textContent != 'All') {
            hideCurrentAdjective();
        }
    }
    currentWord += e.key;
    var hiddenElements = Array.from(document.querySelectorAll("#profession_list > [style]"))
    startsWith = Array.from(document.getElementById("profession_list").children).filter((adj) => adj.innerHTML.startsWith(currentWord) && hiddenElements.indexOf(adj) == -1);
    if(startsWith.length > 0) {
        startsWith[0].scrollIntoView({block:"nearest",inline:"start"});
        document.getElementById("profession_current_selection").innerHTML = startsWith[0].innerHTML;
    }
    timer = setTimeout(function () {
        currentWord = '';
    }, 500);
}

window.addEventListener('click', function(e){  
    gender = document.getElementById('gender_option');
    adjective = document.getElementById('adjective_option');
    profession = document.getElementById('profession_option');
    type = document.getElementById('type_option'); 
    if (!gender.contains(e.target) && gender.classList.contains("active")){
        gender.classList.toggle("active");
    } 
    if (!adjective.contains(e.target) && adjective.classList.contains("active")){
        adjective.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressAdjective); 
    } 
    if (!profession.contains(e.target) && profession.classList.contains("active")){
        profession.classList.toggle("active");
        document.removeEventListener('keydown', keyboardPressProfession); 
    } 
    if (!type.contains(e.target) && type.classList.contains("active")){
        type.classList.toggle("active");
    } 
});

window.onload = function() {
    removeFiltersVisibleHidden()
    gender_filter = document.getElementById("gender_current_selection").textContent;
    adjective_filter = document.getElementById("adjective_current_selection").textContent;
    profession_filter = document.getElementById("profession_current_selection").textContent;
    type_filter = document.getElementById("type_current_selection").textContent;

    initialiseDropdownList("gender_current_selection_parent", "gender_option", "gender_list", "gender_current_selection");
    initialiseDropdownList("type_current_selection_parent", "type_option", "type_list", "type_current_selection");
    initialiseDropdownList("adjective_current_selection_parent", "adjective_option", "adjective_list", "adjective_current_selection", "adjective");
    initialiseDropdownList("profession_current_selection_parent", "profession_option", "profession_list", "profession_current_selection", "profession");

};


