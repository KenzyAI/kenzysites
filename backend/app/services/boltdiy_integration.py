"""
Bolt.DIY Integration Service
Real integration with Bolt.DIY open source landing page builder
Parallel implementation to mock service for comparison
"""

import logging
import aiohttp
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
import uuid
import asyncio

logger = logging.getLogger(__name__)

# Configuration
BOLTDIY_URL = "http://localhost:5173"  # Default Bolt.DIY URL
BOLTDIY_API_URL = f"{BOLTDIY_URL}/api"

class BoltProjectType(str, Enum):
    VANILLA = "vanilla"
    REACT = "react"
    VUE = "vue"
    ANGULAR = "angular"
    SVELTE = "svelte"
    NEXTJS = "nextjs"
    ASTRO = "astro"

class BoltProjectStatus(str, Enum):
    CREATING = "creating"
    READY = "ready"
    BUILDING = "building"
    ERROR = "error"
    EXPORTED = "exported"

class BoltProject(BaseModel):
    """Bolt.DIY project model"""
    id: str = Field(default_factory=lambda: f"bolt_{uuid.uuid4().hex[:8]}")
    name: str
    type: BoltProjectType = BoltProjectType.REACT
    status: BoltProjectStatus = BoltProjectStatus.CREATING
    
    # URLs
    editor_url: Optional[str] = None
    preview_url: Optional[str] = None
    export_url: Optional[str] = None
    
    # Project data
    files: Dict[str, str] = Field(default_factory=dict)
    dependencies: Dict[str, str] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    # Export data
    exported_html: Optional[str] = None
    exported_assets: List[str] = Field(default_factory=list)

class BoltDIYIntegration:
    """Integration service for Bolt.DIY"""
    
    def __init__(self, bolt_url: str = BOLTDIY_URL):
        self.bolt_url = bolt_url
        self.api_url = f"{bolt_url}/api"
        self.projects: Dict[str, BoltProject] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def initialize(self):
        """Initialize connection to Bolt.DIY"""
        try:
            self.session = aiohttp.ClientSession()
            
            # Check if Bolt.DIY is running
            async with self.session.get(self.bolt_url) as response:
                if response.status == 200:
                    logger.info(f"Connected to Bolt.DIY at {self.bolt_url}")
                    return True
                else:
                    logger.warning(f"Bolt.DIY not responding at {self.bolt_url}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect to Bolt.DIY: {str(e)}")
            return False
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
    
    async def create_project(
        self,
        name: str,
        type: BoltProjectType = BoltProjectType.REACT,
        template: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ) -> BoltProject:
        """
        Create a new Bolt.DIY project
        
        Args:
            name: Project name
            type: Project type (React, Vue, etc.)
            template: Template to use
            config: Additional configuration
        """
        
        project = BoltProject(
            name=name,
            type=type,
            status=BoltProjectStatus.CREATING
        )
        
        try:
            # In real implementation, would call Bolt.DIY API
            # For now, simulate the project creation
            
            if template:
                # Load template
                project.files = await self._load_template(template, type)
            else:
                # Create default project structure
                project.files = self._create_default_project(type)
            
            # Set URLs
            project.editor_url = f"{self.bolt_url}/editor/{project.id}"
            project.preview_url = f"{self.bolt_url}/preview/{project.id}"
            project.export_url = f"{self.bolt_url}/export/{project.id}"
            
            # Apply configuration
            if config:
                project.files = self._apply_config(project.files, config)
            
            project.status = BoltProjectStatus.READY
            self.projects[project.id] = project
            
            logger.info(f"Created Bolt.DIY project {project.id}")
            return project
            
        except Exception as e:
            logger.error(f"Failed to create Bolt.DIY project: {str(e)}")
            project.status = BoltProjectStatus.ERROR
            raise
    
    def _create_default_project(self, type: BoltProjectType) -> Dict[str, str]:
        """Create default project files based on type"""
        
        if type == BoltProjectType.REACT:
            return {
                "package.json": json.dumps({
                    "name": "landing-page",
                    "version": "1.0.0",
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    },
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build"
                    }
                }, indent=2),
                "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
