from django.shortcuts import redirect, render
from markdown2 import Markdown
from django import forms
from encyclopedia.util import get_entry
from . import util
import random
import os

# textfield form class 
class SearchForm(forms.Form):
    search = forms.CharField(label="", widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))

# declare global variables for alerts 
edited = False
deleted = False
new = False

# view for making new entry 
def new(request):

    global new
    
    # if we are posting to the new view, we are gonna check if the entry title already exists
    # if it doesn't exist, save to disk and redirect to the entry page
    # if it exists, show error message with link to edit the existing page with same name 
    # change global variable new to True to show alert message 

    if request.method == "POST":
        lower_list = []
        all = util.list_entries()
        
        for entry in all:
            lower_list.append(entry.lower())

        title = request.POST["title"].strip()

        if title.lower() in lower_list:
            return render(request, "encyclopedia/taken.html", {
                "invalid_name" : title,
                "link": "/edit/" + title 
            })
        
        description = request.POST["description"]
        
        with open ("/Users/raiyan/Documents/CS50W/wiki/entries/" + title + ".md", "w") as file:
            file.write(description)

        markdowner = Markdown()
        description = markdowner.convert(description)
        new = True
        return redirect(entries, name=title)
    
    # if request is get, just render new form HTML
    return render(request, "encyclopedia/new.html")

# this view just redirects to a random existing entry's page 
def pick(request):
    return redirect(entries, name=random.choice(util.list_entries()))

def index(request):

    global deleted

    # if we are posting from the index page, it means we are searching
    if request.method == "POST":
        form = SearchForm(request.POST)
        if form.is_valid():
            search = form.cleaned_data["search"]
            return redirect(entries, name=search)
    
    # check if we have just been redirected from a view where we deleted is True, so we can show alert 
    if deleted:
        deleted_dupe = deleted
        deleted = not deleted
    else:
        deleted_dupe = False

    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "form": SearchForm(),
        "deleted": deleted_dupe
    })

def entries(request, name):

    global edited
    global new
    global deleted


    # if we are posting to the entry page, it means we will either be editing or deleting an entry 
    # change global variables as needed 
    if request.method == 'POST':
        if "edit" in request.POST:
            return redirect(edit, name=name)
        elif "delete" in request.POST:
            deleted = True
            path = "/Users/raiyan/Documents/CS50W/wiki/entries/" + name + ".md"
            os.remove(path)
            return redirect(index)

    lower_list = []
    all = util.list_entries()
    matches_list = []
    lower = name.lower()

    for entry in all:
        lower_list.append(entry.lower())
    
    # populate partial substring matches list
    for i, entry in enumerate(lower_list):
        if name in lower_list[i]:
            matches_list.append(all[i])
    
    # check exact matches, making sure to account for edited and deleted alerts 
    if lower in lower_list:

        entry_info = util.get_entry(name)
        markdowner = Markdown()
        converted_html = markdowner.convert(entry_info)

        if edited:
            edited_dupe = edited
            edited = not edited
        else: 
            edited_dupe = False

        if new:
            new_dupe = new
            new = not new
        else:
            new_dupe = False

        return render(request, "encyclopedia/entry.html", {
        "entry": converted_html,
        "form": SearchForm(),
        "edited": edited_dupe,
        "new": new_dupe
        })
    
    # disply partial matches results page 
    elif matches_list:
        return render(request, "encyclopedia/results.html", {
        "entries": matches_list,
        "name": name,
        "form": SearchForm()
        })
    
    # display error message if no matches or partial matches 
    else:
        return render(request, "encyclopedia/error.html", {
        "invalid_name": name,
        "form": SearchForm()
        })

def edit(request, name):

    global edited

    # if we are posting to this page, it means the entry has been edited, chanage edited variable
    if request.method == "POST":
        with open("/Users/raiyan/Documents/CS50W/wiki/entries/" + name + ".md", "w") as file:
            file.write(request.POST["description"])
        edited = True
        return redirect(entries, name=name)
    
    # if request is GET, render populated edit page with current description info
    else:
        return render(request, "encyclopedia/edit.html", {
            "title": name,
            "description": util.get_entry(name)
            })


    
