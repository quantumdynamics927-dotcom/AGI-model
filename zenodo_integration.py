"""
Zenodo API Integration for Quantum Result Archive
==================================================

Provides integration with Zenodo for publishing and archiving
quantum experiment results with DOI generation.

References:
- Zenodo API: https://developers.zenodo.org/
- DOI generation and management
- Metadata standards for scientific data
"""

import os
import json
import hashlib
import requests
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class ZenodoMetadata:
    """Metadata for Zenodo deposition."""
    title: str
    description: str
    creators: List[Dict[str, str]]
    keywords: List[str]
    license: str = "mit"
    upload_type: str = "dataset"
    access_right: str = "open"
    publication_date: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to Zenodo API format."""
        data = {
            'metadata': {
                'title': self.title,
                'description': self.description,
                'creators': self.creators,
                'keywords': self.keywords,
                'license': {'id': self.license},
                'upload_type': self.upload_type,
                'access_right': self.access_right,
            }
        }
        
        if self.publication_date:
            data['metadata']['publication_date'] = self.publication_date
        
        return data


@dataclass
class ZenodoDeposition:
    """Represents a Zenodo deposition."""
    id: int
    doi: Optional[str]
    title: str
    state: str
    submitted: bool
    files: List[Dict[str, Any]] = field(default_factory=list)
    links: Dict[str, str] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ZenodoClient:
    """
    Client for Zenodo API integration.
    
    Supports:
    - Creating depositions
    - Uploading files
    - Publishing with DOI
    - Retrieving existing depositions
    """
    
    SANDBOX_URL = "https://sandbox.zenodo.org/api"
    PRODUCTION_URL = "https://zenodo.org/api"
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        sandbox: bool = True,
        auto_publish: bool = False
    ):
        """
        Initialize Zenodo client.
        
        Args:
            api_key: Zenodo API key (or set ZENODO_API_KEY env var)
            sandbox: Use sandbox environment for testing
            auto_publish: Automatically publish after upload
        """
        self.api_key = api_key or os.environ.get('ZENODO_API_KEY')
        self.sandbox = sandbox
        self.auto_publish = auto_publish
        
        self.base_url = self.SANDBOX_URL if sandbox else self.PRODUCTION_URL
        
        if not self.api_key:
            logger.warning("No Zenodo API key provided. Set ZENODO_API_KEY environment variable.")
    
    @property
    def headers(self) -> Dict[str, str]:
        """Get authorization headers."""
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def create_deposition(
        self,
        metadata: ZenodoMetadata
    ) -> ZenodoDeposition:
        """
        Create a new deposition.
        
        Args:
            metadata: Deposition metadata
            
        Returns:
            ZenodoDeposition object
        """
        url = f"{self.base_url}/deposit/depositions"
        
        response = requests.post(
            url,
            headers=self.headers,
            json=metadata.to_dict()
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to create deposition: {response.text}")
        
        data = response.json()
        
        deposition = ZenodoDeposition(
            id=data['id'],
            doi=data.get('doi'),
            title=data['title'],
            state=data['state'],
            submitted=data.get('submitted', False),
            files=data.get('files', []),
            links=data.get('links', {})
        )
        
        logger.info(f"Created deposition {deposition.id}")
        return deposition
    
    def upload_file(
        self,
        deposition_id: int,
        file_path: Union[str, Path],
        file_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Upload a file to a deposition.
        
        Args:
            deposition_id: Zenodo deposition ID
            file_path: Path to file
            file_name: Optional custom filename
            
        Returns:
            Upload response data
        """
        file_path = Path(file_path)
        file_name = file_name or file_path.name
        
        # Get upload URL
        url = f"{self.base_url}/deposit/depositions/{deposition_id}/files"
        
        # Upload file
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            headers = {'Authorization': f'Bearer {self.api_key}'}
            
            response = requests.post(
                url,
                headers=headers,
                files=files
            )
        
        if response.status_code != 201:
            raise Exception(f"Failed to upload file: {response.text}")
        
        logger.info(f"Uploaded {file_name} to deposition {deposition_id}")
        return response.json()
    
    def upload_metadata(
        self,
        deposition_id: int,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Upload metadata JSON to deposition.
        
        Args:
            deposition_id: Zenodo deposition ID
            metadata: Metadata dictionary
            
        Returns:
            Upload response data
        """
        # Create temporary file
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump(metadata, f, indent=2)
            temp_path = f.name
        
        try:
            return self.upload_file(
                deposition_id,
                temp_path,
                'metadata.json'
            )
        finally:
            os.unlink(temp_path)
    
    def publish_deposition(
        self,
        deposition_id: int
    ) -> ZenodoDeposition:
        """
        Publish a deposition and get DOI.
        
        Args:
            deposition_id: Zenodo deposition ID
            
        Returns:
            Published ZenodoDeposition
        """
        url = f"{self.base_url}/deposit/depositions/{deposition_id}/actions/publish"
        
        response = requests.post(url, headers=self.headers)
        
        if response.status_code != 202:
            raise Exception(f"Failed to publish deposition: {response.text}")
        
        data = response.json()
        
        deposition = ZenodoDeposition(
            id=data['id'],
            doi=data.get('doi'),
            title=data['title'],
            state=data['state'],
            submitted=data.get('submitted', True),
            files=data.get('files', []),
            links=data.get('links', {})
        )
        
        logger.info(f"Published deposition {deposition.id} with DOI: {deposition.doi}")
        return deposition
    
    def get_deposition(
        self,
        deposition_id: int
    ) -> ZenodoDeposition:
        """
        Get deposition details.
        
        Args:
            deposition_id: Zenodo deposition ID
            
        Returns:
            ZenodoDeposition object
        """
        url = f"{self.base_url}/deposit/depositions/{deposition_id}"
        
        response = requests.get(url, headers=self.headers)
        
        if response.status_code != 200:
            raise Exception(f"Failed to get deposition: {response.text}")
        
        data = response.json()
        
        return ZenodoDeposition(
            id=data['id'],
            doi=data.get('doi'),
            title=data['title'],
            state=data['state'],
            submitted=data.get('submitted', False),
            files=data.get('files', []),
            links=data.get('links', {})
        )
    
    def search_depositions(
        self,
        query: str,
        page: int = 1,
        size: int = 10
    ) -> List[ZenodoDeposition]:
        """
        Search for depositions.
        
        Args:
            query: Search query
            page: Page number
            size: Results per page
            
        Returns:
            List of ZenodoDeposition objects
        """
        url = f"{self.base_url}/records"
        params = {
            'q': query,
            'page': page,
            'size': size
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code != 200:
            raise Exception(f"Failed to search: {response.text}")
        
        data = response.json()
        
        depositions = []
        for hit in data.get('hits', {}).get('hits', []):
            depositions.append(ZenodoDeposition(
                id=hit['id'],
                doi=hit.get('doi'),
                title=hit.get('metadata', {}).get('title', ''),
                state='published',
                submitted=True,
                files=[],
                links=hit.get('links', {})
            ))
        
        return depositions
    
    def delete_deposition(
        self,
        deposition_id: int
    ) -> bool:
        """
        Delete an unpublished deposition.
        
        Args:
            deposition_id: Zenodo deposition ID
            
        Returns:
            True if successful
        """
        url = f"{self.base_url}/deposit/depositions/{deposition_id}"
        
        response = requests.delete(url, headers=self.headers)
        
        if response.status_code == 204:
            logger.info(f"Deleted deposition {deposition_id}")
            return True
        
        return False


class QuantumResultPublisher:
    """
    Publish quantum experiment results to Zenodo.
    
    Integrates with QuantumResultArchive for seamless
    publication of quantum experiment data.
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        sandbox: bool = True
    ):
        """
        Initialize publisher.
        
        Args:
            api_key: Zenodo API key
            sandbox: Use sandbox environment
        """
        self.client = ZenodoClient(api_key=api_key, sandbox=sandbox)
    
    def publish_archive_result(
        self,
        archive_id: str,
        result_data: Dict[str, Any],
        fingerprint: Dict[str, str],
        authors: List[Dict[str, str]],
        title: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> ZenodoDeposition:
        """
        Publish an archived quantum result to Zenodo.
        
        Args:
            archive_id: Quantum archive ID
            result_data: Experiment result data
            fingerprint: Quantum fingerprint data
            authors: List of author dictionaries
            title: Optional custom title
            keywords: Optional custom keywords
            
        Returns:
            Published ZenodoDeposition
        """
        # Create metadata
        title = title or f"Quantum Experiment: {fingerprint.get('experiment_type', 'Unknown')}"
        
        keywords = keywords or [
            'quantum',
            'consciousness',
            'VAE',
            'TMT-OS',
            'quantum-computing',
            'machine-learning'
        ]
        
        # Add archive ID to keywords
        keywords.append(f'archive-{archive_id}')
        
        metadata = ZenodoMetadata(
            title=title,
            description=f"Quantum experiment result from TMT-OS Quantum Consciousness system.\n\n"
                       f"Archive ID: {archive_id}\n"
                       f"Experiment Type: {fingerprint.get('experiment_type', 'Unknown')}\n"
                       f"SHA3-256: {fingerprint.get('sha3_256', 'N/A')}\n"
                       f"Timestamp: {fingerprint.get('timestamp', 'N/A')}",
            creators=authors,
            keywords=keywords,
            license='mit',
            upload_type='dataset'
        )
        
        # Create deposition
        deposition = self.client.create_deposition(metadata)
        
        # Upload result data
        import tempfile
        
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.json',
            delete=False
        ) as f:
            json.dump({
                'archive_id': archive_id,
                'result_data': result_data,
                'fingerprint': fingerprint
            }, f, indent=2)
            temp_path = f.name
        
        try:
            self.client.upload_file(
                deposition.id,
                temp_path,
                f'{archive_id}_data.json'
            )
        finally:
            os.unlink(temp_path)
        
        # Publish
        if self.client.auto_publish:
            deposition = self.client.publish_deposition(deposition.id)
        
        return deposition
    
    def create_version(
        self,
        deposition_id: int,
        new_data: Dict[str, Any],
        version_notes: str
    ) -> ZenodoDeposition:
        """
        Create a new version of an existing deposition.
        
        Args:
            deposition_id: Original deposition ID
            new_data: New data to add
            version_notes: Notes for this version
            
        Returns:
            New ZenodoDeposition
        """
        # Get original deposition
        original = self.client.get_deposition(deposition_id)
        
        # Create new version (simplified - Zenodo has specific versioning API)
        # This is a placeholder for the actual versioning workflow
        logger.info(f"Creating new version of deposition {deposition_id}")
        
        # In practice, you would use Zenodo's versioning API
        # For now, return the original
        return original


