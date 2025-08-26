"""
Visual Editor API Routes
"""

from fastapi import APIRouter, HTTPException, Depends, Body
from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
from datetime import datetime

from ...services.visual_editor import (
    VisualEditorService,
    Widget,
    Page,
    WidgetStyle
)
from ...middleware.auth_middleware import get_current_user
from ...models.user import User

router = APIRouter(prefix="/api/editor", tags=["editor"])

# Initialize service
editor_service = VisualEditorService()

class CreateWidgetRequest(BaseModel):
    type: str
    content: Optional[Dict[str, Any]] = None
    parentId: Optional[str] = None
    position: Optional[int] = 0

class UpdateWidgetRequest(BaseModel):
    widgetId: str
    updates: Dict[str, Any]

class MoveWidgetRequest(BaseModel):
    widgetId: str
    targetParentId: Optional[str] = None
    position: int

class DuplicateWidgetRequest(BaseModel):
    widgetId: str
    targetParentId: Optional[str] = None

class SavePageRequest(BaseModel):
    pageId: str
    name: str
    widgets: List[Dict[str, Any]]
    settings: Dict[str, Any]
    seo: Dict[str, Any]

class ApplyThemeRequest(BaseModel):
    pageId: str
    theme: Dict[str, Any]

@router.get("/widgets/library")
async def get_widget_library(
    current_user: User = Depends(get_current_user)
):
    """Get available widget types and their configurations"""
    return {
        "success": True,
        "widgets": editor_service.widget_library
    }

@router.get("/templates")
async def get_editor_templates(
    current_user: User = Depends(get_current_user)
):
    """Get available editor templates"""
    return {
        "success": True,
        "templates": editor_service.templates
    }

