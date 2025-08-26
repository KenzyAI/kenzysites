"""
Visual Editor Service for Template Customization
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel
import json
import uuid
from datetime import datetime

class WidgetType:
    """Widget types for the visual editor"""
    TEXT = "text"
    IMAGE = "image"
    BUTTON = "button"
    CONTAINER = "container"
    SECTION = "section"
    HEADER = "header"
    FOOTER = "footer"
    GALLERY = "gallery"
    FORM = "form"
    MAP = "map"
    VIDEO = "video"
    SOCIAL = "social"
    TESTIMONIAL = "testimonial"
    PRICING = "pricing"
    FAQ = "faq"
    CONTACT = "contact"
    WHATSAPP = "whatsapp"
    PIX = "pix"

class WidgetStyle(BaseModel):
    """Widget styling properties"""
    backgroundColor: Optional[str] = None
    textColor: Optional[str] = None
    fontSize: Optional[str] = None
    fontFamily: Optional[str] = None
    fontWeight: Optional[str] = None
    padding: Optional[Dict[str, str]] = None
    margin: Optional[Dict[str, str]] = None
    border: Optional[Dict[str, Any]] = None
    borderRadius: Optional[str] = None
    boxShadow: Optional[str] = None
    width: Optional[str] = None
    height: Optional[str] = None
    display: Optional[str] = None
    flexDirection: Optional[str] = None
    justifyContent: Optional[str] = None
    alignItems: Optional[str] = None
    gap: Optional[str] = None
    position: Optional[str] = None
    top: Optional[str] = None
    left: Optional[str] = None
    right: Optional[str] = None
    bottom: Optional[str] = None
    zIndex: Optional[int] = None
    opacity: Optional[float] = None
    transform: Optional[str] = None
    transition: Optional[str] = None
    animation: Optional[str] = None
    backgroundImage: Optional[str] = None
    backgroundSize: Optional[str] = None
    backgroundPosition: Optional[str] = None
    backgroundRepeat: Optional[str] = None
    gradient: Optional[Dict[str, Any]] = None

class Widget(BaseModel):
    """Visual editor widget"""
    id: str
    type: str
    content: Dict[str, Any]
    style: WidgetStyle
    children: List['Widget'] = []
    settings: Dict[str, Any] = {}
    animations: List[Dict[str, Any]] = []
    responsive: Dict[str, WidgetStyle] = {}
    locked: bool = False
    visible: bool = True
    
    class Config:
        arbitrary_types_allowed = True

class Page(BaseModel):
    """Page structure for visual editor"""
    id: str
    name: str
    slug: str
    widgets: List[Widget]
    settings: Dict[str, Any]
    seo: Dict[str, Any]
    scripts: List[str] = []
    styles: List[str] = []
    created_at: datetime
    updated_at: datetime

class VisualEditorService:
    """Service for visual template editing"""
    
    def __init__(self):
        self.widget_library = self._initialize_widget_library()
        self.templates = self._load_editor_templates()
    
    def _initialize_widget_library(self) -> Dict[str, Dict[str, Any]]:
        """Initialize widget library with pre-built components"""
        return {
            WidgetType.TEXT: {
                "name": "Texto",
                "icon": "text",
                "defaultContent": {
                    "text": "Digite seu texto aqui",
                    "tag": "p"
                },
                "defaultStyle": {
                    "fontSize": "16px",
                    "textColor": "#333333"
                },
                "settings": {
                    "editable": True,
                    "richText": True
                }
            },
            WidgetType.IMAGE: {
                "name": "Imagem",
                "icon": "image",
                "defaultContent": {
                    "src": "https://via.placeholder.com/600x400",
                    "alt": "Imagem",
                    "lazy": True
                },
                "defaultStyle": {
                    "width": "100%",
                    "height": "auto"
                },
                "settings": {
                    "uploadable": True,
                    "croppable": True,
                    "filters": True
                }
            },
            WidgetType.BUTTON: {
                "name": "Botão",
                "icon": "button",
                "defaultContent": {
                    "text": "Clique Aqui",
                    "link": "#",
                    "target": "_self",
                    "icon": None
                },
                "defaultStyle": {
                    "backgroundColor": "#007bff",
                    "textColor": "#ffffff",
                    "padding": {"top": "12px", "right": "24px", "bottom": "12px", "left": "24px"},
                    "borderRadius": "4px",
                    "fontSize": "16px",
                    "fontWeight": "500",
                    "transition": "all 0.3s ease"
                },
                "settings": {
                    "hoverEffects": True,
                    "iconPosition": "left"
                }
            },
            WidgetType.CONTAINER: {
                "name": "Container",
                "icon": "container",
                "defaultContent": {},
                "defaultStyle": {
                    "padding": {"top": "20px", "right": "20px", "bottom": "20px", "left": "20px"},
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "20px"
                },
                "settings": {
                    "droppable": True,
                    "layout": "flex"
                }
            },
            WidgetType.WHATSAPP: {
                "name": "WhatsApp",
                "icon": "whatsapp",
                "defaultContent": {
                    "phone": "+5511999999999",
                    "message": "Olá! Gostaria de mais informações.",
                    "text": "Fale Conosco no WhatsApp",
                    "showIcon": True
                },
                "defaultStyle": {
                    "backgroundColor": "#25d366",
                    "textColor": "#ffffff",
                    "padding": {"top": "12px", "right": "20px", "bottom": "12px", "left": "20px"},
                    "borderRadius": "50px",
                    "fontSize": "16px",
                    "position": "fixed",
                    "bottom": "30px",
                    "right": "30px",
                    "zIndex": 1000
                },
                "settings": {
                    "floating": True,
                    "animation": "pulse"
                }
            },
            WidgetType.PIX: {
                "name": "PIX QR Code",
                "icon": "qrcode",
                "defaultContent": {
                    "pixKey": "",
                    "amount": None,
                    "merchantName": "",
                    "merchantCity": "",
                    "showQR": True,
                    "showCopyButton": True
                },
                "defaultStyle": {
                    "padding": {"top": "20px", "right": "20px", "bottom": "20px", "left": "20px"},
                    "backgroundColor": "#f8f9fa",
                    "borderRadius": "8px",
                    "textAlign": "center"
                },
                "settings": {
                    "qrSize": 200,
                    "theme": "light"
                }
            },
            WidgetType.GALLERY: {
                "name": "Galeria",
                "icon": "gallery",
                "defaultContent": {
                    "images": [],
                    "layout": "grid",
                    "columns": 3,
                    "lightbox": True
                },
                "defaultStyle": {
                    "display": "grid",
                    "gap": "20px"
                },
                "settings": {
                    "lazy": True,
                    "animation": "fade"
                }
            },
            WidgetType.FORM: {
                "name": "Formulário",
                "icon": "form",
                "defaultContent": {
                    "fields": [
                        {"type": "text", "name": "name", "label": "Nome", "required": True},
                        {"type": "email", "name": "email", "label": "E-mail", "required": True},
                        {"type": "textarea", "name": "message", "label": "Mensagem", "required": False}
                    ],
                    "submitText": "Enviar",
                    "action": "/api/contact",
                    "method": "POST"
                },
                "defaultStyle": {
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "16px"
                },
                "settings": {
                    "validation": True,
                    "recaptcha": False,
                    "lgpdConsent": True
                }
            },
            WidgetType.MAP: {
                "name": "Mapa",
                "icon": "map",
                "defaultContent": {
                    "address": "",
                    "lat": -23.5505,
                    "lng": -46.6333,
                    "zoom": 15,
                    "provider": "google"
                },
                "defaultStyle": {
                    "width": "100%",
                    "height": "400px"
                },
                "settings": {
                    "interactive": True,
                    "markers": True,
                    "controls": True
                }
            },
            WidgetType.TESTIMONIAL: {
                "name": "Depoimento",
                "icon": "testimonial",
                "defaultContent": {
                    "text": "Excelente serviço!",
                    "author": "Cliente Satisfeito",
                    "role": "CEO",
                    "avatar": None,
                    "rating": 5
                },
                "defaultStyle": {
                    "padding": {"top": "24px", "right": "24px", "bottom": "24px", "left": "24px"},
                    "backgroundColor": "#ffffff",
                    "borderRadius": "8px",
                    "boxShadow": "0 2px 8px rgba(0,0,0,0.1)"
                },
                "settings": {
                    "showRating": True,
                    "showAvatar": True
                }
            },
            WidgetType.PRICING: {
                "name": "Tabela de Preços",
                "icon": "pricing",
                "defaultContent": {
                    "plans": [
                        {
                            "name": "Básico",
                            "price": "R$ 29,90",
                            "period": "/mês",
                            "features": ["Feature 1", "Feature 2"],
                            "highlighted": False
                        }
                    ],
                    "currency": "BRL"
                },
                "defaultStyle": {
                    "display": "grid",
                    "gap": "20px"
                },
                "settings": {
                    "showComparison": False,
                    "animatedPrices": True
                }
            },
            WidgetType.FAQ: {
                "name": "FAQ",
                "icon": "faq",
                "defaultContent": {
                    "items": [
                        {
                            "question": "Pergunta frequente?",
                            "answer": "Resposta detalhada."
                        }
                    ],
                    "expandIcon": "chevron"
                },
                "defaultStyle": {
                    "display": "flex",
                    "flexDirection": "column",
                    "gap": "12px"
                },
                "settings": {
                    "accordion": True,
                    "searchable": False
                }
            }
        }
    
    def _load_editor_templates(self) -> Dict[str, Any]:
        """Load editor templates"""
        return {
            "blank": {
                "name": "Página em Branco",
                "pages": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Home",
                        "slug": "home",
                        "widgets": [],
                        "settings": {
                            "container": "full-width",
                            "background": "#ffffff"
                        },
                        "seo": {
                            "title": "",
                            "description": "",
                            "keywords": []
                        }
                    }
                ]
            },
            "landing": {
                "name": "Landing Page",
                "pages": [
                    {
                        "id": str(uuid.uuid4()),
                        "name": "Landing",
                        "slug": "landing",
                        "widgets": self._create_landing_widgets(),
                        "settings": {
                            "container": "boxed",
                            "background": "#ffffff"
                        },
                        "seo": {
                            "title": "Landing Page",
                            "description": "Página de conversão",
                            "keywords": []
                        }
                    }
                ]
            }
        }
    
    def _create_landing_widgets(self) -> List[Widget]:
        """Create landing page widgets"""
        return [
            Widget(
                id=str(uuid.uuid4()),
                type=WidgetType.SECTION,
                content={
                    "name": "Hero Section"
                },
                style=WidgetStyle(
                    padding={"top": "80px", "bottom": "80px"},
                    backgroundColor="#f8f9fa"
                ),
                children=[
                    Widget(
                        id=str(uuid.uuid4()),
                        type=WidgetType.TEXT,
                        content={
                            "text": "Título Principal",
                            "tag": "h1"
                        },
                        style=WidgetStyle(
                            fontSize="48px",
                            fontWeight="700",
                            textColor="#333333",
                            margin={"bottom": "20px"}
                        )
                    ),
                    Widget(
                        id=str(uuid.uuid4()),
                        type=WidgetType.TEXT,
                        content={
                            "text": "Subtítulo explicativo do produto ou serviço",
                            "tag": "p"
                        },
                        style=WidgetStyle(
                            fontSize="20px",
                            textColor="#666666",
                            margin={"bottom": "30px"}
                        )
                    ),
                    Widget(
                        id=str(uuid.uuid4()),
                        type=WidgetType.BUTTON,
                        content={
                            "text": "Começar Agora",
                            "link": "#contact"
                        },
                        style=WidgetStyle(
                            backgroundColor="#28a745",
                            textColor="#ffffff",
                            padding={"top": "15px", "right": "30px", "bottom": "15px", "left": "30px"},
                            fontSize="18px",
                            borderRadius="5px"
                        )
                    )
                ]
            )
        ]
    
    def create_widget(self, widget_type: str, custom_content: Dict[str, Any] = None) -> Widget:
        """Create a new widget"""
        if widget_type not in self.widget_library:
            raise ValueError(f"Unknown widget type: {widget_type}")
        
        template = self.widget_library[widget_type]
        content = template["defaultContent"].copy()
        if custom_content:
            content.update(custom_content)
        
        return Widget(
            id=str(uuid.uuid4()),
            type=widget_type,
            content=content,
            style=WidgetStyle(**template["defaultStyle"]),
            settings=template["settings"]
        )
    
    def update_widget(self, widget: Widget, updates: Dict[str, Any]) -> Widget:
        """Update widget properties"""
        if "content" in updates:
            widget.content.update(updates["content"])
        
        if "style" in updates:
            for key, value in updates["style"].items():
                setattr(widget.style, key, value)
        
        if "settings" in updates:
            widget.settings.update(updates["settings"])
        
        if "children" in updates:
            widget.children = updates["children"]
        
        return widget
    
    def move_widget(self, page: Page, widget_id: str, target_parent_id: str, position: int) -> Page:
        """Move widget to new position"""
        widget = self._find_widget(page.widgets, widget_id)
        if not widget:
            raise ValueError(f"Widget {widget_id} not found")
        
        # Remove from current position
        self._remove_widget(page.widgets, widget_id)
        
        # Add to new position
        if target_parent_id:
            parent = self._find_widget(page.widgets, target_parent_id)
            if parent:
                parent.children.insert(position, widget)
        else:
            page.widgets.insert(position, widget)
        
        return page
    
    def _find_widget(self, widgets: List[Widget], widget_id: str) -> Optional[Widget]:
        """Find widget by ID"""
        for widget in widgets:
            if widget.id == widget_id:
                return widget
            found = self._find_widget(widget.children, widget_id)
            if found:
                return found
        return None
    
    def _remove_widget(self, widgets: List[Widget], widget_id: str) -> bool:
        """Remove widget by ID"""
        for i, widget in enumerate(widgets):
            if widget.id == widget_id:
                widgets.pop(i)
                return True
            if self._remove_widget(widget.children, widget_id):
                return True
        return False
    
    def duplicate_widget(self, widget: Widget) -> Widget:
        """Duplicate a widget"""
        new_widget = widget.copy(deep=True)
        new_widget.id = str(uuid.uuid4())
        
        # Update IDs of children
        def update_child_ids(children: List[Widget]):
            for child in children:
                child.id = str(uuid.uuid4())
                update_child_ids(child.children)
        
        update_child_ids(new_widget.children)
        return new_widget
    
    def export_to_html(self, page: Page) -> str:
        """Export page to HTML"""
        html = []
        html.append('<!DOCTYPE html>')
        html.append('<html lang="pt-BR">')
        html.append('<head>')
        html.append(f'<title>{page.seo.get("title", "")}</title>')
        html.append(f'<meta name="description" content="{page.seo.get("description", "")}">')
        html.append('<meta charset="UTF-8">')
        html.append('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
        
        # Add styles
        html.append('<style>')
        html.append(self._generate_css(page))
        html.append('</style>')
        
        for style_url in page.styles:
            html.append(f'<link rel="stylesheet" href="{style_url}">')
        
        html.append('</head>')
        html.append('<body>')
        
        # Render widgets
        for widget in page.widgets:
            html.append(self._render_widget_html(widget))
        
        # Add scripts
        for script_url in page.scripts:
            html.append(f'<script src="{script_url}"></script>')
        
        html.append('</body>')
        html.append('</html>')
        
        return '\n'.join(html)
    
    def _render_widget_html(self, widget: Widget) -> str:
        """Render widget to HTML"""
        if not widget.visible:
            return ''
        
        html = []
        style = self._style_to_css(widget.style)
        
        if widget.type == WidgetType.TEXT:
            tag = widget.content.get('tag', 'p')
            text = widget.content.get('text', '')
            html.append(f'<{tag} id="{widget.id}" style="{style}">{text}</{tag}>')
        
        elif widget.type == WidgetType.IMAGE:
            src = widget.content.get('src', '')
            alt = widget.content.get('alt', '')
            html.append(f'<img id="{widget.id}" src="{src}" alt="{alt}" style="{style}">')
        
        elif widget.type == WidgetType.BUTTON:
            text = widget.content.get('text', '')
            link = widget.content.get('link', '#')
            target = widget.content.get('target', '_self')
            html.append(f'<a id="{widget.id}" href="{link}" target="{target}" style="{style}">{text}</a>')
        
        elif widget.type in [WidgetType.CONTAINER, WidgetType.SECTION]:
            html.append(f'<div id="{widget.id}" style="{style}">')
            for child in widget.children:
                html.append(self._render_widget_html(child))
            html.append('</div>')
        
        elif widget.type == WidgetType.WHATSAPP:
            phone = widget.content.get('phone', '')
            message = widget.content.get('message', '')
            text = widget.content.get('text', '')
            link = f"https://wa.me/{phone.replace('+', '')}?text={message}"
            html.append(f'<a id="{widget.id}" href="{link}" target="_blank" style="{style}">')
            if widget.content.get('showIcon'):
                html.append('🟢 ')
            html.append(text)
            html.append('</a>')
        
        else:
            # Generic container for other widget types
            html.append(f'<div id="{widget.id}" style="{style}">')
            for child in widget.children:
                html.append(self._render_widget_html(child))
            html.append('</div>')
        
        return ''.join(html)
    
    def _style_to_css(self, style: WidgetStyle) -> str:
        """Convert style object to CSS string"""
        css = []
        
        if style.backgroundColor:
            css.append(f'background-color: {style.backgroundColor}')
        if style.textColor:
            css.append(f'color: {style.textColor}')
        if style.fontSize:
            css.append(f'font-size: {style.fontSize}')
        if style.fontFamily:
            css.append(f'font-family: {style.fontFamily}')
        if style.fontWeight:
            css.append(f'font-weight: {style.fontWeight}')
        
        if style.padding:
            padding = []
            for side in ['top', 'right', 'bottom', 'left']:
                if side in style.padding:
                    padding.append(style.padding[side])
            if padding:
                css.append(f'padding: {" ".join(padding)}')
        
        if style.margin:
            margin = []
            for side in ['top', 'right', 'bottom', 'left']:
                if side in style.margin:
                    margin.append(style.margin[side])
            if margin:
                css.append(f'margin: {" ".join(margin)}')
        
        if style.width:
            css.append(f'width: {style.width}')
        if style.height:
            css.append(f'height: {style.height}')
        if style.display:
            css.append(f'display: {style.display}')
        if style.flexDirection:
            css.append(f'flex-direction: {style.flexDirection}')
        if style.justifyContent:
            css.append(f'justify-content: {style.justifyContent}')
        if style.alignItems:
            css.append(f'align-items: {style.alignItems}')
        if style.gap:
            css.append(f'gap: {style.gap}')
        if style.borderRadius:
            css.append(f'border-radius: {style.borderRadius}')
        if style.boxShadow:
            css.append(f'box-shadow: {style.boxShadow}')
        if style.position:
            css.append(f'position: {style.position}')
        if style.top:
            css.append(f'top: {style.top}')
        if style.left:
            css.append(f'left: {style.left}')
        if style.right:
            css.append(f'right: {style.right}')
        if style.bottom:
            css.append(f'bottom: {style.bottom}')
        if style.zIndex is not None:
            css.append(f'z-index: {style.zIndex}')
        if style.opacity is not None:
            css.append(f'opacity: {style.opacity}')
        if style.transform:
            css.append(f'transform: {style.transform}')
        if style.transition:
            css.append(f'transition: {style.transition}')
        
        return '; '.join(css)
    
    def _generate_css(self, page: Page) -> str:
        """Generate CSS for the page"""
        css = []
        css.append('* { margin: 0; padding: 0; box-sizing: border-box; }')
        css.append('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }')
        css.append('a { text-decoration: none; display: inline-block; }')
        css.append('img { max-width: 100%; height: auto; }')
        
        # Add responsive styles
        css.append('@media (max-width: 768px) {')
        css.append('  body { font-size: 14px; }')
        css.append('}')
        
        return '\n'.join(css)
    
    def export_to_elementor(self, page: Page) -> Dict[str, Any]:
        """Export page to Elementor format"""
        elements = []
        
        for widget in page.widgets:
            elements.append(self._widget_to_elementor(widget))
        
        return {
            "version": "0.4",
            "title": page.name,
            "type": "page",
            "content": elements,
            "page_settings": {
                "title": page.seo.get("title", ""),
                "description": page.seo.get("description", "")
            }
        }
    
    def _widget_to_elementor(self, widget: Widget) -> Dict[str, Any]:
        """Convert widget to Elementor element"""
        element = {
            "id": widget.id,
            "elType": "widget" if widget.type not in [WidgetType.CONTAINER, WidgetType.SECTION] else "section",
            "isInner": False,
            "settings": {},
            "elements": []
        }
        
        if widget.type == WidgetType.TEXT:
            element["widgetType"] = "text-editor"
            element["settings"]["editor"] = widget.content.get("text", "")
        
        elif widget.type == WidgetType.IMAGE:
            element["widgetType"] = "image"
            element["settings"]["image"] = {"url": widget.content.get("src", "")}
        
        elif widget.type == WidgetType.BUTTON:
            element["widgetType"] = "button"
            element["settings"]["text"] = widget.content.get("text", "")
            element["settings"]["link"] = {"url": widget.content.get("link", "#")}
        
        elif widget.type in [WidgetType.CONTAINER, WidgetType.SECTION]:
            element["elType"] = "section"
            element["elements"] = [self._widget_to_elementor(child) for child in widget.children]
        
        # Apply styles
        if widget.style.backgroundColor:
            element["settings"]["background_background"] = "classic"
            element["settings"]["background_color"] = widget.style.backgroundColor
        
        if widget.style.padding:
            element["settings"]["padding"] = {
                "unit": "px",
                "top": widget.style.padding.get("top", "0").replace("px", ""),
                "right": widget.style.padding.get("right", "0").replace("px", ""),
                "bottom": widget.style.padding.get("bottom", "0").replace("px", ""),
                "left": widget.style.padding.get("left", "0").replace("px", "")
            }
        
        return element
    
    def import_from_json(self, json_data: str) -> Page:
        """Import page from JSON"""
        data = json.loads(json_data)
        return Page(**data)
    
    def export_to_json(self, page: Page) -> str:
        """Export page to JSON"""
        return page.json(indent=2)
    
    def validate_page(self, page: Page) -> List[str]:
        """Validate page structure"""
        errors = []
        
        # Check for required SEO fields
        if not page.seo.get("title"):
            errors.append("Título SEO não definido")
        
        if not page.seo.get("description"):
            errors.append("Descrição SEO não definida")
        
        # Check for empty page
        if not page.widgets:
            errors.append("Página não contém widgets")
        
        # Validate widgets
        def validate_widget(widget: Widget, path: str = ""):
            widget_path = f"{path}/{widget.type}[{widget.id}]"
            
            # Check for required content
            if widget.type == WidgetType.IMAGE and not widget.content.get("src"):
                errors.append(f"{widget_path}: Imagem sem fonte definida")
            
            if widget.type == WidgetType.BUTTON and not widget.content.get("link"):
                errors.append(f"{widget_path}: Botão sem link definido")
            
            # Validate children
            for child in widget.children:
                validate_widget(child, widget_path)
        
        for widget in page.widgets:
            validate_widget(widget)
        
        return errors
    
    def apply_theme(self, page: Page, theme: Dict[str, Any]) -> Page:
        """Apply theme to page"""
        # Apply theme colors
        colors = theme.get("colors", {})
        
        def apply_theme_to_widget(widget: Widget):
            # Update colors based on widget type
            if widget.type == WidgetType.TEXT:
                if "text" in colors:
                    widget.style.textColor = colors["text"]
            
            elif widget.type == WidgetType.BUTTON:
                if "primary" in colors:
                    widget.style.backgroundColor = colors["primary"]
                if "buttonText" in colors:
                    widget.style.textColor = colors["buttonText"]
            
            elif widget.type in [WidgetType.CONTAINER, WidgetType.SECTION]:
                if "background" in colors:
                    widget.style.backgroundColor = colors["background"]
            
            # Apply to children
            for child in widget.children:
                apply_theme_to_widget(child)
        
        for widget in page.widgets:
            apply_theme_to_widget(widget)
        
        # Apply theme fonts
        if "fonts" in theme:
            page.settings["fontFamily"] = theme["fonts"].get("body")
            page.settings["headingFontFamily"] = theme["fonts"].get("heading")
        
        return page