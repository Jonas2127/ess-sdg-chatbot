"""
Engine B: Excel to SQL Processor
=================================
Converts 17 UN SDG Excel files into a unified SQLite database

Features:
- Loads all 17 SDG Goal Excel files
- Normalizes and cleans data
- Creates relational SQL schema
- Enables precise SQL queries
"""

import pandas as pd
import sqlite3
from pathlib import Path
from typing import List, Dict
from tqdm import tqdm
import re

class ExcelProcessor:
    """Process UN SDG Excel files into SQL database"""
    
    def __init__(self, db_path: str = "data/sql_database/sdg_ethiopia.db"):
        """
        Initialize Excel processor
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = None
        
        # SDG Goal descriptions
        self.sdg_goals = {
            1: "No Poverty",
            2: "Zero Hunger",
            3: "Good Health and Well-being",
            4: "Quality Education",
            5: "Gender Equality",
            6: "Clean Water and Sanitation",
            7: "Affordable and Clean Energy",
            8: "Decent Work and Economic Growth",
            9: "Industry, Innovation and Infrastructure",
            10: "Reduced Inequalities",
            11: "Sustainable Cities and Communities",
            12: "Responsible Consumption and Production",
            13: "Climate Action",
            14: "Life Below Water",
            15: "Life on Land",
            16: "Peace, Justice and Strong Institutions",
            17: "Partnerships for the Goals"
        }
    
    def connect_db(self):
        """Create connection to SQLite database"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        print(f"✅ Connected to database: {self.db_path}")
    
    def close_db(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✅ Database connection closed")
    
    def load_excel_file(self, file_path: str, goal_number: int) -> pd.DataFrame:
        """
        Load a single Excel file
        
        Args:
            file_path: Path to Excel file
            goal_number: SDG Goal number (1-17)
            
        Returns:
            DataFrame with SDG data
        """
        try:
            df = pd.read_excel(file_path)
            
            # Add metadata columns
            df['goal_number'] = goal_number
            df['goal_name'] = self.sdg_goals[goal_number]
            df['source_file'] = Path(file_path).name
            
            return df
        except Exception as e:
            print(f"⚠️  Error loading {file_path}: {str(e)}")
            return pd.DataFrame()
    
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names
        
        Converts various naming conventions to standard format
        """
        # Create column name mapping
        column_mapping = {}
        
        for col in df.columns:
            # Convert to lowercase and replace spaces/special chars with underscore
            normalized = col.lower().strip()
            normalized = re.sub(r'[^\w\s]', '', normalized)
            normalized = re.sub(r'\s+', '_', normalized)
            column_mapping[col] = normalized
        
        df = df.rename(columns=column_mapping)
        
        return df
    
    def process_all_excel_files(self, folder_path: str) -> pd.DataFrame:
        """
        Process all 17 UN SDG Excel files
        
        Args:
            folder_path: Path to folder containing Goal1.xlsx through Goal17.xlsx
            
        Returns:
            Combined DataFrame with all SDG data
        """
        excel_files = sorted(Path(folder_path).glob("Goal*.xlsx"))
        
        if not excel_files:
            print(f"⚠️  No Excel files found in {folder_path}")
            return pd.DataFrame()
        
        print(f"\n📊 Processing {len(excel_files)} UN SDG Excel files...")
        
        all_data = []
        
        for file_path in tqdm(excel_files, desc="Loading Excel files"):
            # Extract goal number from filename (Goal1.xlsx -> 1)
            filename = file_path.stem  # Gets 'Goal1' from 'Goal1.xlsx'
            goal_number = int(re.search(r'\d+', filename).group())
            
            # Load Excel file
            df = self.load_excel_file(str(file_path), goal_number)
            
            if not df.empty:
                # Normalize column names
                df = self.normalize_columns(df)
                all_data.append(df)
        
        if not all_data:
            print("⚠️  No data loaded from Excel files")
            return pd.DataFrame()
        
        # Combine all data
        combined_df = pd.concat(all_data, ignore_index=True)
        
        print(f"✅ Loaded {len(combined_df)} rows from {len(excel_files)} files")
        
        return combined_df
    
    def create_tables(self, df: pd.DataFrame):
        """
        Create SQL tables from DataFrame
        
        Args:
            df: Combined SDG data
        """
        if df.empty:
            print("⚠️  No data to create tables")
            return
        
        print("\n🔨 Creating SQL tables...")
        
        # Main SDG data table
        df.to_sql('sdg_indicators', self.conn, if_exists='replace', index=False)
        print(f"✅ Created table: sdg_indicators ({len(df)} rows)")
        
        # Create SDG goals reference table
        goals_df = pd.DataFrame([
            {'goal_number': num, 'goal_name': name}
            for num, name in self.sdg_goals.items()
        ])
        goals_df.to_sql('sdg_goals', self.conn, if_exists='replace', index=False)
        print(f"✅ Created table: sdg_goals (17 rows)")
        
        # Create indexes for faster queries
        cursor = self.conn.cursor()
        
        try:
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_goal_number ON sdg_indicators(goal_number)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_year ON sdg_indicators(year)") if 'year' in df.columns else None
            self.conn.commit()
            print("✅ Created indexes")
        except Exception as e:
            print(f"⚠️  Index creation: {str(e)}")
        
    def get_table_info(self) -> Dict:
        """Get information about database tables"""
        cursor = self.conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        info = {}
        
        for (table_name,) in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            info[table_name] = {
                'row_count': count,
                'columns': columns
            }
        
        return info
    
    def execute_query(self, query: str) -> pd.DataFrame:
        """
        Execute SQL query and return results
        
        Args:
            query: SQL query string
            
        Returns:
            DataFrame with query results
        """
        try:
            df = pd.read_sql_query(query, self.conn)
            return df
        except Exception as e:
            print(f"⚠️  Query error: {str(e)}")
            return pd.DataFrame()


def main():
    """Test Excel processor"""
    processor = ExcelProcessor()
    processor.connect_db()
    
    # Process all Excel files
    df = processor.process_all_excel_files("data/raw/un_sdg_excel")
    
    # Create tables
    processor.create_tables(df)
    
    # Get info
    info = processor.get_table_info()
    print(f"\n📊 Database Info:")
    for table_name, table_info in info.items():
        print(f"   {table_name}: {table_info['row_count']} rows, {len(table_info['columns'])} columns")
    
    # Test query
    test_query = "SELECT goal_number, goal_name, COUNT(*) as indicator_count FROM sdg_indicators GROUP BY goal_number ORDER BY goal_number"
    results = processor.execute_query(test_query)
    print(f"\n📈 Indicators per Goal:")
    print(results.to_string(index=False))
    
    processor.close_db()


if __name__ == "__main__":
    main()