@router.post("/widgets/create")
async def create_widget(
    request: CreateWidgetRequest,
    current_user: User = Depends(get_current_user)
):
    """Create a new widget"""
    try:
        widget = editor_service.create_widget(
            widget_type=request.type,
            custom_content=request.content
        )
        
        return {
            "success": True,
            "widget": widget.dict()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/widgets/update")
async def update_widget(
    request: UpdateWidgetRequest,
    current_user: User = Depends(get_current_user)
):
    """Update widget properties"""
    # In a real implementation, we would load the widget from storage
    # For now, we'll create a dummy widget to demonstrate
    widget = Widget(
        id=request.widgetId,
        type="text",
        content={},
        style=WidgetStyle()
    )
    
    updated_widget = editor_service.update_widget(widget, request.updates)
    
    return {
        "success": True,
        "widget": updated_widget.dict()
    }

@router.post("/widgets/duplicate")
async def duplicate_widget(
    request: DuplicateWidgetRequest,
    current_user: User = Depends(get_current_user)
):
    """Duplicate a widget"""
    # In a real implementation, we would load the widget from storage
    widget = Widget(
        id=request.widgetId,
        type="text",
        content={"text": "Duplicated widget"},
        style=WidgetStyle()
    )
    
    duplicated = editor_service.duplicate_widget(widget)
    
    return {
        "success": True,
        "widget": duplicated.dict()
    }

@router.post("/pages/save")
async def save_page(
    request: SavePageRequest,
    current_user: User = Depends(get_current_user)
):
    """Save page configuration"""
    # Convert dict widgets to Widget objects
    widgets = []
    for widget_data in request.widgets:
        widget = Widget(
            id=widget_data.get("id"),
            type=widget_data.get("type"),
            content=widget_data.get("content", {}),
            style=WidgetStyle(**widget_data.get("style", {})),
            children=widget_data.get("children", []),
            settings=widget_data.get("settings", {})
        )
        widgets.append(widget)
    
    page = Page(
        id=request.pageId,
        name=request.name,
        slug=request.name.lower().replace(" ", "-"),
        widgets=widgets,
        settings=request.settings,
        seo=request.seo,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # In a real implementation, save to database
    # For now, return success
    
    return {
        "success": True,
        "page": {
            "id": page.id,
            "name": page.name,
            "slug": page.slug
        }
    }

@router.get("/pages/{page_id}")
async def get_page(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get page configuration"""
    # In a real implementation, load from database
    # For now, return a sample page
    
    page = Page(
        id=page_id,
        name="Sample Page",
        slug="sample-page",
        widgets=[],
        settings={},
        seo={
            "title": "Sample Page",
            "description": "A sample page"
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    return {
        "success": True,
        "page": page.dict()
    }

@router.post("/pages/{page_id}/export/html")
async def export_page_html(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Export page to HTML"""
    # In a real implementation, load page from database
    page = Page(
        id=page_id,
        name="Exported Page",
        slug="exported-page",
        widgets=[],
        settings={},
        seo={
            "title": "Exported Page",
            "description": "An exported page"
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    html = editor_service.export_to_html(page)
    
    return {
        "success": True,
        "html": html
    }

@router.post("/pages/{page_id}/export/elementor")
async def export_page_elementor(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Export page to Elementor format"""
    # In a real implementation, load page from database
    page = Page(
        id=page_id,
        name="Elementor Page",
        slug="elementor-page",
        widgets=[],
        settings={},
        seo={
            "title": "Elementor Page",
            "description": "An Elementor page"
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    elementor_data = editor_service.export_to_elementor(page)
    
    return {
        "success": True,
        "elementor": elementor_data
    }

@router.post("/pages/{page_id}/export/json")
async def export_page_json(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Export page to JSON"""
    # In a real implementation, load page from database
    page = Page(
        id=page_id,
        name="JSON Page",
        slug="json-page",
        widgets=[],
        settings={},
        seo={
            "title": "JSON Page",
            "description": "A JSON page"
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    json_data = editor_service.export_to_json(page)
    
    return {
        "success": True,
        "json": json.loads(json_data)
    }

@router.post("/pages/import/json")
async def import_page_json(
    json_data: Dict[str, Any] = Body(...),
    current_user: User = Depends(get_current_user)
):
    """Import page from JSON"""
    try:
        page = editor_service.import_from_json(json.dumps(json_data))
        
        return {
            "success": True,
            "page": page.dict()
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/pages/{page_id}/validate")
async def validate_page(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Validate page structure"""
    # In a real implementation, load page from database
    page = Page(
        id=page_id,
        name="Page to Validate",
        slug="page-to-validate",
        widgets=[],
        settings={},
        seo={},
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    errors = editor_service.validate_page(page)
    
    return {
        "success": len(errors) == 0,
        "errors": errors
    }

@router.post("/pages/apply-theme")
async def apply_theme(
    request: ApplyThemeRequest,
    current_user: User = Depends(get_current_user)
):
    """Apply theme to page"""
    # In a real implementation, load page from database
    page = Page(
        id=request.pageId,
        name="Themed Page",
        slug="themed-page",
        widgets=[],
        settings={},
        seo={
            "title": "Themed Page",
            "description": "A themed page"
        },
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    themed_page = editor_service.apply_theme(page, request.theme)
    
    return {
        "success": True,
        "page": themed_page.dict()
    }

@router.post("/pages/{page_id}/preview")
async def preview_page(
    page_id: str,
    device: str = "desktop",
    current_user: User = Depends(get_current_user)
):
    """Generate preview URL for page"""
    preview_url = f"/preview/{page_id}?device={device}"
    
    return {
        "success": True,
        "previewUrl": preview_url,
        "device": device
    }

@router.get("/pages/{page_id}/history")
async def get_page_history(
    page_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get page edit history"""
    # In a real implementation, load from database
    history = [
        {
            "id": "1",
            "timestamp": datetime.now().isoformat(),
            "action": "Created page",
            "user": current_user.email
        }
    ]
    
    return {
        "success": True,
        "history": history
    }

@router.post("/pages/{page_id}/restore/{version_id}")
async def restore_page_version(
    page_id: str,
    version_id: str,
    current_user: User = Depends(get_current_user)
):
    """Restore page to previous version"""
    return {
        "success": True,
        "message": f"Page restored to version {version_id}"
    }

@router.post("/assets/upload")
async def upload_asset(
    current_user: User = Depends(get_current_user)
):
    """Upload image or other asset"""
    # In a real implementation, handle file upload
    return {
        "success": True,
        "url": "https://example.com/uploaded-asset.jpg"
    }

@router.get("/assets/library")
async def get_asset_library(
    current_user: User = Depends(get_current_user)
):
    """Get user's asset library"""
    return {
        "success": True,
        "assets": [
            {
                "id": "1",
                "url": "https://example.com/asset1.jpg",
                "type": "image",
                "name": "Asset 1"
            }
        ]
    }