def generate_doi(
    result_data: Dict[str, Any],
    fingerprint: Dict[str, str],
    authors: List[Dict[str, str]],
    sandbox: bool = True
) -> Optional[str]:
    """
    Convenience function to generate a DOI for quantum results.
    
    Args:
        result_data: Experiment result data
        fingerprint: Quantum fingerprint
        authors: List of authors
        sandbox: Use sandbox environment
        
    Returns:
        DOI string or None if failed
    """
    try:
        publisher = QuantumResultPublisher(sandbox=sandbox)
        
        deposition = publisher.publish_archive_result(
            archive_id=fingerprint.get('experiment_id', 'unknown'),
            result_data=result_data,
            fingerprint=fingerprint,
            authors=authors
        )
        
        return deposition.doi
    except Exception as e:
        logger.error(f"Failed to generate DOI: {e}")
        return None


if __name__ == "__main__":
    print("Zenodo API Integration for Quantum Result Archive")
    print("=" * 50)
    
    # Example usage
    print("\nTo use this module, set ZENODO_API_KEY environment variable:")
    print("  export ZENODO_API_KEY='your-api-key'")
    
    # Create sample data
    sample_result = {
        'fidelity': 0.9876,
        'coherence': 0.9543,
        'kl_divergence': 0.0234,
        'latent_dim': 32
    }
    
    sample_fingerprint = {
        'experiment_id': 'QRA-000001',
        'experiment_type': 'vae_training',
        'sha3_256': 'abc123...',
        'timestamp': datetime.now().isoformat()
    }
    
    sample_authors = [
        {'name': 'TMT-OS System', 'affiliation': 'Quantum Consciousness Lab'}
    ]
    
    print("\nSample metadata:")
    metadata = ZenodoMetadata(
        title="Quantum VAE Training Results",
        description="Experimental results from quantum consciousness VAE",
        creators=sample_authors,
        keywords=['quantum', 'VAE', 'consciousness', 'TMT-OS']
    )
    print(json.dumps(metadata.to_dict(), indent=2))