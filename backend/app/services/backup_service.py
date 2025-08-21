"""
Backup Service for WordPress Sites
Automated backups to S3-compatible storage (AWS S3, Cloudflare R2, etc.)
"""

import logging
import asyncio
import os
import tarfile
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import boto3
from botocore.exceptions import ClientError
import subprocess
import json
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)

class BackupService:
    """
    Handles automated backups for WordPress sites
    """
    
    def __init__(self):
        # S3 Configuration (supports AWS S3, Cloudflare R2, MinIO, etc.)
        self.s3_endpoint = os.getenv('S3_ENDPOINT', 'https://s3.amazonaws.com')
        self.s3_access_key = os.getenv('S3_ACCESS_KEY', '')
        self.s3_secret_key = os.getenv('S3_SECRET_KEY', '')
        self.s3_bucket = os.getenv('S3_BACKUP_BUCKET', 'kenzysites-backups')
        self.s3_region = os.getenv('S3_REGION', 'us-east-1')
        
        # Backup retention policies
        self.retention_policies = {
            'daily': 30,    # Keep daily backups for 30 days
            'weekly': 8,     # Keep weekly backups for 8 weeks
            'monthly': 12    # Keep monthly backups for 12 months
        }
        
        # Initialize S3 client
        self.s3_client = boto3.client(
            's3',
            endpoint_url=self.s3_endpoint if self.s3_endpoint != 'https://s3.amazonaws.com' else None,
            aws_access_key_id=self.s3_access_key,
            aws_secret_access_key=self.s3_secret_key,
            region_name=self.s3_region
        )
        
        # Ensure bucket exists
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Ensure the backup bucket exists"""
        try:
            self.s3_client.head_bucket(Bucket=self.s3_bucket)
        except ClientError:
            try:
                self.s3_client.create_bucket(
                    Bucket=self.s3_bucket,
                    CreateBucketConfiguration={'LocationConstraint': self.s3_region}
                    if self.s3_region != 'us-east-1' else {}
                )
                logger.info(f"Created S3 bucket: {self.s3_bucket}")
                
                # Set lifecycle policy for automatic deletion
                self._set_lifecycle_policy()
            except Exception as e:
                logger.error(f"Failed to create S3 bucket: {str(e)}")
    
    def _set_lifecycle_policy(self):
        """Set S3 lifecycle policy for automatic backup deletion"""
        lifecycle_policy = {
            'Rules': [
                {
                    'ID': 'DeleteOldDailyBackups',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': 'daily/'},
                    'Expiration': {'Days': self.retention_policies['daily']}
                },
                {
                    'ID': 'DeleteOldWeeklyBackups',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': 'weekly/'},
                    'Expiration': {'Days': self.retention_policies['weekly'] * 7}
                },
                {
                    'ID': 'DeleteOldMonthlyBackups',
                    'Status': 'Enabled',
                    'Filter': {'Prefix': 'monthly/'},
                    'Expiration': {'Days': self.retention_policies['monthly'] * 30}
                }
            ]
        }
        
        try:
            self.s3_client.put_bucket_lifecycle_configuration(
                Bucket=self.s3_bucket,
                LifecycleConfiguration=lifecycle_policy
            )
            logger.info("S3 lifecycle policy configured")
        except Exception as e:
            logger.error(f"Failed to set lifecycle policy: {str(e)}")
    
    async def backup_wordpress_site(
        self,
        client_id: str,
        backup_type: str = 'daily',
        include_uploads: bool = True,
        include_plugins: bool = True,
        include_themes: bool = True
    ) -> Dict[str, Any]:
        """
        Create a backup of a WordPress site
        """
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_id = f"{client_id}_{backup_type}_{timestamp}"
        
        try:
            # Create temporary directory for backup
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Step 1: Export MySQL database
                db_backup_path = await self._backup_mysql(client_id, temp_path)
                
                # Step 2: Backup WordPress files
                files_backup_path = await self._backup_wordpress_files(
                    client_id, 
                    temp_path,
                    include_uploads,
                    include_plugins,
                    include_themes
                )
                
                # Step 3: Create metadata file
                metadata_path = self._create_backup_metadata(
                    client_id,
                    backup_id,
                    temp_path,
                    {
                        'database': db_backup_path.name if db_backup_path else None,
                        'files': files_backup_path.name if files_backup_path else None,
                        'include_uploads': include_uploads,
                        'include_plugins': include_plugins,
                        'include_themes': include_themes
                    }
                )
                
                # Step 4: Create compressed archive
                archive_path = temp_path / f"{backup_id}.tar.gz"
                with tarfile.open(archive_path, 'w:gz') as tar:
                    if db_backup_path:
                        tar.add(db_backup_path, arcname=db_backup_path.name)
                    if files_backup_path:
                        tar.add(files_backup_path, arcname=files_backup_path.name)
                    tar.add(metadata_path, arcname='metadata.json')
                
                # Step 5: Calculate checksum
                checksum = self._calculate_checksum(archive_path)
                
                # Step 6: Upload to S3
                s3_key = f"{backup_type}/{client_id}/{backup_id}.tar.gz"
                upload_result = await self._upload_to_s3(archive_path, s3_key, metadata={
                    'client_id': client_id,
                    'backup_type': backup_type,
                    'timestamp': timestamp,
                    'checksum': checksum
                })
                
                # Step 7: Verify upload
                if upload_result['success']:
                    # Clean up old backups based on retention policy
                    await self._cleanup_old_backups(client_id, backup_type)
                    
                    return {
                        'success': True,
                        'backup_id': backup_id,
                        's3_key': s3_key,
                        'size': archive_path.stat().st_size,
                        'checksum': checksum,
                        'timestamp': timestamp,
                        'url': self._generate_download_url(s3_key)
                    }
                else:
                    raise Exception("Failed to upload backup to S3")
                    
        except Exception as e:
            logger.error(f"Backup failed for {client_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _backup_mysql(self, client_id: str, temp_path: Path) -> Optional[Path]:
        """Backup MySQL database"""
        
        try:
            # Use kubectl to exec into MySQL pod and dump database
            namespace = f"client-{client_id}"
            pod_name = f"mysql-{client_id}"
            db_name = f"wordpress_{client_id}"
            
            dump_file = temp_path / f"database_{client_id}.sql"
            
            # Get MySQL credentials from Kubernetes secret
            get_password_cmd = [
                "kubectl", "get", "secret",
                f"mysql-{client_id}-secret",
                "-n", namespace,
                "-o", "jsonpath='{.data.password}'",
                "|", "base64", "-d"
            ]
            
            # Execute mysqldump
            dump_cmd = [
                "kubectl", "exec",
                "-n", namespace,
                pod_name,
                "--",
                "mysqldump",
                f"--user=wp_{client_id}",
                "--single-transaction",
                "--routines",
                "--triggers",
                "--events",
                db_name
            ]
            
            # Run mysqldump and save to file
            result = subprocess.run(
                " ".join(dump_cmd),
                shell=True,
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                dump_file.write_text(result.stdout)
                
                # Compress the SQL dump
                compressed_file = temp_path / f"database_{client_id}.sql.gz"
                import gzip
                with open(dump_file, 'rb') as f_in:
                    with gzip.open(compressed_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                logger.info(f"Database backup completed for {client_id}")
                return compressed_file
            else:
                logger.error(f"Database backup failed: {result.stderr}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to backup MySQL for {client_id}: {str(e)}")
            return None
    
    async def _backup_wordpress_files(
        self,
        client_id: str,
        temp_path: Path,
        include_uploads: bool,
        include_plugins: bool,
        include_themes: bool
    ) -> Optional[Path]:
        """Backup WordPress files"""
        
        try:
            namespace = f"client-{client_id}"
            pod_name = f"wordpress-{client_id}"
            
            # Paths to backup
            paths_to_backup = []
            if include_uploads:
                paths_to_backup.append("/var/www/html/wp-content/uploads")
            if include_plugins:
                paths_to_backup.append("/var/www/html/wp-content/plugins")
            if include_themes:
                paths_to_backup.append("/var/www/html/wp-content/themes")
            
            # Always backup wp-config.php
            paths_to_backup.append("/var/www/html/wp-config.php")
            
            # Create tar archive in the pod
            tar_cmd = [
                "kubectl", "exec",
                "-n", namespace,
                pod_name,
                "--",
                "tar", "-czf",
                f"/tmp/wordpress_files_{client_id}.tar.gz"
            ] + paths_to_backup
            
            # Execute tar command
            result = subprocess.run(tar_cmd, capture_output=True)
            
            if result.returncode == 0:
                # Copy archive from pod to local
                files_archive = temp_path / f"wordpress_files_{client_id}.tar.gz"
                
                copy_cmd = [
                    "kubectl", "cp",
                    f"{namespace}/{pod_name}:/tmp/wordpress_files_{client_id}.tar.gz",
                    str(files_archive)
                ]
                
                subprocess.run(copy_cmd, check=True)
                
                # Clean up archive in pod
                cleanup_cmd = [
                    "kubectl", "exec",
                    "-n", namespace,
                    pod_name,
                    "--",
                    "rm", f"/tmp/wordpress_files_{client_id}.tar.gz"
                ]
                subprocess.run(cleanup_cmd)
                
                logger.info(f"WordPress files backup completed for {client_id}")
                return files_archive
            else:
                logger.error(f"Files backup failed: {result.stderr.decode()}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to backup WordPress files for {client_id}: {str(e)}")
            return None
    
    def _create_backup_metadata(
        self,
        client_id: str,
        backup_id: str,
        temp_path: Path,
        backup_info: Dict
    ) -> Path:
        """Create metadata file for the backup"""
        
        metadata = {
            'backup_id': backup_id,
            'client_id': client_id,
            'timestamp': datetime.now().isoformat(),
            'wordpress_version': self._get_wordpress_version(client_id),
            'php_version': '8.2',
            'mysql_version': '8.0',
            'backup_contents': backup_info,
            'retention_policy': self.retention_policies,
            'created_by': 'KenzySites Backup Service'
        }
        
        metadata_file = temp_path / 'metadata.json'
        metadata_file.write_text(json.dumps(metadata, indent=2))
        
        return metadata_file
    
    def _get_wordpress_version(self, client_id: str) -> str:
        """Get WordPress version for the site"""
        try:
            namespace = f"client-{client_id}"
            pod_name = f"wordpress-{client_id}"
            
            cmd = [
                "kubectl", "exec",
                "-n", namespace,
                pod_name,
                "--",
                "wp", "core", "version"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return "unknown"
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Calculate SHA256 checksum of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    async def _upload_to_s3(
        self,
        file_path: Path,
        s3_key: str,
        metadata: Dict[str, str]
    ) -> Dict[str, Any]:
        """Upload file to S3"""
        
        try:
            # Upload with metadata
            self.s3_client.upload_file(
                str(file_path),
                self.s3_bucket,
                s3_key,
                ExtraArgs={
                    'Metadata': metadata,
                    'StorageClass': 'STANDARD_IA'  # Infrequent Access for cost savings
                }
            )
            
            logger.info(f"Uploaded backup to S3: {s3_key}")
            
            return {'success': True}
            
        except Exception as e:
            logger.error(f"Failed to upload to S3: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def _generate_download_url(self, s3_key: str, expiration: int = 3600) -> str:
        """Generate presigned URL for downloading backup"""
        
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.s3_bucket, 'Key': s3_key},
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate download URL: {str(e)}")
            return ""
    
    async def _cleanup_old_backups(self, client_id: str, backup_type: str):
        """Clean up old backups based on retention policy"""
        
        try:
            prefix = f"{backup_type}/{client_id}/"
            
            # List all backups for this client
            response = self.s3_client.list_objects_v2(
                Bucket=self.s3_bucket,
                Prefix=prefix
            )
            
            if 'Contents' not in response:
                return
            
            # Sort by last modified date
            backups = sorted(response['Contents'], key=lambda x: x['LastModified'], reverse=True)
            
            # Determine how many to keep based on backup type
            retention_count = self.retention_policies.get(backup_type, 30)
            
            # Delete old backups
            if len(backups) > retention_count:
                for backup in backups[retention_count:]:
                    self.s3_client.delete_object(
                        Bucket=self.s3_bucket,
                        Key=backup['Key']
                    )
                    logger.info(f"Deleted old backup: {backup['Key']}")
                    
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {str(e)}")
    
    async def restore_backup(
        self,
        client_id: str,
        backup_id: str,
        restore_database: bool = True,
        restore_files: bool = True
    ) -> Dict[str, Any]:
        """
        Restore a backup for a WordPress site
        """
        
        try:
            # Find the backup in S3
            backup_key = None
            for backup_type in ['daily', 'weekly', 'monthly']:
                potential_key = f"{backup_type}/{client_id}/{backup_id}.tar.gz"
                try:
                    self.s3_client.head_object(Bucket=self.s3_bucket, Key=potential_key)
                    backup_key = potential_key
                    break
                except:
                    continue
            
            if not backup_key:
                return {'success': False, 'error': 'Backup not found'}
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                
                # Download backup from S3
                archive_path = temp_path / f"{backup_id}.tar.gz"
                self.s3_client.download_file(self.s3_bucket, backup_key, str(archive_path))
                
                # Extract archive
                with tarfile.open(archive_path, 'r:gz') as tar:
                    tar.extractall(temp_path)
                
                # Read metadata
                metadata_file = temp_path / 'metadata.json'
                if metadata_file.exists():
                    metadata = json.loads(metadata_file.read_text())
                else:
                    metadata = {}
                
                # Restore database if requested
                if restore_database and metadata.get('backup_contents', {}).get('database'):
                    await self._restore_mysql(client_id, temp_path / metadata['backup_contents']['database'])
                
                # Restore files if requested
                if restore_files and metadata.get('backup_contents', {}).get('files'):
                    await self._restore_wordpress_files(client_id, temp_path / metadata['backup_contents']['files'])
                
                return {
                    'success': True,
                    'backup_id': backup_id,
                    'restored_at': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Restore failed for {client_id}: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _restore_mysql(self, client_id: str, sql_file: Path):
        """Restore MySQL database from backup"""
        
        namespace = f"client-{client_id}"
        pod_name = f"mysql-{client_id}"
        db_name = f"wordpress_{client_id}"
        
        # Decompress if needed
        if sql_file.suffix == '.gz':
            import gzip
            decompressed = sql_file.parent / sql_file.stem
            with gzip.open(sql_file, 'rb') as f_in:
                with open(decompressed, 'wb') as f_out:
                    f_out.write(f_in.read())
            sql_file = decompressed
        
        # Copy SQL file to pod
        copy_cmd = [
            "kubectl", "cp",
            str(sql_file),
            f"{namespace}/{pod_name}:/tmp/restore.sql"
        ]
        subprocess.run(copy_cmd, check=True)
        
        # Restore database
        restore_cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "mysql",
            f"--user=wp_{client_id}",
            db_name,
            "<", "/tmp/restore.sql"
        ]
        
        subprocess.run(" ".join(restore_cmd), shell=True, check=True)
        
        # Clean up
        cleanup_cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "rm", "/tmp/restore.sql"
        ]
        subprocess.run(cleanup_cmd)
        
        logger.info(f"Database restored for {client_id}")
    
    async def _restore_wordpress_files(self, client_id: str, files_archive: Path):
        """Restore WordPress files from backup"""
        
        namespace = f"client-{client_id}"
        pod_name = f"wordpress-{client_id}"
        
        # Copy archive to pod
        copy_cmd = [
            "kubectl", "cp",
            str(files_archive),
            f"{namespace}/{pod_name}:/tmp/restore_files.tar.gz"
        ]
        subprocess.run(copy_cmd, check=True)
        
        # Extract files
        extract_cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "tar", "-xzf",
            "/tmp/restore_files.tar.gz",
            "-C", "/var/www/html"
        ]
        subprocess.run(extract_cmd, check=True)
        
        # Fix permissions
        perms_cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "chown", "-R", "www-data:www-data",
            "/var/www/html/wp-content"
        ]
        subprocess.run(perms_cmd)
        
        # Clean up
        cleanup_cmd = [
            "kubectl", "exec",
            "-n", namespace,
            pod_name,
            "--",
            "rm", "/tmp/restore_files.tar.gz"
        ]
        subprocess.run(cleanup_cmd)
        
        logger.info(f"WordPress files restored for {client_id}")
    
    async def list_backups(self, client_id: str) -> List[Dict[str, Any]]:
        """List all available backups for a client"""
        
        backups = []
        
        for backup_type in ['daily', 'weekly', 'monthly']:
            prefix = f"{backup_type}/{client_id}/"
            
            try:
                response = self.s3_client.list_objects_v2(
                    Bucket=self.s3_bucket,
                    Prefix=prefix
                )
                
                if 'Contents' in response:
                    for obj in response['Contents']:
                        # Get metadata
                        head_response = self.s3_client.head_object(
                            Bucket=self.s3_bucket,
                            Key=obj['Key']
                        )
                        
                        backups.append({
                            'key': obj['Key'],
                            'backup_id': Path(obj['Key']).stem,
                            'type': backup_type,
                            'size': obj['Size'],
                            'created': obj['LastModified'].isoformat(),
                            'metadata': head_response.get('Metadata', {}),
                            'download_url': self._generate_download_url(obj['Key'])
                        })
                        
            except Exception as e:
                logger.error(f"Failed to list backups for {client_id}: {str(e)}")
        
        # Sort by creation date
        backups.sort(key=lambda x: x['created'], reverse=True)
        
        return backups

# Global instance
backup_service = BackupService()