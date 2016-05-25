from django.shortcuts import render
from .models import Meetings, Nutritionist
from django.core import serializers
import json
from django.core import serializers
from django.http import HttpResponse, JsonResponse
from .forms import MeetingForm
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.core.mail import EmailMessage
from django.shortcuts import redirect

# Create your views here.
def home(request):
    title = 'dietetycy'
    nutritionists = Nutritionist.objects.all()
    data_json = serializers.serialize("json", nutritionists)
    return render(request, "nutritionist.html", {'title': title, 'nutritionists': nutritionists, "data_json": data_json})

def calendar(request, id=None):
    nutritionist = Nutritionist.objects.get(id=id)
    title = 'kalendarz'
    meetings = Meetings.objects.all()
    url = request.get_full_path()
    n_id = url[-1:]

    dataToCal = {
        '1': [],
        '2': [],
        '3': [],
        '4': [],
        '5': []
    }
    data_json = serializers.serialize("json", meetings)
    for day in range(1,6):
        day = str(day)
        for meeting in meetings:
            if meeting.day == day and str(meeting.nutritionist.id) == n_id:


                hourBegin = meeting.hourBegin
                hourEnd = meeting.hourEnd
                # hourBegin.encode('ascii', 'ignore')
                # hourEnd.encode('ascii','ignore')
                dataToCal[day].append([hourBegin, hourEnd])
    dataToCal = json.dumps(dataToCal)
    print dataToCal
    # dataToCal = serializers.serialize("json", dataToCal)

    return render(request, "calendar.html", {'title': title, 'dataToCal': dataToCal})

@csrf_exempt
def send_form(request):
    title = 'Formularz'
    url = request.get_full_path()
    print 'xxxxxxxxxxxxxx',url
    day = url[-7:-6]
    n_id = url[-1:]
    hourBegin = url[-6:-1].encode('ascii','ignore')
    hourEnd = hourBegin
    hourEnd = list(hourEnd)
    if hourEnd[3] == '0':
        hourEnd[3] = '3'
    elif hourEnd[3] == '3':
        if hourEnd[1] == '9' and hourEnd[0] == "0":
            hourEnd[0] = "1"
            hourEnd[1] = "0"
            hourEnd[3] = '0'
        elif hourEnd[1] == '9' and hourEnd[0] == "1":
            hourEnd[0] = "2"
            hourEnd[1] = "0"
            hourEnd[3] = '0'
        else:
            hourEnd[1] = str(int(hourEnd[1]) + 1)
            hourEnd[3] = '0'
    hourEnd = "".join(hourEnd)
    nutritionist = Nutritionist.objects.get(pk=n_id)
    if request.method == "POST":
        meeting_hourBegin = hourBegin
        meetting_hourEnd = hourEnd
        meeting_day = day
        meeting_name = request.POST.get('the_name')
        meeting_fullname = request.POST.get('the_fullname')
        meeting_email = request.POST.get('the_email')
        meeting_nutritionist = nutritionist

        response_data = {}
        nutritionist = Nutritionist.objects.all().first()

        meeting = Meetings(
            hourBegin=meeting_hourBegin,
            hourEnd=meetting_hourEnd ,
            day=meeting_day ,
            name=meeting_name ,
            fullname=meeting_fullname ,
            email=meeting_email ,
            nutritionist=nutritionist
        )
        meeting.save()
        response_data['hourBegin'] = meeting.hourBegin
        response_data['hourEnd'] = meeting.hourEnd
        response_data['day'] = meeting.day
        response_data['name'] = meeting.name
        response_data['fullname'] = meeting.fullname
        response_data['email'] = meeting.email
        response_data['nutritionist'] = meeting.nutritionist.id

        days = {
            '1': 'poniedzialek',
            '2': 'wtorek',
            '3': 'sroda',
            '4': 'czwartek',
            '5': 'piatek'
        }
        print response_data
        email = EmailMessage("Potwierzenie rejestracji",
                             'Witaj {}! Zarejestrowales sie do dietetyka {} {} {} w najblizszy {} o godznie {}'.
                             format(meeting_name.encode('ascii','ignore'),
                                    meeting_nutritionist.title.encode('ascii','ignore'),
                                    meeting_nutritionist.name.encode('ascii','ignore'),
                                    meeting_nutritionist.fullname.encode('ascii','ignore'),
                                    days[meeting_day].encode('ascii','ignore'),
                                    meeting_hourBegin).encode('ascii','ignore'),
                             to=[meeting_email])
        email.send()

        return JsonResponse(response_data)
    elif request.method == "GET":
        form = MeetingForm()
        return render(request, "form.html", {'title': title, 'form': form})

def thanks(request):
    # email = EmailMessage('title', 'body', to=["john_qr@o2.pl"])
    # email.send()
    title = 'dziekujemy'
    return render(request, "thanks.html", {'title': title})

