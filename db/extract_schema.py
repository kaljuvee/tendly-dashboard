#!/usr/bin/env python3
"""
Script to extract PostgreSQL database schema and save it as JSON.
"""

import psycopg2
import json
import sys
from typing import Dict, List, Any

def get_database_schema(connection_string: str) -> Dict[str, Any]:
    """
    Extract complete database schema from PostgreSQL database.
    
    Args:
        connection_string: PostgreSQL connection string
        
    Returns:
        Dictionary containing the database schema
    """
    try:
        # Connect to the database
        conn = psycopg2.connect(connection_string)
        cursor = conn.cursor()
        
        schema = {
            "tables": {},
            "views": {},
            "indexes": {},
            "constraints": {}
        }
        
        # Get all tables
        cursor.execute("""
            SELECT table_name, table_type 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables_info = cursor.fetchall()
        
        for table_name, table_type in tables_info:
            if table_type == 'BASE TABLE':
                schema["tables"][table_name] = get_table_schema(cursor, table_name)
            elif table_type == 'VIEW':
                schema["views"][table_name] = get_view_schema(cursor, table_name)
        
        # Get indexes
        cursor.execute("""
            SELECT 
                i.relname as index_name,
                t.relname as table_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary
            FROM 
                pg_class t,
                pg_class i,
                pg_index ix,
                pg_attribute a
            WHERE 
                t.oid = ix.indrelid
                AND i.oid = ix.indexrelid
                AND a.attrelid = t.oid
                AND a.attnum = ANY(ix.indkey)
                AND t.relkind = 'r'
                AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = 'public')
            ORDER BY t.relname, i.relname;
        """)
        
        indexes = cursor.fetchall()
        for index_name, table_name, column_name, is_unique, is_primary in indexes:
            if table_name not in schema["indexes"]:
                schema["indexes"][table_name] = []
            schema["indexes"][table_name].append({
                "index_name": index_name,
                "column_name": column_name,
                "is_unique": is_unique,
                "is_primary": is_primary
            })
        
        cursor.close()
        conn.close()
        
        return schema
        
    except Exception as e:
        print(f"Error extracting schema: {e}")
        return {}

def get_table_schema(cursor, table_name: str) -> Dict[str, Any]:
    """Get detailed schema for a specific table."""
    
    # Get columns information
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale
        FROM information_schema.columns 
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, (table_name,))
    
    columns = []
    for row in cursor.fetchall():
        column_info = {
            "name": row[0],
            "data_type": row[1],
            "is_nullable": row[2] == 'YES',
            "default": row[3],
            "max_length": row[4],
            "precision": row[5],
            "scale": row[6]
        }
        columns.append(column_info)
    
    # Get row count
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
        row_count = cursor.fetchone()[0]
    except:
        row_count = 0
    
    # Get sample data (first 5 rows)
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT 5;")
        sample_data = cursor.fetchall()
        # Convert to list of dictionaries
        sample_rows = []
        for row in sample_data:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col["name"]] = str(row[i]) if row[i] is not None else None
            sample_rows.append(row_dict)
    except:
        sample_rows = []
    
    return {
        "columns": columns,
        "row_count": row_count,
        "sample_data": sample_rows
    }

def get_view_schema(cursor, view_name: str) -> Dict[str, Any]:
    """Get schema for a view."""
    cursor.execute("""
        SELECT 
            column_name,
            data_type,
            is_nullable
        FROM information_schema.columns 
        WHERE table_name = %s AND table_schema = 'public'
        ORDER BY ordinal_position;
    """, (view_name,))
    
    columns = []
    for row in cursor.fetchall():
        column_info = {
            "name": row[0],
            "data_type": row[1],
            "is_nullable": row[2] == 'YES'
        }
        columns.append(column_info)
    
    return {
        "columns": columns,
        "type": "view"
    }

def main():
    # Database connection string
    db_url = "postgresql://tendlydev_user:ugXs4YbGLX7iTdQkAV5LpHtEnPephO9U@dpg-d30k5s8gjchc73eupg30-a.frankfurt-postgres.render.com/tendlydev"
    
    print("Extracting database schema...")
    schema = get_database_schema(db_url)
    
    if schema:
        # Save schema to JSON file
        output_file = "/home/ubuntu/tendly-dashboard/db/schema.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False, default=str)
        
        print(f"Schema extracted successfully and saved to {output_file}")
        
        # Print summary
        print(f"\nSchema Summary:")
        print(f"- Tables: {len(schema.get('tables', {}))}")
        print(f"- Views: {len(schema.get('views', {}))}")
        
        if 'tables' in schema:
            print(f"\nTables found:")
            for table_name, table_info in schema['tables'].items():
                row_count = table_info.get('row_count', 0)
                col_count = len(table_info.get('columns', []))
                print(f"  - {table_name}: {col_count} columns, {row_count} rows")
    else:
        print("Failed to extract schema")
        sys.exit(1)

if __name__ == "__main__":
    main()
