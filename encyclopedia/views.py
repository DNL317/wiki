from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms
import random
from markdown2 import Markdown
from . import util


markdown_tool = Markdown()

class NewEntryForm(forms.Form):
    title = forms.CharField(label="new_title", widget=forms.TextInput)
    content = forms.CharField(label='new_content', widget=forms.Textarea)

class EditForm(forms.Form):
    content = forms.CharField(label="", widget=forms.Textarea)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def entry(request, page_title):
    
    page = util.get_entry(page_title)

    try:
        return render(request, "encyclopedia/entry.html", {
            "content": markdown_tool.convert(page),
            "page_title": page_title
            })
    except: 
        message = "Page does not exist."
        return render(request, "encyclopedia/error.html", {
            "message": message,
            "not_exist": True
        })


def search(request):
    
    input = request.GET.get('q', '')

    if not input:

        return HttpResponseRedirect(reverse("index"))

    elif util.get_entry(input):

        return HttpResponseRedirect(reverse("entry", kwargs={'entry': input }))

    else:

        entries = util.list_entries()
        search_matches = []

        for entry in entries:
            if input.upper() in entry.upper():
                search_matches.append(entry)

        return render(request, "encyclopedia/index.html", {
            "entries": search_matches,
            "search": True
        })

def new_page(request):
    
    if request.method == "POST":

        form = NewEntryForm(request.POST)
        if form.is_valid():
            new_title = form.cleaned_data['title']
            new_content = form.cleaned_data['content']

            if util.get_entry(new_title):
                return render(request, "encyclopedia/error.html", {
                    "message": "Page already exists"
                })
            else:
                util.save_entry(new_title, new_content)

                return HttpResponseRedirect(reverse("entry", kwargs={'page_title': new_title }))

    else:

        return render(request, "encyclopedia/new_page.html", {
            "form": NewEntryForm
        })

def edit(request, page_title):
    
    if request.method == "GET":

        page = util.get_entry(page_title)

        return render(request, "encyclopedia/edit.html", {
            "page_title": page_title,
            "edit": EditForm(initial={'content': page}),
        })
    
    else:

        form = EditForm(request.POST)

        if form.is_valid():
            new_content = form.cleaned_data['content']
            util.save_entry(page_title, new_content)
            return HttpResponseRedirect(reverse("entry", kwargs={'page_title': page_title }))
        else:
            message = "Invalid form submission"
            return render(request, "encyclopedia/error.html", {
                "message": message
            })

def random_page(request):

    entries = util.list_entries()
    page = random.choice(entries)

    print(page)

    return HttpResponseRedirect(reverse("entry", kwargs={'page_title': page}))

