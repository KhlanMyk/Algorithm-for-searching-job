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
                        job = {
                            'title': card.find('h2', class_='jobTitle') or 'N/A',
                            'company': card.find('span', class_='companyName') or 'N/A',
                            'location': card.find('div', class_='companyLocation') or 'N/A',
                            'job_url': 'https://www.indeed.com' + (card.find('a')['href'] if card.find('a') else ''),
                            'description': card.find('div', class_='job-snippet') or '',
                            'source': 'Indeed',
                            'posted_date': datetime.now().isoformat(),
                        }
                        job['job_id'] = self.generate_job_id(job)
                        jobs.append(job)
                    except:
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
        
        print(f"\n📊 Total jobs found across all sources: {len(all_jobs)}")
        if len(all_jobs) > 0:
            print(f"   - GitHub Jobs: {len(github_jobs)}")
            print(f"   - Indeed: {len(indeed_jobs)}")
            print(f"   - LinkedIn: {len(linkedin_jobs)}")
            print(f"   - Stack Overflow: {len(stackoverflow_jobs)}\n")
        else:
            print("   No jobs found (external sources may not be accessible)\n")
        
        return all_jobs
