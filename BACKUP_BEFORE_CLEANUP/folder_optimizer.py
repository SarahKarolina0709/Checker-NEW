# -*- coding: utf-8 -*-
"""
Folder Optimizer - Enhanced customer folder management and anonymization
"""

import os
import shutil
import json
import hashlib
from datetime import datetime
from pathlib import Path
import threading
import queue

class FolderOptimizer:
    def __init__(self):
        self.base_dir = "Checker_Projekte"
        self.cache_file = "folder_cache.json"
        self.folder_cache = self._load_cache()
        
    def _load_cache(self):
        """Load folder structure cache for faster access"""
        try:
            cache_path = os.path.join(self.base_dir, self.cache_file)
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        return {}
    
    def _save_cache(self):
        """Save folder structure cache"""
        try:
            cache_path = os.path.join(self.base_dir, self.cache_file)
            os.makedirs(self.base_dir, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.folder_cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def get_optimized_customer_folder(self, customer_name, order_number):
        """Get or create optimized customer folder structure"""
        # Create cache key
        cache_key = f"{customer_name}_{order_number}"
        
        if cache_key in self.folder_cache:
            folder_path = self.folder_cache[cache_key]["path"]
            if os.path.exists(folder_path):
                return folder_path
        
        # Create new folder structure
        sanitized_name = self._sanitize_foldername(customer_name)
        sanitized_order = self._sanitize_foldername(order_number)
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        folder_name = f"{sanitized_name}_{sanitized_order}_{date_str}"
        folder_path = os.path.join(self.base_dir, folder_name)
        
        # Create folder structure
        subfolders = [
            "quellen", "uebersetzungen", "pruefung", 
            "finalisierung", "korrespondenz", "backup"
        ]
        
        for subfolder in subfolders:
            os.makedirs(os.path.join(folder_path, subfolder), exist_ok=True)
        
        # Update cache
        self.folder_cache[cache_key] = {
            "path": folder_path,
            "created": datetime.now().isoformat(),
            "customer": customer_name,
            "order": order_number
        }
        self._save_cache()
        
        return folder_path
    
    def create_anonymized_copy(self, source_file, customer_name, target_folder):
        """Create anonymized copy for translator"""
        try:
            # Generate anonymous filename
            hash_obj = hashlib.md5(f"{customer_name}_{os.path.basename(source_file)}".encode())
            anonymous_name = f"doc_{hash_obj.hexdigest()[:8]}{os.path.splitext(source_file)[1]}"
            
            target_path = os.path.join(target_folder, anonymous_name)
            
            # Copy file
            shutil.copy2(source_file, target_path)
            
            # Create mapping file for de-anonymization
            mapping_file = os.path.join(target_folder, "anonymization_mapping.json")
            mapping = {}
            
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    mapping = json.load(f)
            
            mapping[anonymous_name] = {
                "original_name": os.path.basename(source_file),
                "customer": "[ANONYMISIERT]",
                "created": datetime.now().isoformat()
            }
            
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(mapping, f, ensure_ascii=False, indent=2)
            
            return target_path
            
        except Exception as e:
            print(f"Anonymization error: {e}")
            return None
    
    def batch_file_operations(self, operations):
        """Perform batch file operations with progress tracking"""
        results = []
        operation_queue = queue.Queue()
        
        # Add operations to queue
        for op in operations:
            operation_queue.put(op)
        
        def worker():
            while not operation_queue.empty():
                try:
                    operation = operation_queue.get()
                    op_type = operation.get("type")
                    
                    if op_type == "copy":
                        shutil.copy2(operation["source"], operation["target"])
                        results.append({"status": "success", "operation": operation})
                    elif op_type == "move":
                        shutil.move(operation["source"], operation["target"])
                        results.append({"status": "success", "operation": operation})
                    elif op_type == "anonymize":
                        result = self.create_anonymized_copy(
                            operation["source"], 
                            operation["customer"], 
                            operation["target_folder"]
                        )
                        results.append({"status": "success" if result else "error", "operation": operation})
                    
                    operation_queue.task_done()
                    
                except Exception as e:
                    results.append({"status": "error", "operation": operation, "error": str(e)})
                    operation_queue.task_done()
        
        # Use multiple threads for batch operations
        threads = []
        for i in range(min(3, len(operations))):  # Max 3 threads
            thread = threading.Thread(target=worker)
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        operation_queue.join()
        
        return results
    
    def _sanitize_foldername(self, name):
        """Sanitize folder name"""
        import re
        # Remove invalid characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
        # Remove multiple underscores
        sanitized = re.sub(r'_+', '_', sanitized)
        # Trim and limit length
        return sanitized.strip('_')[:50]
    
    def cleanup_old_projects(self, days_old=90):
        """Clean up projects older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
        cleaned_folders = []
        
        try:
            for folder_name in os.listdir(self.base_dir):
                folder_path = os.path.join(self.base_dir, folder_name)
                if os.path.isdir(folder_path):
                    # Check modification time
                    mod_time = os.path.getmtime(folder_path)
                    if mod_time < cutoff_date:
                        # Move to archive instead of delete
                        archive_path = os.path.join(self.base_dir, "archive", folder_name)
                        os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                        shutil.move(folder_path, archive_path)
                        cleaned_folders.append(folder_name)
        
        except Exception as e:
            print(f"Cleanup error: {e}")
        
        return cleaned_folders

# Global instance
folder_optimizer = FolderOptimizer()
