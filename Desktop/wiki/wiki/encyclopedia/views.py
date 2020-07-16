from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
import markdown2
from . import util
from django import forms
import secrets

class NewPage(forms.Form):
    title=forms.CharField(label= "title")
    markuptext= forms.CharField(label="markuptext")

class EditPage(forms.Form):
    markuptext= forms.CharField(label="text")


def index(request):
    return render(request, "encyclopedia/index.html", {
    "entries": util.list_entries()
          })

def search(request):
    query = request.GET['q']
    filename=util.get_entry(query)
    entries=util.list_entries()
    if filename is None:
        list=[]
        for entry in entries:
            if query.lower() in entry.lower():
                list.append(entry)
        if not list:
            return render(request,"encyclopedia/error.html", {"error": "search not found"})
        else:
            return render(request, "encyclopedia/substring.html", {"entries":list})

    file=markdown2.markdown(filename)
    return render(request, "encyclopedia/display.html", {
    "content": file , "titlename":query})

def wiki(request,title):
    titlename=title
    file=util.get_entry(title)
    if file is None:
        return render(request, "encyclopedia/error.html",{"error": "page not found"})
    else:
        file=markdown2.markdown(file)
        return render(request, "encyclopedia/display.html", {
        "content": file , "titlename":titlename})


def newpage(request):
    if request.method == "POST":
        form= NewPage(request.POST)
        if form.is_valid():
            title=form.cleaned_data["title"]
            content=form.cleaned_data["markuptext"]
            entries=util.list_entries()
            for entry in entries:
                if title.lower() in entry.lower():
                    return render(request,"encyclopedia/error.html",{
                    "error": "sorry page with this title already exists"
                    })

            util.save_entry(title,content)
            content=markdown2.markdown(content)
            return render(request,"encyclopedia/display.html",{
            "content":content,"titlename":title})
    return render(request, "encyclopedia/newpage.html",{
    "form":NewPage()
    })

def edit(request,entry):
    if request.method == "POST":
        form= EditPage(request.POST)
        if form.is_valid():
            title=entry
            content=form.cleaned_data["markuptext"]
            util.save_entry(title,content)
            content=markdown2.markdown(content)
            return render(request,"encyclopedia/display.html",{
            "content":content, "titlename":title
            })

    titlename=entry
    file=util.get_entry(entry)
    data = {'markuptext':file}
    form=EditPage(initial=data)
    return render(request, "encyclopedia/edit.html",{
    "form":form, "titlename":titlename
    })

def random(request):
    entries=util.list_entries()
    filename=secrets.choice(entries)
    entry=util.get_entry(filename)
    content=markdown2.markdown(entry)
    return render(request, "encyclopedia/display.html",{
    "content":content, "titlename":filename
    })
