import random
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import resolve
import datetime

from django.db.utils import OperationalError
try:

    from .forms import FilterForm, LimerickForm, ADJECTIVE_CHOICES, SaveLimerickForm, VoteForm

    from .models import Limerick, AdjProfHelper, generateFromSecond, generateFromThird, generateFromFourth, run_limerick_generation_multiple, run_limerick_generation_single, update_rankings


    def indexView(request):
        try:
            del request.session['limericks']
        except KeyError:
            pass
        try:
            del request.session['new_limerick']
        except KeyError:
            pass
        try:
            del request.session['originating']
        except KeyError:
            pass
        try:
            del request.session['filtered_limericks']
        except KeyError:
            pass
        try:
            del request.session['sort']
        except KeyError:
            pass
        return render(request, 'limerines/index.html')

    def all_limericks(request):
        try:
            del request.session['limericks']
        except KeyError:
            pass
        try:
            del request.session['originating']
        except KeyError:
            pass
        try:
            del request.session['new_limerick']
        except KeyError:
            pass
        sort = 'user'
        try:
            sort = request.session['sort']
        except KeyError:
            pass
        if request.method == "POST":
            print(request.POST)
            filter_form = FilterForm(request.POST)
            if 'limerick_id' in request.POST:
                form = VoteForm(request.POST)
                if form.is_valid():
                    upvote = form.cleaned_data.get('upvote')
                    limerick_id = form.cleaned_data.get('limerick_id')
                    l = Limerick.objects.get(pk=limerick_id)
                    if upvote == 'true':
                        l.votes += 1
                    elif upvote == 'false':
                        l.votes -= 1
                    l.save()
                    update_rankings()
            if filter_form.is_valid():
                gender = filter_form.cleaned_data.get('gender')
                adjective = filter_form.cleaned_data.get('adjective')
                profession = filter_form.cleaned_data.get('profession')
                type = filter_form.cleaned_data.get('type')
                sort = filter_form.cleaned_data.get('sort')
                limericks = Limerick.objects.all()
                if gender == 'male':
                    limericks = limericks.filter(female=False)
                elif gender == 'female':
                    limericks = limericks.filter(female=True)
                if adjective != 'All':
                    limericks = limericks.filter(adjective=adjective)
                if profession != 'All':
                    limericks = limericks.filter(profession=profession)
                if type == 'place':
                    limericks = limericks.filter(place=True)
                elif type == 'name':
                    limericks = limericks.filter(place=False)
                if sort == 'user':
                    limericks_list = limericks.order_by('rank')
                else:
                    limericks_list = limericks.order_by('model_rank')
                request.session['sort'] = sort
                request.session['filtered_limericks'] = [l.id for l in limericks_list]
        else:
            if sort == 'user':
                limericks_list = Limerick.objects.order_by('rank')
            else:
                limericks_list = Limerick.objects.order_by('model_rank')
            filter_form = FilterForm(initial={'gender':'All','adjective':'All','profession':'All','type':'All'})

        page = request.GET.get('page', 1)
        paginator = Paginator(limericks_list, 10)
        try:
            limericks = paginator.page(page)
        except PageNotAnInteger:
            limericks = paginator.page(1)
        except EmptyPage:
            limericks = paginator.page(paginator.num_pages)
        return render(request, 'limerines/limericks.html', { 'sort' : sort, 'limericks': limericks , 'filter_form': filter_form})

    def detail(request, limerick_id):
        url_name = resolve(request.path).url_name
        limericks = []
        new_limerick = 0
        originating = 0
        sort = 'user'
        try:
            limericks = request.session['limericks']
        except KeyError:
            pass
        try:
            new_limerick = request.session['new_limerick']
        except KeyError:
            pass
        try:
            originating = request.session['originating']
        except KeyError:
            pass
        try:
            sort = request.session['sort']
        except KeyError:
            pass

        if url_name == 'edit' and limerick_id not in limericks:
            return render(request, 'limerines/pageNotFound.html')
        if url_name == 'result' and limerick_id != new_limerick:
            return render(request, 'limerines/pageNotFound.html')

        if url_name != 'result':
            try:
                del request.session['new_limerick']
            except KeyError:
                pass
        
        limerick = get_object_or_404(Limerick, pk=limerick_id)
        if request.method == "POST":
            print("DETAIL POST")
            print(request.POST)
            if 'upvote' in request.POST:
                form = VoteForm(request.POST)
                if form.is_valid():
                    upvote = form.cleaned_data.get('upvote')
                    if upvote == 'true':
                        limerick.votes += 1
                    elif upvote == 'false':
                        limerick.votes -= 1
                    limerick.save()
                    update_rankings()
                    return render(request, 'limerines/detail.html', {'limericks':limericks, 'limerick':limerick, 'originating':originating, 'sort':sort})
            if 'verse1' in request.POST:
                form = SaveLimerickForm(request.POST)
                print(request.POST)
                if form.is_valid():
                    verse1 = form.cleaned_data.get('verse1'); verse2 = form.cleaned_data.get('verse2')
                    verse3 = form.cleaned_data.get('verse3'); verse4 = form.cleaned_data.get('verse4')
                    verse5 = form.cleaned_data.get('verse5')
                    overse1 = form.cleaned_data.get('overse1'); overse3 = form.cleaned_data.get('overse3')
                    overse4 = form.cleaned_data.get('overse4'); overse5 = form.cleaned_data.get('overse5')[:-1]
                    female = form.cleaned_data.get('female'); place = form.cleaned_data.get('place')
                    adjective = form.cleaned_data.get('adjective'); profession = form.cleaned_data.get('profession')
                    request.session['originating'] = limerick.id 
                    if verse3 != 'hidden' and verse4 != 'hidden' and verse5 != 'hidden':
                        l = Limerick(verse1 = verse1, verse2 = verse2, verse3 = verse3, verse4 = verse4, verse5 = verse5, 
                        female = female, adjective = adjective, profession = profession, place = place)
                        l.get_pronunciation()
                        l.get_perplexity()
                        l.save()
                        update_rankings()
                        request.session['new_limerick'] = l.id
                        return redirect('limerines:result', limerick_id=l.id)
                    if verse3 != 'hidden' and verse4 != 'hidden' and verse5 == 'hidden':
                        text = verse1 + ' ' + verse2 + ' ' + verse3 + ' ' + verse4
                        l = generateFromFourth(text, overse5, adjective, profession, female, place)
                        request.session['new_limerick'] = l.id
                        return redirect('limerines:result', limerick_id=l.id)
                    if verse3 != 'hidden' and verse4 == 'hidden' and verse5 == 'hidden':
                        text = verse1 + ' ' + verse2 + ' ' + verse3
                        l = generateFromThird(text, overse4, overse5, adjective, profession, female, place) 
                        request.session['new_limerick'] = l.id
                        return redirect('limerines:result', limerick_id=l.id)  
                    if verse3 == 'hidden' and verse4 == 'hidden' and verse5 == 'hidden':
                        text = verse1 + ' ' + verse2
                        l = generateFromSecond(text, overse1, overse3, overse4, overse5, adjective, profession, female, place)
                        request.session['new_limerick'] = l.id
                        return redirect('limerines:result', limerick_id=l.id)
        else:
            return render(request, 'limerines/detail.html', {'limericks':limericks, 'limerick':limerick, 'originating':originating, 'sort':sort})

    def generate_limerick(request):
        try:
            del request.session['sort']
        except KeyError:
            pass
        try:
            del request.session['limericks']
        except KeyError:
            pass
        try:
            del request.session['originating']
        except KeyError:
            pass
        try:
            del request.session['filtered_limericks']
        except KeyError:
            pass
        if request.method == "POST":
            print(request.POST)
            form = LimerickForm(request.POST)
            if form.is_valid():
                adjective = form.cleaned_data.get('adjective')
                profession = form.cleaned_data.get('profession')
                kind = form.cleaned_data.get('kind')
                now = datetime.datetime.now()
                if kind == 'single':
                    print(f'Starting single gleneration at {now}')
                    try:
                        limericks = run_limerick_generation_single(adjective, profession)
                    except:
                        return render(request, 'limerines/errorGeneration.html')
                else:
                    print(f'Starting multi gleneration at {now}')
                    try:
                        limericks = run_limerick_generation_multiple(adjective, profession)
                    except:
                        return render(request, 'limerines/errorGeneration.html')
                now = datetime.datetime.now()
                print(f'Ending at {now}')
                first_limerick = limericks[0]
                request.session['limericks'] = [l.id for l in limericks]
                return redirect(reverse('limerines:edit', args=(first_limerick.id,)))
            else:
                return render(request, 'limerines/generate.html', {'form': form})
        else:
            adjective = random.choice(ADJECTIVE_CHOICES)[0]
            adjective_professions = AdjProfHelper.object().adjective_profession
            profession = random.choice(adjective_professions[adjective])
            form = LimerickForm(initial = {'adjective':adjective, 'profession':profession})
        return render(request, 'limerines/generate.html', {'form': form})


except OperationalError:
    def indexView(request):
        return render(request, 'limerines/index.html')

    def all_limericks(request):
        return render(request, 'limerines/index.html')

    def detail(request):
        return render(request, 'limerines/index.html')

    def generate_limerick(request):
        return render(request, 'limerines/index.html')