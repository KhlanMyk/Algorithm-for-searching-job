"""
Job scraper module for collecting job listings from various sources
"""
import requests
import hashlib
from datetime import datetime
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import json
import sys
import os
from urllib.parse import urlparse, urljoin, urlencode, parse_qs, unquote

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class JobScraper:
    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Import config for API keys
        try:
            from config.config import INDEED_API_KEY, INDEED_PUBLISHER_ID, LINKEDIN_API_KEY
            self.indeed_api_key = INDEED_API_KEY
            self.indeed_publisher_id = INDEED_PUBLISHER_ID
            self.linkedin_api_key = LINKEDIN_API_KEY
        except:
            self.indeed_api_key = ""
            self.indeed_publisher_id = ""
            self.linkedin_api_key = ""
    
    @staticmethod
    def generate_job_id(job_data: Dict) -> str:
        """Generate unique ID for job"""
        unique_string = f"{job_data.get('title', '')}{job_data.get('company', '')}{job_data.get('job_url', '')}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    @staticmethod
    def _normalize_text(text: str) -> str:
        return " ".join((text or "").split()).strip().lower()

    def _keyword_match(self, text: str, keywords: List[str]) -> bool:
        haystack = self._normalize_text(text)
        return any(self._normalize_text(k) in haystack for k in keywords if k)

    def _extract_json_ld_jobs(self, soup: BeautifulSoup, base_url: str, source_name: str, keywords: List[str]) -> List[Dict]:
        jobs = []
        scripts = soup.find_all("script", attrs={"type": "application/ld+json"})
        for script in scripts:
            try:
                data = json.loads(script.string or "")
            except Exception:
                continue

            items = data if isinstance(data, list) else [data]
            for item in items:
                if isinstance(item, dict) and item.get("@type") == "JobPosting":
                    title = item.get("title", "")
                    description = item.get("description", "")
                    if keywords and not self._keyword_match(f"{title} {description}", keywords):
                        continue

                    hiring_org = item.get("hiringOrganization", {}) or {}
                    company = hiring_org.get("name", "") if isinstance(hiring_org, dict) else str(hiring_org)
                    job_url = item.get("url") or item.get("applicationUrl") or base_url
                    if job_url and job_url.startswith("/"):
                        job_url = urljoin(base_url, job_url)

                    location = ""
                    job_location = item.get("jobLocation")
                    if isinstance(job_location, dict):
                        address = job_location.get("address", {}) or {}
                        location = address.get("addressLocality") or address.get("addressRegion") or address.get("addressCountry") or ""
                    elif isinstance(job_location, list) and job_location:
                        address = job_location[0].get("address", {}) if isinstance(job_location[0], dict) else {}
                        location = address.get("addressLocality") or address.get("addressRegion") or address.get("addressCountry") or ""

                    job = {
                        'title': title or 'N/A',
                        'company': company or 'N/A',
                        'location': location or 'N/A',
                        'job_url': job_url or base_url,
                        'description': BeautifulSoup(description, 'html.parser').get_text(" ")[:1000] if description else '',
                        'source': source_name,
                        'posted_date': item.get("datePosted", datetime.now().isoformat()),
                    }
                    job['job_id'] = self.generate_job_id(job)
                    jobs.append(job)
        return jobs

    def _extract_result_url(self, href: str) -> Optional[str]:
        if not href:
            return None
        if "duckduckgo.com/l/?" in href:
            parsed = urlparse(href)
            uddg = parse_qs(parsed.query).get("uddg", [])
            if uddg:
                return unquote(uddg[0])
        return href

    def _search_duckduckgo(self, query: str, max_results: int) -> List[str]:
        urls = []
        try:
            url = "https://duckduckgo.com/html/"
            response = requests.get(url, params={"q": query}, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            for link in soup.select("a.result__a"):
                href = self._extract_result_url(link.get("href"))
                if href and href.startswith("http"):
                    urls.append(href)
                if len(urls) >= max_results:
                    break
        except Exception as e:
            print(f"❌ Error searching DuckDuckGo: {e}")
        return urls

    def scrape_employer_site_url(self, url: str, keywords: List[str]) -> List[Dict]:
        jobs = []
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')

            domain = urlparse(url).netloc
            source_name = f"Employer Site: {domain}"
            jobs.extend(self._extract_json_ld_jobs(soup, url, source_name, keywords))
        except Exception as e:
            print(f"❌ Error scraping employer site {url}: {e}")
        return jobs

    def scrape_employer_sites(self, keywords: List[str]) -> List[Dict]:
        jobs = []
        try:
            from config.config import (
                EMPLOYER_SITE_URLS,
                SEARCH_ENGINE_ENABLED,
                SEARCH_ENGINE_PROVIDER,
                SEARCH_ENGINE_MAX_RESULTS,
                EMPLOYER_SITE_PATH_KEYWORDS,
            )
        except Exception:
            EMPLOYER_SITE_URLS = []
            SEARCH_ENGINE_ENABLED = False
            SEARCH_ENGINE_PROVIDER = "duckduckgo"
            SEARCH_ENGINE_MAX_RESULTS = 10
            EMPLOYER_SITE_PATH_KEYWORDS = ["careers", "career", "jobs", "job", "vacancies", "opportunities", "openings"]

        seen_urls = set()

        # 1) Direct employer URLs (manual list)
        for site_url in EMPLOYER_SITE_URLS or []:
            if site_url not in seen_urls:
                seen_urls.add(site_url)
                jobs.extend(self.scrape_employer_site_url(site_url, keywords))

        # 2) Search-engine discovery (no API keys)
        if SEARCH_ENGINE_ENABLED:
            for keyword in keywords:
                query = f"{keyword} careers OR jobs site:.com"
                if SEARCH_ENGINE_PROVIDER == "duckduckgo":
                    results = self._search_duckduckgo(query, SEARCH_ENGINE_MAX_RESULTS)
                else:
                    results = []

                for result_url in results:
                    path = urlparse(result_url).path.lower()
                    if any(k in path for k in EMPLOYER_SITE_PATH_KEYWORDS):
                        if result_url not in seen_urls:
                            seen_urls.add(result_url)
                            jobs.extend(self.scrape_employer_site_url(result_url, keywords))

        return jobs
    
    def scrape_github_jobs(self, keywords: List[str]) -> List[Dict]:
        """Scrape jobs from GitHub Jobs API"""
        jobs = []
        
        for keyword in keywords:
            try:
                url = "https://jobs.github.com/positions.json"
                params = {"description": keyword}
                
                response = requests.get(url, params=params, timeout=self.timeout, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                
                for job_data in data:
                    job = {
                        'title': job_data.get('title', ''),
                        'company': job_data.get('company', ''),
                        'location': job_data.get('location', ''),
                        'job_url': job_data.get('url', ''),
                        'description': job_data.get('description', ''),
                        'source': 'GitHub Jobs',
                        'posted_date': job_data.get('created_at', ''),
                    }
                    job['job_id'] = self.generate_job_id(job)
                    jobs.append(job)
                
                print(f"✅ Found {len(data)} jobs from GitHub Jobs for '{keyword}'")
            
            except Exception as e:
                print(f"❌ Error scraping GitHub Jobs: {e}")
        
        return jobs
    
    def scrape_job_board(self, url: str, source_name: str) -> List[Dict]:
        """Generic job board scraper"""
        jobs = []
        
        try:
            response = requests.get(url, timeout=self.timeout, headers=self.headers)
            response.raise_for_status()
            
            # This is a basic template - customize based on the website structure
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find job listings (customize selectors based on the website)
            job_listings = soup.find_all('div', class_=['job-card', 'job-listing', 'job-result'])
            
            for listing in job_listings:
                try:
                    job = {
                        'title': listing.find(['h2', 'h3', 'a'], class_=['job-title', 'title']) or 'N/A',
                        'company': listing.find(['span', 'div'], class_=['company', 'employer']) or 'N/A',
                        'location': listing.find(['span', 'div'], class_=['location', 'job-location']) or 'N/A',
                        'job_url': listing.find('a', href=True) or '#',
                        'description': listing.find('p') or '',
                        'source': source_name,
                        'posted_date': datetime.now().isoformat(),
                    }
                    job['job_id'] = self.generate_job_id(job)
                    jobs.append(job)
                except:
                    continue
            
            print(f"✅ Found {len(jobs)} jobs from {source_name}")
        
        except Exception as e:
            print(f"❌ Error scraping {source_name}: {e}")
        
        return jobs
    
    def scrape_indeed_api(self, keywords: List[str]) -> List[Dict]:
        """Scrape Indeed using official API"""
        jobs = []
        
        if not self.indeed_api_key or not self.indeed_publisher_id:
            print("⚠️  Indeed API key not configured (using web scraping fallback)")
            return jobs
        
        for keyword in keywords:
            try:
                url = "https://api.indeed.com/ads/apisearch"
                
                params = {
                    'publisher': self.indeed_publisher_id,
                    'q': keyword,
                    'l': 'USA',
                    'sort': 'date',
                    'radius': '25',
                    'st': 'internship',
                    'jt': 'internship',
                    'start': '0',
                    'limit': '25',
                    'fromage': '7',
                    'format': 'json',
                    'userip': '1.2.3.4',
                    'useragent': 'Mozilla/5.0'
                }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                if 'results' in data:
                    for job_data in data['results'][:10]:
                        job = {
                            'title': job_data.get('jobtitle', ''),
                            'company': job_data.get('company', ''),
                            'location': job_data.get('locations', [{}])[0] if job_data.get('locations') else '',
                            'job_url': job_data.get('url', ''),
                            'description': job_data.get('snippet', ''),
                            'source': 'Indeed (API)',
                            'posted_date': job_data.get('date', ''),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    
                    print(f"✅ Found {len(data.get('results', [])[:10])} jobs from Indeed API for '{keyword}'")
            
            except Exception as e:
                print(f"❌ Error scraping Indeed API: {e}")
        
        return jobs
    
    def scrape_linkedin_api(self, keywords: List[str]) -> List[Dict]:
        """Scrape LinkedIn using official API"""
        jobs = []
        
        if not self.linkedin_api_key:
            print("⚠️  LinkedIn API key not configured (using web scraping fallback)")
            return jobs
        
        try:
            from linkedin_jobs_crawler.glassdoor.glassdoor import Glassdoor
            from linkedin_jobs_crawler import LinkedInScraper
            
            for keyword in keywords:
                try:
                    scraper = LinkedInScraper(
                        chrome_driver_path=None,
                        headless_browser=True
                    )
                    
                    jobs_list = scraper.scrape_jobs(
                        keyword=keyword,
                        locations=['United States'],
                        job_types=['Internship'],
                        experience_levels=['Entry level'],
                        limit=10
                    )
                    
                    for job_data in jobs_list:
                        job = {
                            'title': job_data.get('job_title', ''),
                            'company': job_data.get('company', ''),
                            'location': job_data.get('location', ''),
                            'job_url': job_data.get('job_url', ''),
                            'description': job_data.get('description', ''),
                            'source': 'LinkedIn (API)',
                            'posted_date': datetime.now().isoformat(),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    
                    print(f"✅ Found {len(jobs_list)} jobs from LinkedIn API for '{keyword}'")
                
                except Exception as e:
                    print(f"❌ Error with LinkedIn API for '{keyword}': {e}")
        
        except ImportError:
            print("⚠️  LinkedIn API library not installed (using web scraping)")
        
        return jobs
    
    def scrape_indeed_api(self, keywords: List[str]) -> List[Dict]:
        """Scrape Indeed using official API"""
        jobs = []
        
        if not self.indeed_api_key or not self.indeed_publisher_id:
            print("⚠️  Indeed API keys not configured")
            return jobs
        
        for keyword in keywords:
            try:
                url = "https://api.indeed.com/ads/apisearch"
                
                params = {
                    'publisher': self.indeed_publisher_id,
                    'q': keyword + ' internship',
                    'l': 'United States',
                    'sort': 'date',
                    'radius': '25',
                    'jt': 'internship',
                    'start': '0',
                    'limit': '25',
                    'fromage': '7',
                    'format': 'json',
                    'userip': '1.2.3.4',
                    'useragent': 'Mozilla/5.0'
                }
                
                response = requests.get(url, params=params, timeout=self.timeout)
                response.raise_for_status()
                
                data = response.json()
                
                if 'results' in data:
                    for job_data in data['results'][:10]:
                        job = {
                            'title': job_data.get('jobtitle', ''),
                            'company': job_data.get('company', ''),
                            'location': job_data.get('locations', [{}])[0] if job_data.get('locations') else 'USA',
                            'job_url': job_data.get('url', ''),
                            'description': job_data.get('snippet', ''),
                            'source': 'Indeed (Official API)',
                            'posted_date': job_data.get('date', ''),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    
                    print(f"✅ Found {min(len(data.get('results', [])), 10)} jobs from Indeed API for '{keyword}'")
            
            except Exception as e:
                print(f"❌ Error with Indeed API: {e}")
        
        return jobs

    def scrape_indeed_snapshot(self, keywords: List[str]) -> List[Dict]:
        """Scrape Indeed for jobs (basic version without API)"""
        jobs = []

        for keyword in keywords:
            try:
                url = f"https://www.indeed.com/jobs?q={keyword}+internship&limit=25"

                response = requests.get(url, timeout=self.timeout, headers=self.headers)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Indeed uses dynamic loading, so this captures only visible results
                job_cards = soup.find_all('div', class_='job_seen_beacon')

                for card in job_cards[:10]:  # Limit to 10 per keyword
                    try:
                        title_elem = card.find('h2', class_='jobTitle')
                        company_elem = card.find('span', class_='companyName')
                        location_elem = card.find('div', class_='companyLocation')
                        link_elem = card.find('a', href=True)

                        job = {
                            'title': title_elem.get_text(strip=True) if title_elem else 'N/A',
                            'company': company_elem.get_text(strip=True) if company_elem else 'N/A',
                            'location': location_elem.get_text(strip=True) if location_elem else 'N/A',
                            'job_url': 'https://www.indeed.com' + (link_elem.get('href') if link_elem else ''),
                            'description': card.find('div', class_='job-snippet').get_text(" ", strip=True) if card.find('div', class_='job-snippet') else '',
                            'source': 'Indeed (Web)',
                            'posted_date': datetime.now().isoformat(),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    except Exception:
                        continue

                print(f"✅ Found {len(job_cards[:10])} jobs from Indeed for '{keyword}'")

            except Exception as e:
                print(f"❌ Error scraping Indeed: {e}")

        return jobs
    
    def scrape_linkedin_jobs(self, keywords: List[str]) -> List[Dict]:
        """Scrape LinkedIn Jobs"""
        jobs = []
        
        for keyword in keywords:
            try:
                # LinkedIn URL structure for job search
                search_term = keyword.replace(" ", "%20")
                url = f"https://www.linkedin.com/jobs/search/?keywords={search_term}&position=1&pageNum=0"
                
                response = requests.get(url, timeout=self.timeout, headers=self.headers)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find job listings in LinkedIn's structure
                job_cards = soup.find_all('div', class_='base-card')
                
                for card in job_cards[:8]:  # Limit to 8 per keyword
                    try:
                        title_elem = card.find('h3', class_='base-search-card__title')
                        company_elem = card.find('h4', class_='base-search-card__subtitle')
                        location_elem = card.find('span', class_='job-search-card__location')
                        link_elem = card.find('a', class_='base-card__full-link')
                        
                        job = {
                            'title': title_elem.text.strip() if title_elem else 'N/A',
                            'company': company_elem.text.strip() if company_elem else 'N/A',
                            'location': location_elem.text.strip() if location_elem else 'N/A',
                            'job_url': link_elem.get('href', '') if link_elem else '#',
                            'description': '',
                            'source': 'LinkedIn',
                            'posted_date': datetime.now().isoformat(),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    except:
                        continue
                
                if len(job_cards) > 0:
                    print(f"✅ Found {min(len(job_cards), 8)} jobs from LinkedIn for '{keyword}'")
                else:
                    print(f"⚠️  No jobs found on LinkedIn for '{keyword}' (may need login)")
            
            except Exception as e:
                print(f"❌ Error scraping LinkedIn: {e}")
        
        return jobs
    
    def scrape_stackoverflow_jobs(self, keywords: List[str]) -> List[Dict]:
        """Scrape Stack Overflow Jobs"""
        jobs = []
        
        try:
            # Stack Overflow Jobs API/scraping
            for keyword in keywords:
                try:
                    search_term = keyword.replace(" ", "+")
                    url = f"https://stackoverflow.com/jobs?q={search_term}&sort=i"
                    
                    response = requests.get(url, timeout=self.timeout, headers=self.headers)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find job listings
                    job_cards = soup.find_all('div', class_='s-job-card')
                    
                    for card in job_cards[:8]:  # Limit to 8 per keyword
                        try:
                            title_elem = card.find('h2')
                            company_elem = card.find('h3')
                            link_elem = card.find('a', class_='s-link')
                            
                            job = {
                                'title': title_elem.text.strip() if title_elem else 'N/A',
                                'company': company_elem.text.strip() if company_elem else 'N/A',
                                'location': 'Remote',
                                'job_url': 'https://stackoverflow.com' + link_elem.get('href', '') if link_elem else '#',
                                'description': '',
                                'source': 'Stack Overflow',
                                'posted_date': datetime.now().isoformat(),
                            }
                            job['job_id'] = self.generate_job_id(job)
                            jobs.append(job)
                        except:
                            continue
                    
                    if len(job_cards) > 0:
                        print(f"✅ Found {min(len(job_cards), 8)} jobs from Stack Overflow for '{keyword}'")
                    else:
                        print(f"⚠️  No jobs found on Stack Overflow for '{keyword}'")
                
                except Exception as e:
                    print(f"❌ Error scraping Stack Overflow: {e}")
        
        except Exception as e:
            print(f"❌ Error with Stack Overflow scraper: {e}")
        
        return jobs

    
    def scrape_all_sources(self, keywords: List[str]) -> List[Dict]:
        """Scrape all configured job sources"""
        all_jobs = []
        
        print("\n🔍 Starting job search across all sources...")
        print(f"📍 Searching for: {', '.join(keywords)}\n")
        print("📊 Sources being searched:")
        
        # GitHub Jobs (most reliable for this demo)
        print("  📌 GitHub Jobs (API)")
        github_jobs = self.scrape_github_jobs(keywords)
        all_jobs.extend(github_jobs)
        
        # Indeed - Try API first, fallback to web scraping
        print("  📌 Indeed (Official API or Web Scraping)")
        if self.indeed_api_key and self.indeed_publisher_id:
            indeed_jobs = self.scrape_indeed_api(keywords)
        else:
            indeed_jobs = self.scrape_indeed_snapshot(keywords)
        all_jobs.extend(indeed_jobs)
        
        # LinkedIn - Try API first, fallback to web scraping
        print("  📌 LinkedIn (Official API or Web Scraping)")
        if self.linkedin_api_key:
            linkedin_jobs = self.scrape_linkedin_api(keywords)
        else:
            linkedin_jobs = self.scrape_linkedin_jobs(keywords)
        all_jobs.extend(linkedin_jobs)
        
        # Stack Overflow Jobs (tech jobs)
        print("  📌 Stack Overflow (Web Scraping)")
        stackoverflow_jobs = self.scrape_stackoverflow_jobs(keywords)
        all_jobs.extend(stackoverflow_jobs)

        # Employer sites via search engine + direct URLs
        try:
            from config.config import SEARCH_EMPLOYER_SITES
        except Exception:
            SEARCH_EMPLOYER_SITES = False

        if SEARCH_EMPLOYER_SITES:
            print("  📌 Employer Sites (Search Engine + Direct URLs)")
            employer_jobs = self.scrape_employer_sites(keywords)
            all_jobs.extend(employer_jobs)
        else:
            employer_jobs = []
        
        print(f"\n📊 Total jobs found across all sources: {len(all_jobs)}")
        if len(all_jobs) > 0:
            print(f"   - GitHub Jobs: {len(github_jobs)}")
            print(f"   - Indeed: {len(indeed_jobs)}")
            print(f"   - LinkedIn: {len(linkedin_jobs)}")
            print(f"   - Stack Overflow: {len(stackoverflow_jobs)}\n")
            if SEARCH_EMPLOYER_SITES:
                print(f"   - Employer Sites: {len(employer_jobs)}\n")
        else:
            print("   No jobs found (external sources may not be accessible)\n")
        
        return all_jobs
