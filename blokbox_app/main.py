from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import requests

app = FastAPI()

def get_default_stats():
    return {
        "Top Packages": ["requests", "numpy", "pandas", "flask", "django"],
        "PyPI Stats": {
            "Total Packages": "400k+",
            "Most Downloaded": "requests",
            "Trending": ["httpx", "rich", "fastapi"]
        }
    }

def get_package_stats(pkg_name):
    url = f"https://pypi.org/pypi/{pkg_name}/json"
    resp = requests.get(url)
    if resp.status_code != 200:
        return {"error": "Package not found"}
    data = resp.json()
    info = data.get("info", {})
    releases = data.get("releases", {})

    # Fetch usage statistics from PyPI Stats API as an alternative to PePy
    pypistats_url = f"https://pypistats.org/api/packages/{pkg_name}/recent"
    pypistats_resp = requests.get(pypistats_url)
    downloads_last_day = downloads_last_week = downloads_last_month = "N/A"
    if pypistats_resp.status_code == 200:
        pypistats_data = pypistats_resp.json()
        stats_data = pypistats_data.get("data", {})
        downloads_last_day = stats_data.get("last_day", "N/A")
        downloads_last_week = stats_data.get("last_week", "N/A")
        downloads_last_month = stats_data.get("last_month", "N/A")

    stats = {
        "Name": info.get("name"),
        "Version": info.get("version"),
        "Summary": info.get("summary"),
        "Author": info.get("author_email") or info.get("author"),
        "License": info.get("license"),
        "Release Count": len(releases),
        "Home Page": info.get("home_page"),
        "Project URL": info.get("project_url"),
        "Requires Python": info.get("requires_python"),
        "Classifiers": info.get("classifiers"),
        "Release History": list(releases.keys())[-5:][::-1],
        "Downloads Last Day": downloads_last_day,
        "Downloads Last Week": downloads_last_week,
        "Downloads Last Month": downloads_last_month,
    }
    return stats

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    stats = get_default_stats()
    html = f"""
    <html>
    <head>
        <title>Blokbox PyPI Stats</title>
    </head>
    <body>
        <h1>Blokbox PyPI Statistics</h1>
        <form action="/search" method="get">
            <input type="text" name="pkg" placeholder="Enter PyPI package name">
            <button type="submit">Search</button>
        </form>
        <h2>Default Statistics</h2>
        <ul>
            <li>Top Packages: {', '.join(stats['Top Packages'])}</li>
            <li>Total Packages: {stats['PyPI Stats']['Total Packages']}</li>
            <li>Most Downloaded: {stats['PyPI Stats']['Most Downloaded']}</li>
            <li>Trending: {', '.join(stats['PyPI Stats']['Trending'])}</li>
        </ul>
    </body>
    </html>
    """
    return html

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, pkg: str = ""):
    stats = get_package_stats(pkg)
    if "error" in stats:
        html = f"""
        <html>
        <body>
            <h1>Package '{pkg}' not found.</h1>
            <a href="/">Back</a>
        </body>
        </html>
        """
        return html
    html = f"""
    <html>
    <head>
        <title>Blokbox PyPI Stats - {stats['Name']}</title>
    </head>
    <body>
        <h1>Statistics for '{stats['Name']}'</h1>
        <ul>
            <li>Version: {stats['Version']}</li>
            <li>Summary: {stats['Summary']}</li>
            <li>Author: {stats['Author']}</li>
            <li>License: {stats['License']}</li>
            <li>Release Count: {stats['Release Count']}</li>
            <li>Home Page: <a href="{stats['Home Page']}">{stats['Home Page']}</a></li>
            <li>Project URL: {stats['Project URL']}</li>
            <li>Requires Python: {stats['Requires Python']}</li>
            <li>Classifiers: <ul>{"".join(f"<li>{c}</li>" for c in stats['Classifiers'])}</ul></li>
            <li>Recent Releases: {', '.join(stats['Release History'])}</li>
            <li>Downloads Last Day: {stats['Downloads Last Day']}</li>
            <li>Downloads Last Week: {stats['Downloads Last Week']}</li>
            <li>Downloads Last Month: {stats['Downloads Last Month']}</li>
        </ul>
        <a href="/">Back</a>
    </body>
    </html>
    """
    return html
