from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.contrib import messages
from .utils import (
    process_file_with_graph,
    get_llm,
    extract_text_from_file,
    extract_text_chunks,
    fetch_text_from_links  
)
from langchain.schema import HumanMessage
import os
import requests
from bs4 import BeautifulSoup






def index(request):
    result = None
    input_text = ''
    file_path = ''
    history = request.session.get("history", [])
    rules = request.session.get("rules", [])
    rag_links = request.session.get("rag_links", [])
    upload_dir = os.path.join(default_storage.location, 'uploads')
    uploaded_files = os.listdir(upload_dir) if os.path.exists(upload_dir) else []

    if request.method == 'POST' and 'input_text' in request.POST:
        input_text = request.POST.get('input_text')
        uploaded_file = request.FILES.get('uploaded_file')

        if uploaded_file:
            try:
                relative_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
                file_path = os.path.join(default_storage.location, relative_path)
                messages.success(request, f"✅ File '{uploaded_file.name}' uploaded successfully.")

                file_text = extract_text_from_file(file_path)
                request.session["file_text"] = file_text
                request.session["file_name"] = uploaded_file.name

                chunks = extract_text_chunks(file_text)
                summaries = []
                llm = get_llm(request)
                for i, chunk in enumerate(chunks):
                    print(f"🔍 Preprocessing chunk {i+1}/{len(chunks)}")
                    resp = llm.invoke([
                        HumanMessage(content=f"Context:\n{chunk}\n\nSummarize this chunk.")
                    ])
                    summaries.append(resp.content)

                request.session["file_summaries"] = summaries
                request.session.modified = True

                uploaded_files = os.listdir(upload_dir)

            except Exception as e:
                messages.error(request, f"❌ File upload failed: {str(e)}")

        if not file_path and request.session.get("file_name"):
            file_path = os.path.join(upload_dir, request.session["file_name"])

        # ✅ Summarize RAG URLs
        if rag_links:
            url_summaries = {}
            llm = get_llm(request)
            for url in rag_links:
                try:
                    print(f"🌐 Fetching and summarizing URL: {url}")
                    raw_text = fetch_text_from_links([url])
                    print(f"📝 Raw text from {url}:\n{raw_text[:1000]}")  # Print first 1000 chars
                    chunks = extract_text_chunks(raw_text)
                    summaries = []
                    for i, chunk in enumerate(chunks):
                        print(f"🔍 Summarizing URL chunk {i+1}/{len(chunks)}")
                        response = llm.invoke([
                            HumanMessage(content=f"Context:\n{chunk}\n\nSummarize this for knowledge extraction.")
                        ])
                        summaries.append(response.content)
                    url_summaries[url] = summaries
                except Exception as e:
                    print(f"❌ Failed to summarize {url}: {e}")
            request.session["url_summaries"] = url_summaries
            request.session.modified = True

        # ✅ Process final answer
        if input_text:
            try:
                result = process_file_with_graph(request, input_text, file_path)

                if file_path and os.path.exists(file_path):
                    messages.success(request, f"🧠 File '{os.path.basename(file_path)}' was read and processed successfully.")

                clean_result = result.copy()
                if "request" in clean_result:
                    del clean_result["request"]

                history.append({
                    "question": input_text,
                    "result": clean_result
                })
                request.session["history"] = history
                request.session.modified = True

            except Exception as e:
                messages.error(request, f"❌ Failed to process: {str(e)}")

    return render(request, 'index.html', {
        'result': result,
        'history': history,
        'question': input_text,
        'uploaded_files': uploaded_files,
        'rules': rules,
        'links': rag_links,
    })


def delete_file(request, filename):
    upload_dir = os.path.join(default_storage.location, 'uploads')
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        messages.success(request, f"🗑️ File '{filename}' deleted.")

        if request.session.get("file_name") == filename:
            for key in ["file_name", "file_text", "file_summaries"]:
                request.session.pop(key, None)
            request.session.modified = True
    else:
        messages.error(request, "❌ File not found.")
    return redirect('index')


def set_model_settings(request):
    if request.method == 'POST':
        model = request.POST.get('model_name')
        api_key = request.POST.get('api_key')
        rules = request.session.get("rules", [])

        try:
            llm = get_llm({
                "session": {
                    "model_name": model,
                    "api_key": api_key,
                    "rules": rules
                }
            })
            llm.invoke([HumanMessage(content="Say hello!")])

            request.session['model_name'] = model
            request.session['api_key'] = api_key
            request.session.modified = True

        except Exception as e:
            messages.error(request, f"❌ Invalid API Key or Model: {str(e)}")

        return redirect('index')


