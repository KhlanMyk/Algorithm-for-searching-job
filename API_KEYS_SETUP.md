# API Keys Setup Guide

This guide shows how to get official API credentials for Indeed, LinkedIn, and other job boards.

## 📌 Indeed API

### Getting Indeed Publisher ID & API Key

1. **Go to Indeed Developer Portal**
   - Visit: https://opensource.indeedeng.io/api-documentation/

2. **Register for Free Account**
   - Click "Sign Up" (free tier available)
   - Create a new application
   - You'll receive a **Publisher ID**

3. **API Key Details**
   - Indeed provides a free API for job searches
   - Rate limits: 600 requests per IP per 24 hours
   - No authentication token needed, just Publisher ID

4. **Add to .env**
   ```
   INDEED_PUBLISHER_ID=your_publisher_id_here
   INDEED_API_KEY=your_api_key_here
   ```

5. **Example Indeed API Request**
   ```
   GET https://api.indeed.com/ads/apisearch?publisher={ID}&q=python&l=USA&format=json
   ```

**Pros:**
- ✅ Official API with good documentation
- ✅ Free tier available
- ✅ 600 requests per day
- ✅ Returns structured JSON data
- ✅ Reliable and maintained

---

## 📌 LinkedIn Jobs API

### Option 1: LinkedIn Official API (Recommended)

1. **Go to LinkedIn Developers**
   - Visit: https://www.linkedin.com/developers/apps

2. **Create New App**
   - Click "Create app"
   - Fill in company name (your company or "Personal")
   - Select "Search jobs on LinkedIn"
   - Accept terms and create

3. **Get Credentials**
   - Navigate to "Auth" tab
   - Copy your **Client ID** and **Client Secret**
   - These are your API credentials

4. **Add to .env**
   ```
   LINKEDIN_API_KEY=your_client_id_here
   ```

5. **Authentication**
   - LinkedIn requires OAuth 2.0
   - The system will guide you through login on first use

**Pros:**
- ✅ Official API
- ✅ Most accurate data
- ✅ Real-time job listings
- ✅ Company information included

**Cons:**
- ⚠️ Rate limited (300 requests per minute for some endpoints)
- ⚠️ Requires OAuth authentication

### Option 2: LinkedIn Jobs Crawler Library

If you prefer not to use the official API:

1. **Install LinkedIn Jobs Crawler**
   ```bash
   pip install linkedin-jobs-crawler
   ```

2. **Add to .env**
   ```
   LINKEDIN_API_KEY=true  # Enable the library version
   ```

3. **This uses web scraping (headless browser)**
   - No API key needed
   - Slower than official API
   - May be blocked by LinkedIn

---

## 📌 Other Job Board APIs

### Stack Overflow Jobs API
- **Endpoint**: https://stackoverflow.com/jobs/api/
- **Auth**: None required
- **Rate limit**: ~100 requests per minute

### GitHub Jobs API
- **Endpoint**: https://jobs.github.com/positions.json
- **Auth**: None required
- **Rate limit**: Very generous

### Glassdoor
- **API**: Not officially available
- **Workaround**: Web scraping only

### Upwork
- **API**: Available for freelancers
- **URL**: https://www.upwork.com/developers/

---

## 🔧 Testing Your API Keys

### Test Indeed API
```bash
python3 << 'EOF'
import requests

PUBLISHER_ID = "your_publisher_id"
INDEED_API_KEY = "your_api_key"

url = "https://api.indeed.com/ads/apisearch"
params = {
    'publisher': PUBLISHER_ID,
    'q': 'python internship',
    'l': 'USA',
    'format': 'json',
    'limit': '10'
}

response = requests.get(url, params=params)
print(f"Status: {response.status_code}")
print(f"Jobs found: {len(response.json().get('results', []))}")
EOF
```

### Test LinkedIn API
```bash
python3 << 'EOF'
from linkedin import linkedin

# OAuth authentication
authentication = linkedin.LinkedInAuthentication(
    'your_client_id',
    'your_client_secret',
    'http://localhost:8000',
    linkedin.PERMISSIONS.enums.PermissionEnum.R_JOBS
)

application = linkedin.LinkedInApplication(authentication)
jobs = application.search_job(selectors=['id', 'posting-date'])
print(f"Jobs found: {len(jobs)}")
EOF
```

---

## 🔐 Security Notes

1. **Never hardcode API keys** in your code
2. **Use .env file** (already in .gitignore)
3. **Rotate API keys** periodically
4. **Use environment variables** for production
5. **Restrict API key permissions** to job search only

### Production Setup
```bash
# macOS/Linux
export INDEED_PUBLISHER_ID="your_key"
export LINKEDIN_API_KEY="your_key"

# Then run
python main.py
```

---

## 📊 Comparison of Job Sources

| Source | Type | Free API | Rate Limit | Data Quality |
|--------|------|----------|-----------|--------------|
| Indeed | API | ✅ Yes | 600/day | ⭐⭐⭐⭐⭐ |
| LinkedIn | API | ✅ Yes | 300/min | ⭐⭐⭐⭐⭐ |
| GitHub Jobs | API | ✅ Yes | Generous | ⭐⭐⭐⭐ |
| Stack Overflow | API | ✅ Yes | 100/min | ⭐⭐⭐⭐ |
| Glassdoor | Scraping | ❌ No | Limited | ⭐⭐⭐ |

---

## 🚀 Next Steps

1. **Get your API keys** using the guides above
2. **Add them to .env file**
3. **Run the system**:
   ```bash
   python main.py
   ```
4. **Monitor the output** to see which sources are being searched

---

## 🆘 Troubleshooting

### "API key not valid"
- Check spelling of API key
- Verify key hasn't expired
- Regenerate key if necessary
- Ensure you have the correct Publisher ID (not API key)

### "Rate limit exceeded"
- Indeed: 600 requests per 24 hours
- LinkedIn: 300 requests per minute
- Consider adjusting CHECK_INTERVAL in config.py

### "Connection refused"
- Check internet connection
- Verify API endpoint URL is correct
- Check if job board has blocked the IP

### No jobs found
- Verify keywords are relevant
- Check API response in logs
- Try simpler keywords
- Ensure date filters aren't too restrictive

---

## 📚 Resources

- **Indeed API Docs**: https://opensource.indeedeng.io/api-documentation/
- **LinkedIn API Docs**: https://docs.microsoft.com/en-us/linkedin/
- **GitHub Jobs Docs**: https://jobs.github.com/api
- **Stack Overflow API**: https://stackoverflow.com/jobs/api

---

Made with ❤️ for Computer Science students

For questions, check the README.md or GETTING_STARTED.md
