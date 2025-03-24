import os
import json
from datetime import datetime
import subprocess
from typing import Dict, Any, List, Tuple
import numpy as np
from etl.util import get_connection, safe_convert
from etl.load import COLUMNS
from index.index import get_total_count, fetch_embeddings_in_batches

def get_git_commit() -> str:
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, 
                              text=True)
        return result.stdout.strip()
    except:
        return "unknown"

def check_table_structure(conn) -> Dict[str, Any]:
    """Validates the table structure matches the expected schema"""
    with conn.cursor() as cur:
        # Check if table exists
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'papers'
            );
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            return {"valid": False, "error": "papers table does not exist"}
            
        # Check if all expected columns exist
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'papers'
        """)
        existing_columns = {row[0]: row[1] for row in cur.fetchall()}
        
        expected_columns = {col["name"]: col["definition"].split()[0] for col in COLUMNS}
        missing_columns = set(expected_columns.keys()) - set(existing_columns.keys())
        
        if missing_columns:
            return {"valid": False, "error": f"Missing columns: {missing_columns}"}
            
        return {"valid": True}

def check_data_quality(conn) -> Dict[str, Any]:
    """Validates data quality metrics for key fields"""
    with conn.cursor() as cur:
        checks = {}
        
        # Check for NULL values in required fields
        required_fields = ["doi", "title", "abstract"]
        for field in required_fields:
            cur.execute(f"SELECT COUNT(*) FROM papers WHERE {field} IS NULL")
            null_count = cur.fetchone()[0]
            checks[f"{field}_null_count"] = null_count
            
        # Check for empty strings in required fields
        for field in required_fields:
            cur.execute(f"SELECT COUNT(*) FROM papers WHERE {field} = ''")
            empty_count = cur.fetchone()[0]
            checks[f"{field}_empty_count"] = empty_count
            
        # Check date ranges
        cur.execute("""
            SELECT 
                MIN(published_date),
                MAX(published_date),
                COUNT(*) FILTER (WHERE published_date IS NULL)
            FROM papers
        """)
        min_date, max_date, null_dates = cur.fetchone()
        checks["date_range"] = {
            "min": min_date.isoformat() if min_date else None,
            "max": max_date.isoformat() if max_date else None,
            "null_count": null_dates
        }
        
        # Check vector embeddings
        cur.execute("""
            SELECT COUNT(*) 
            FROM papers 
            WHERE embedding IS NULL
        """)
        null_embeddings = cur.fetchone()[0]
        checks["null_embeddings"] = null_embeddings
        
        # Check vector dimensions
        cur.execute("""
            SELECT COUNT(*) 
            FROM papers 
            WHERE embedding IS NOT NULL 
            AND array_length(embedding, 1) != 384
        """)
        invalid_dimensions = cur.fetchone()[0]
        checks["invalid_dimensions"] = invalid_dimensions
        
        return checks

def validate_embeddings(conn) -> Dict[str, Any]:
    """Validates vector embeddings quality"""
    results = {"valid": True, "issues": []}
    
    # Check first batch of embeddings
    for batch in fetch_embeddings_in_batches(batch_size=100):
        if not batch:
            break
            
        embeddings = []
        for _, embedding in batch:
            if isinstance(embedding, str):
                embedding = json.loads(embedding)
            embeddings.append(embedding)
            
        embeddings = np.array(embeddings, dtype=np.float32)
        
        # Check for NaN values
        if np.any(np.isnan(embeddings)):
            results["valid"] = False
            results["issues"].append("Found NaN values in embeddings")
            
        # Check for infinite values
        if np.any(np.isinf(embeddings)):
            results["valid"] = False
            results["issues"].append("Found infinite values in embeddings")
            
        # Check vector norms
        norms = np.linalg.norm(embeddings, axis=1)
        if not np.allclose(norms, 1.0, rtol=1e-5, atol=1e-5):
            results["valid"] = False
            results["issues"].append("Some embeddings are not normalized")
            
        break  # Only check first batch for performance
        
    return results

def validate_database(conn) -> Dict[str, Any]:
    """Main validation function that runs all checks"""
    validation_result = {
        "timestamp": datetime.utcnow().isoformat(),
        "rows_loaded": get_total_count(),
        "etl_commit": get_git_commit(),
        "validation": {},
        "notes": []
    }
    
    # Check table structure
    structure_check = check_table_structure(conn)
    validation_result["validation"]["table_structure"] = structure_check
    if not structure_check["valid"]:
        validation_result["notes"].append(structure_check["error"])
    
    # Check data quality
    quality_checks = check_data_quality(conn)
    validation_result["validation"]["data_quality"] = quality_checks
    
    # Check embeddings
    embedding_check = validate_embeddings(conn)
    validation_result["validation"]["embeddings"] = embedding_check
    if not embedding_check["valid"]:
        validation_result["notes"].extend(embedding_check["issues"])
    
    # Add quality check notes
    for field in ["doi", "title", "abstract"]:
        if quality_checks[f"{field}_null_count"] > 0:
            validation_result["notes"].append(f"Found {quality_checks[f'{field}_null_count']} NULL values in {field}")
        if quality_checks[f"{field}_empty_count"] > 0:
            validation_result["notes"].append(f"Found {quality_checks[f'{field}_empty_count']} empty strings in {field}")
    
    if quality_checks["null_embeddings"] > 0:
        validation_result["notes"].append(f"Found {quality_checks['null_embeddings']} NULL embeddings")
    if quality_checks["invalid_dimensions"] > 0:
        validation_result["notes"].append(f"Found {quality_checks['invalid_dimensions']} embeddings with invalid dimensions")
    
    # Overall validation status
    validation_result["validation"]["overall_valid"] = (
        structure_check["valid"] and
        embedding_check["valid"] and
        quality_checks["null_embeddings"] == 0 and
        quality_checks["invalid_dimensions"] == 0
    )
    
    return validation_result

def main():
    try:
        conn = get_connection()
        validation_result = validate_database(conn)
        
        # Write validation results to file
        with open("etl/last_run.json", "w") as f:
            json.dump(validation_result, f, indent=2)
            
        # Exit with error if validation failed
        if not validation_result["validation"]["overall_valid"]:
            print("Validation failed:", validation_result["notes"])
            exit(1)
            
        print("Validation successful:", validation_result)
        
    except Exception as e:
        print(f"Error during validation: {str(e)}")
        exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main() 