def reset_settings(request):
    upload_dir = os.path.join(default_storage.location, 'uploads')
    if os.path.exists(upload_dir):
        for file in os.listdir(upload_dir):
            file_path = os.path.join(upload_dir, file)
            if os.path.isfile(file_path):
                os.remove(file_path)

    for key in ["file_text", "file_name", "file_summaries", "history", "model_name", "api_key", "rules", "rag_links"]:
        request.session.pop(key, None)

    request.session.modified = True
    messages.success(request, "✅ All settings, files, rules, links, and history have been reset.")
    return redirect('index')


def upload_file_only(request):
    if request.method == 'POST' and request.FILES.get('uploaded_file'):
        uploaded_file = request.FILES['uploaded_file']
        try:
            relative_path = default_storage.save(f"uploads/{uploaded_file.name}", uploaded_file)
            file_path = os.path.join(default_storage.location, relative_path)
            file_text = extract_text_from_file(file_path)

            request.session["file_text"] = file_text
            request.session["file_name"] = uploaded_file.name

            chunks = extract_text_chunks(file_text)
            summaries = []
            llm = get_llm(request)
            for i, chunk in enumerate(chunks):
                print(f"🔍 Preprocessing chunk {i+1}/{len(chunks)}")
                resp = llm.invoke([HumanMessage(content=f"Context:\n{chunk}\n\nSummarize this chunk.")])
                summaries.append(resp.content)
            request.session["file_summaries"] = summaries
            request.session.modified = True

            messages.success(request, f"✅ File '{uploaded_file.name}' uploaded and preprocessed for future use.")
        except Exception as e:
            messages.error(request, f"❌ Failed to upload file: {str(e)}")

    return redirect('index')


def add_rule(request):
    if request.method == 'POST':
        rule_text = request.POST.get("rule")
        rules = request.session.get("rules", [])
        if rule_text and rule_text not in rules:
            rules.append(rule_text)
            request.session["rules"] = rules
            request.session.modified = True
            messages.success(request, f"✅ Rule added: {rule_text}")
    return redirect("index")


def delete_rule(request, rule):
    rules = request.session.get("rules", [])
    if rule in rules:
        rules.remove(rule)
        request.session["rules"] = rules
        request.session.modified = True
        messages.success(request, f"🗑️ Rule '{rule}' deleted.")
    else:
        messages.error(request, "❌ Rule not found.")
    return redirect('index')




def fetch_text_from_url(url):
    try:
        response = requests.get(url, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")
        # Remove script/style
        for s in soup(["script", "style"]): s.extract()
        return soup.get_text(separator=" ", strip=True)
    except Exception as e:
        return ""

def add_link(request):
    if request.method == 'POST':
        new_link = request.POST.get("url")
        rag_links = request.session.get("rag_links", [])
        url_summaries = request.session.get("url_summaries", {})

        model = request.session.get("model_name")
        api_key = request.session.get("api_key")
        if not model or not api_key:
            messages.error(request, "❌ Please set a model and API key before adding URLs.")
            return redirect("index")

        if not new_link:
            messages.error(request, "❌ No URL provided.")
            return redirect("index")

        if new_link in rag_links:
            messages.warning(request, "⚠️ This URL is already added.")
            return redirect("index")

        try:
            print(f"🌐 Fetching: {new_link}")
            raw_text = fetch_text_from_url(new_link)
            print(f"📝 Raw fetched text from {new_link}:\n{'-'*40}\n{raw_text[:1000]}\n{'-'*40}")

            if raw_text.strip():
                chunks = extract_text_chunks(raw_text)
                summaries = []
                llm = get_llm(request)

                for i, chunk in enumerate(chunks):
                    print(f"🔍 Summarizing URL chunk {i+1}/{len(chunks)}")
                    resp = llm.invoke([HumanMessage(content=f"Summarize this chunk:\n\n{chunk}")])
                    summaries.append(resp.content)

                rag_links.append(new_link)
                url_summaries[new_link] = summaries
                request.session["rag_links"] = rag_links
                request.session["url_summaries"] = url_summaries
                request.session.modified = True

                messages.success(request, f"✅ Link added and processed: {new_link}")
            else:
                messages.warning(request, f"⚠️ The link was fetched, but no usable text was found.")

        except Exception as e:
            print(f"❌ Error processing link {new_link}: {e}")
            messages.error(request, f"❌ Failed to process the link: {e}")

    return redirect("index")



def delete_link(request, link):
    rag_links = request.session.get("rag_links", [])
    if link in rag_links:
        rag_links.remove(link)
        request.session["rag_links"] = rag_links
        request.session.modified = True
        messages.success(request, f"🗑️ Link removed: {link}")
    return redirect("index")
