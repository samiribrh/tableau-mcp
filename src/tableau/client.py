"""Tableau Server connection management."""
from typing import Optional

import tableauserverclient as TSC

from src.config import settings, get_logger

logger = get_logger(__name__)


class TableauClient:
    """
    Manages connection to Tableau Server.
    
    Uses Personal Access Token (PAT) authentication.
    Context manager support for automatic cleanup.
    """
    
    def __init__(
        self,
        server_url: Optional[str] = None,
        site_id: Optional[str] = None,
        pat_name: Optional[str] = None,
        pat_secret: Optional[str] = None,
    ):
        """
        Initialize Tableau client.
        
        Args:
            server_url: Tableau Server URL (defaults to settings)
            site_id: Site ID (defaults to settings)
            pat_name: Personal Access Token name (defaults to settings)
            pat_secret: Personal Access Token secret (defaults to settings)
        """
        self.server_url = server_url or settings.tableau_server
        self.site_id = site_id or settings.tableau_site_id
        self.pat_name = pat_name or settings.tableau_pat_name
        self.pat_secret = pat_secret or settings.tableau_pat_secret
        
        self._server: Optional[TSC.Server] = None
    
    def connect(self) -> TSC.Server:
        """
        Connect to Tableau Server.
        
        Returns:
            Authenticated Tableau Server instance
            
        Raises:
            Exception: If connection fails
        """
        try:
            logger.info(f"Connecting to Tableau Server: {self.server_url}")
            
            # Create authentication
            tableau_auth = TSC.PersonalAccessTokenAuth(
                token_name=self.pat_name,
                personal_access_token=self.pat_secret,
                site_id=self.site_id
            )
            
            # Create server instance
            server = TSC.Server(self.server_url, use_server_version=True)
            
            # Sign in
            server.auth.sign_in(tableau_auth)
            
            self._server = server
            logger.info("✓ Connected to Tableau Server successfully")
            
            return server
            
        except Exception as e:
            logger.error(f"✗ Failed to connect to Tableau Server: {e}")
            raise
    
    def disconnect(self) -> None:
        """Sign out from Tableau Server."""
        if self._server:
            try:
                self._server.auth.sign_out()
                logger.info("✓ Disconnected from Tableau Server")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
            finally:
                self._server = None
    
    @property
    def server(self) -> TSC.Server:
        """Get the connected server instance."""
        if not self._server:
            raise RuntimeError("Not connected to Tableau Server. Call connect() first.")
        return self._server
    
    # Context manager support (allows using 'with' statement)
    def __enter__(self):
        """Enter context manager."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        self.disconnect()


def get_tableau_client() -> TableauClient:
    """
    Factory function to create a Tableau client.
    
    Returns:
        Configured TableauClient instance
    """
    return TableauClient()