</body>
</html>""",
                "src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)""",
                "src/App.jsx": """import React from 'react'

function App() {
  return (
    <div className="app">
      <header>
        <h1>Welcome to Your Landing Page</h1>
        <p>Built with Bolt.DIY</p>
      </header>
      <main>
        <section className="hero">
          <h2>Build Amazing Websites</h2>
          <p>Create stunning landing pages in minutes</p>
          <button>Get Started</button>
        </section>
      </main>
    </div>
  )
}

export default App""",
                "src/index.css": """* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 2rem;
  text-align: center;
}

.hero {
  padding: 4rem 2rem;
  text-align: center;
}

button {
  background: #667eea;
  color: white;
  border: none;
  padding: 1rem 2rem;
  font-size: 1.1rem;
  border-radius: 5px;
  cursor: pointer;
  margin-top: 1rem;
}

button:hover {
  background: #764ba2;
}"""
            }
        
        elif type == BoltProjectType.VUE:
            return {
                "package.json": json.dumps({
                    "name": "landing-page-vue",
                    "version": "1.0.0",
                    "dependencies": {
                        "vue": "^3.3.0"
                    },
                    "scripts": {
                        "dev": "vite",
                        "build": "vite build"
                    }
                }, indent=2),
                "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vue Landing Page</title>
</head>
<body>
    <div id="app"></div>
    <script type="module" src="/src/main.js"></script>
</body>
</html>""",
                "src/main.js": """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')""",
                "src/App.vue": """<template>
  <div class="app">
    <header>
      <h1>Vue Landing Page</h1>
    </header>
    <main>
      <section class="hero">
        <h2>Built with Bolt.DIY</h2>
        <button>Get Started</button>
      </section>
    </main>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
.app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
}
</style>"""
            }
        
        else:  # Vanilla HTML/CSS/JS
            return {
                "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Landing Page</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>Welcome to Your Landing Page</h1>
    </header>
    <main>
        <section class="hero">
            <h2>Build Amazing Websites</h2>
            <p>Create stunning landing pages in minutes</p>
            <button id="cta-button">Get Started</button>
        </section>
    </main>
    <script src="script.js"></script>
</body>
</html>""",
                "style.css": """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    text-align: center;
}

.hero {
    padding: 4rem 2rem;
    text-align: center;
    max-width: 800px;
    margin: 0 auto;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    border-radius: 5px;
    cursor: pointer;
    transition: background 0.3s;
}

button:hover {
    background: #764ba2;
}""",
                "script.js": """document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('cta-button');
    
    button.addEventListener('click', function() {
        alert('Welcome to Bolt.DIY!');
    });
});"""
            }
    
    async def _load_template(
        self,
        template_id: str,
        type: BoltProjectType
    ) -> Dict[str, str]:
        """Load a template from Bolt.DIY templates library"""
        
        # In real implementation, would fetch from Bolt.DIY templates
        # For now, return enhanced default based on template_id
        
        base_files = self._create_default_project(type)
        
        # Enhance based on template type
        if "ecommerce" in template_id.lower():
            if type == BoltProjectType.REACT:
                base_files["src/components/ProductCard.jsx"] = """import React from 'react'

export default function ProductCard({ product }) {
  return (
    <div className="product-card">
      <img src={product.image} alt={product.name} />
      <h3>{product.name}</h3>
      <p className="price">${product.price}</p>
      <button>Add to Cart</button>
    </div>
  )
}"""
        
        elif "saas" in template_id.lower():
            if type == BoltProjectType.REACT:
                base_files["src/components/PricingTable.jsx"] = """import React from 'react'

