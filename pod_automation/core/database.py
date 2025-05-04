"""
Database layer for POD Automation System.
Provides a unified interface for data storage and retrieval.
"""

import os
import json
import sqlite3
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from datetime import datetime

# Import utilities
from pod_automation.utils.logging_config import get_logger

# Initialize logger
logger = get_logger(__name__)

class Database:
    """Database layer for POD Automation System."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection.
        
        Args:
            db_path: Path to SQLite database file (optional)
        """
        self.db_path = db_path or os.path.join(
            os.path.expanduser("~"), ".pod_automation", "pod_automation.db"
        )
        self.db_dir = os.path.dirname(self.db_path)
        
        # Create database directory if it doesn't exist
        os.makedirs(self.db_dir, exist_ok=True)
        
        # Initialize database
        self.conn = None
        self.cursor = None
        self.connect()
        self.initialize_tables()
    
    def connect(self) -> bool:
        """Connect to the database.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
            self.cursor = self.conn.cursor()
            logger.info(f"Connected to database at {self.db_path}")
            return True
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from the database.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self.conn:
                self.conn.close()
                self.conn = None
                self.cursor = None
                logger.info("Disconnected from database")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}")
            return False
    
    def initialize_tables(self) -> bool:
        """Initialize database tables.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Create designs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS designs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    path TEXT NOT NULL,
                    keyword TEXT,
                    prompt TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Create mockups table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mockups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    design_id INTEGER,
                    product_type TEXT NOT NULL,
                    path TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (design_id) REFERENCES designs (id)
                )
            ''')
            
            # Create products table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    design_id INTEGER,
                    title TEXT NOT NULL,
                    description TEXT,
                    product_type TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    platform_id TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (design_id) REFERENCES designs (id)
                )
            ''')
            
            # Create tags table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_id INTEGER,
                    tag TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')
            
            # Create trends table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    keyword TEXT NOT NULL,
                    score REAL,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Create workflows table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    metadata TEXT
                )
            ''')
            
            # Create workflow_steps table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    FOREIGN KEY (workflow_id) REFERENCES workflows (id)
                )
            ''')
            
            self.conn.commit()
            logger.info("Database tables initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing database tables: {str(e)}")
            return False
    
    def create(self, table: str, data: Dict[str, Any]) -> int:
        """Create a new record.
        
        Args:
            table: Table name
            data: Record data
            
        Returns:
            int: ID of the created record, or -1 if creation failed
        """
        try:
            # Convert any non-string values to JSON
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = json.dumps(value)
            
            # Build SQL query
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['?' for _ in data.keys()])
            query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
            
            # Execute query
            self.cursor.execute(query, list(data.values()))
            self.conn.commit()
            
            # Get ID of the created record
            record_id = self.cursor.lastrowid
            logger.info(f"Created record in {table} with ID {record_id}")
            
            return record_id
        except Exception as e:
            logger.error(f"Error creating record in {table}: {str(e)}")
            return -1
    
    def read(self, table: str, record_id: int) -> Optional[Dict[str, Any]]:
        """Read a record by ID.
        
        Args:
            table: Table name
            record_id: Record ID
            
        Returns:
            Dict containing record data, or None if not found
        """
        try:
            # Execute query
            self.cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (record_id,))
            
            # Get result
            result = self.cursor.fetchone()
            
            if result:
                # Convert to dictionary
                record = dict(result)
                
                # Parse JSON fields
                for key, value in record.items():
                    if key == 'metadata' and value:
                        try:
                            record[key] = json.loads(value)
                        except:
                            pass
                
                logger.info(f"Read record from {table} with ID {record_id}")
                return record
            else:
                logger.warning(f"Record not found in {table} with ID {record_id}")
                return None
        except Exception as e:
            logger.error(f"Error reading record from {table}: {str(e)}")
            return None
    
    def update(self, table: str, record_id: int, data: Dict[str, Any]) -> bool:
        """Update a record by ID.
        
        Args:
            table: Table name
            record_id: Record ID
            data: Updated record data
            
        Returns:
            bool: True if update successful, False otherwise
        """
        try:
            # Convert any non-string values to JSON
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    data[key] = json.dumps(value)
            
            # Build SQL query
            set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
            query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
            
            # Execute query
            self.cursor.execute(query, list(data.values()) + [record_id])
            self.conn.commit()
            
            # Check if record was updated
            if self.cursor.rowcount > 0:
                logger.info(f"Updated record in {table} with ID {record_id}")
                return True
            else:
                logger.warning(f"Record not found in {table} with ID {record_id}")
                return False
        except Exception as e:
            logger.error(f"Error updating record in {table}: {str(e)}")
            return False
    
    def delete(self, table: str, record_id: int) -> bool:
        """Delete a record by ID.
        
        Args:
            table: Table name
            record_id: Record ID
            
        Returns:
            bool: True if deletion successful, False otherwise
        """
        try:
            # Execute query
            self.cursor.execute(f"DELETE FROM {table} WHERE id = ?", (record_id,))
            self.conn.commit()
            
            # Check if record was deleted
            if self.cursor.rowcount > 0:
                logger.info(f"Deleted record from {table} with ID {record_id}")
                return True
            else:
                logger.warning(f"Record not found in {table} with ID {record_id}")
                return False
        except Exception as e:
            logger.error(f"Error deleting record from {table}: {str(e)}")
            return False
    
    def query(self, query: str, params: Tuple = ()) -> List[Dict[str, Any]]:
        """Execute a custom SQL query.
        
        Args:
            query: SQL query
            params: Query parameters
            
        Returns:
            List of records matching the query
        """
        try:
            # Execute query
            self.cursor.execute(query, params)
            
            # Get results
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            records = [dict(row) for row in results]
            
            # Parse JSON fields
            for record in records:
                for key, value in record.items():
                    if key == 'metadata' and value:
                        try:
                            record[key] = json.loads(value)
                        except:
                            pass
            
            logger.info(f"Executed query: {query}")
            return records
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return []
    
    def find(self, table: str, conditions: Dict[str, Any], limit: int = 100) -> List[Dict[str, Any]]:
        """Find records matching conditions.
        
        Args:
            table: Table name
            conditions: Search conditions
            limit: Maximum number of records to return
            
        Returns:
            List of records matching the conditions
        """
        try:
            # Build SQL query
            where_clause = ' AND '.join([f"{key} = ?" for key in conditions.keys()])
            query = f"SELECT * FROM {table}"
            
            if where_clause:
                query += f" WHERE {where_clause}"
            
            query += f" LIMIT {limit}"
            
            # Execute query
            self.cursor.execute(query, list(conditions.values()))
            
            # Get results
            results = self.cursor.fetchall()
            
            # Convert to list of dictionaries
            records = [dict(row) for row in results]
            
            # Parse JSON fields
            for record in records:
                for key, value in record.items():
                    if key == 'metadata' and value:
                        try:
                            record[key] = json.loads(value)
                        except:
                            pass
            
            logger.info(f"Found {len(records)} records in {table} matching conditions")
            return records
        except Exception as e:
            logger.error(f"Error finding records in {table}: {str(e)}")
            return []
    
    def count(self, table: str, conditions: Dict[str, Any] = None) -> int:
        """Count records matching conditions.
        
        Args:
            table: Table name
            conditions: Search conditions (optional)
            
        Returns:
            int: Number of records matching the conditions
        """
        try:
            # Build SQL query
            query = f"SELECT COUNT(*) FROM {table}"
            
            if conditions:
                where_clause = ' AND '.join([f"{key} = ?" for key in conditions.keys()])
                query += f" WHERE {where_clause}"
                
                # Execute query
                self.cursor.execute(query, list(conditions.values()))
            else:
                # Execute query
                self.cursor.execute(query)
            
            # Get result
            result = self.cursor.fetchone()
            
            if result:
                count = result[0]
                logger.info(f"Counted {count} records in {table}")
                return count
            else:
                logger.warning(f"Error counting records in {table}")
                return 0
        except Exception as e:
            logger.error(f"Error counting records in {table}: {str(e)}")
            return 0

# Global database instance
_db_instance = None

def get_database(db_path: Optional[str] = None) -> Database:
    """Get global database instance.
    
    Args:
        db_path: Path to SQLite database file (optional)
        
    Returns:
        Database instance
    """
    global _db_instance
    
    if _db_instance is None or db_path is not None:
        _db_instance = Database(db_path)
    
    return _db_instance