"""
Database management module for tracking sent jobs
"""
import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class JobDatabase:
    def __init__(self, db_path: str = "data/jobs_database.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database"""
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT UNIQUE,
                title TEXT,
                company TEXT,
                location TEXT,
                job_url TEXT,
                description TEXT,
                source TEXT,
                posted_date TEXT,
                found_date TEXT,
                sent_date TEXT,
                notification_type TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        
        # Create notifications table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id TEXT,
                notification_method TEXT,
                sent_date TEXT,
                status TEXT,
                FOREIGN KEY (job_id) REFERENCES jobs (job_id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_job(self, job_data: Dict) -> bool:
        """Add a new job to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO jobs 
                (job_id, title, company, location, job_url, description, 
                 source, posted_date, found_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                job_data.get('job_id'),
                job_data.get('title'),
                job_data.get('company'),
                job_data.get('location'),
                job_data.get('job_url'),
                job_data.get('description', ''),
                job_data.get('source'),
                job_data.get('posted_date'),
                datetime.now().isoformat(),
                'pending'
            ))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False  # Job already exists
        except Exception as e:
            print(f"Error adding job: {e}")
            return False
    
    def job_exists(self, job_id: str) -> bool:
        """Check if job already exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM jobs WHERE job_id = ?", (job_id,))
        result = cursor.fetchone() is not None
        conn.close()
        
        return result
    
    def mark_job_sent(self, job_id: str, method: str) -> bool:
        """Mark job as sent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE jobs 
                SET sent_date = ?, status = 'sent'
                WHERE job_id = ?
            """, (datetime.now().isoformat(), job_id))
            
            cursor.execute("""
                INSERT INTO notifications 
                (job_id, notification_method, sent_date, status)
                VALUES (?, ?, ?, ?)
            """, (job_id, method, datetime.now().isoformat(), 'sent'))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error marking job as sent: {e}")
            return False
    
    def get_pending_jobs(self) -> List[Dict]:
        """Get all pending jobs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT job_id, title, company, location, job_url, source
            FROM jobs
            WHERE status = 'pending'
        """)
        
        jobs = []
        for row in cursor.fetchall():
            jobs.append({
                'job_id': row[0],
                'title': row[1],
                'company': row[2],
                'location': row[3],
                'job_url': row[4],
                'source': row[5]
            })
        
        conn.close()
        return jobs
    
    def get_job_count(self) -> Dict[str, int]:
        """Get count of jobs by status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT status, COUNT(*) FROM jobs GROUP BY status")
        results = cursor.fetchall()
        conn.close()
        
        counts = {}
        for status, count in results:
            counts[status] = count
        
        return counts