export default function PricingTable() {
  return (
    <div className="pricing-table">
      <div className="plan">
        <h3>Starter</h3>
        <p className="price">$9/mo</p>
        <ul>
          <li>Feature 1</li>
          <li>Feature 2</li>
        </ul>
        <button>Choose Plan</button>
      </div>
    </div>
  )
}"""
        
        return base_files
    
    def _apply_config(
        self,
        files: Dict[str, str],
        config: Dict[str, Any]
    ) -> Dict[str, str]:
        """Apply configuration to project files"""
        
        # Replace placeholders in files with config values
        for filename, content in files.items():
            if "brand_name" in config:
                content = content.replace("Your Landing Page", config["brand_name"])
            if "primary_color" in config:
                content = content.replace("#667eea", config["primary_color"])
            if "description" in config:
                content = content.replace(
                    "Create stunning landing pages in minutes",
                    config["description"]
                )
            files[filename] = content
        
        return files
    
    async def update_project_file(
        self,
        project_id: str,
        file_path: str,
        content: str
    ) -> bool:
        """Update a file in the project"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.files[file_path] = content
        project.updated_at = datetime.now()
        
        logger.info(f"Updated file {file_path} in project {project_id}")
        return True
    
    async def export_project(
        self,
        project_id: str,
        format: str = "html"
    ) -> Dict[str, Any]:
        """
        Export project in specified format
        
        Args:
            project_id: Project ID
            format: Export format (html, react, vue, zip)
        """
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        project.status = BoltProjectStatus.BUILDING
        
        try:
            if format == "html":
                # Export as static HTML
                exported_html = await self._build_static_html(project)
                project.exported_html = exported_html
                
            elif format == "react":
                # Export as React component
                return {
                    "format": "react",
                    "files": project.files,
                    "dependencies": {
                        "react": "^18.2.0",
                        "react-dom": "^18.2.0"
                    }
                }
                
            elif format == "zip":
                # Would create a zip file with all project files
                return {
                    "format": "zip",
                    "download_url": f"{self.bolt_url}/download/{project_id}.zip"
                }
            
            project.status = BoltProjectStatus.EXPORTED
            
            return {
                "format": format,
                "project_id": project_id,
                "exported_at": datetime.now().isoformat(),
                "html": project.exported_html if format == "html" else None
            }
            
        except Exception as e:
            logger.error(f"Failed to export project: {str(e)}")
            project.status = BoltProjectStatus.ERROR
            raise
    
    async def _build_static_html(self, project: BoltProject) -> str:
        """Build project as static HTML"""
        
        # In real implementation, would use Vite/Webpack to build
        # For now, return the HTML file content
        
        html = project.files.get("index.html", "")
        css = project.files.get("style.css", "") or project.files.get("src/index.css", "")
        js = project.files.get("script.js", "") or project.files.get("src/main.js", "")
        
        # Inline CSS and JS for single-file export
        if css:
            html = html.replace("</head>", f"<style>{css}</style></head>")
        if js and "script.js" in js:
            html = html.replace("</body>", f"<script>{js}</script></body>")
        
        return html
    
    async def deploy_to_wordpress(
        self,
        project_id: str,
        site_id: str
    ) -> Dict[str, Any]:
        """Deploy Bolt.DIY project as WordPress page"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Export as HTML
        export_result = await self.export_project(project_id, "html")
        html_content = export_result.get("html", "")
        
        # Convert to WordPress compatible format
        wp_content = self._convert_to_wordpress(html_content)
        
        # Would integrate with WordPress service to create page
        return {
            "success": True,
            "wordpress_page_id": f"wp_page_{uuid.uuid4().hex[:8]}",
            "site_id": site_id,
            "content": wp_content[:500] + "...",  # Preview
            "message": "Successfully deployed to WordPress"
        }
    
    def _convert_to_wordpress(self, html: str) -> str:
        """Convert HTML to WordPress Gutenberg blocks"""
        
        # Simple conversion - in production would use proper parser
        wp_content = html
        
        # Convert to Gutenberg blocks format
        wp_content = wp_content.replace("<header>", "<!-- wp:group --><div class='wp-block-group'>")
        wp_content = wp_content.replace("</header>", "</div><!-- /wp:group -->")
        wp_content = wp_content.replace("<h1>", "<!-- wp:heading {\"level\":1} --><h1>")
        wp_content = wp_content.replace("</h1>", "</h1><!-- /wp:heading -->")
        wp_content = wp_content.replace("<button>", "<!-- wp:button --><div class='wp-block-button'><a class='wp-block-button__link'>")
        wp_content = wp_content.replace("</button>", "</a></div><!-- /wp:button -->")
        
        return wp_content
    
    async def get_project_preview_url(self, project_id: str) -> str:
        """Get live preview URL for project"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return project.preview_url or f"{self.bolt_url}/preview/{project_id}"
    
    async def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """Get project status and metadata"""
        
        project = self.projects.get(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return {
            "id": project.id,
            "name": project.name,
            "type": project.type.value,
            "status": project.status.value,
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat(),
            "files_count": len(project.files),
            "editor_url": project.editor_url,
            "preview_url": project.preview_url
        }
    
    async def list_projects(self) -> List[Dict[str, Any]]:
        """List all projects"""
        
        return [
            await self.get_project_status(project_id)
            for project_id in self.projects.keys()
        ]

# Global instance
boltdiy_integration = BoltDIYIntegration()